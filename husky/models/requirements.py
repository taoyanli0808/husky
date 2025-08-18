import os
import re
import json
import random

from io import BytesIO
from textwrap import dedent
from datetime import datetime
from typing import Dict, Optional

import PyPDF2  # 需要安装：pip install PyPDF2

from openai import OpenAI
from loguru import logger
from husky.repositories.mysql_repository import MysqlRepository  # 更新导入路径

class Requirements:
    def __init__(self, file_stream: BytesIO, filename: str):
        """
        初始化需求解析器
        :param file_stream: 文件字节流
        :param filename: 原始文件名（用于提取信息）
        """
        self.gpt = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com")
        self.file_stream = file_stream
        self.filename = filename
        self.record = {
            "require_id": self._generate_require_id(),
            "require_name": "",
            "description": "",
            "original_text": "",
            "business_domain": "",
            "module": "",
            "quality_score": {
                "completeness": 0,
                "testability": 0,
                "clarity": 0,
                "consistency": 0
            },
            "total_score": 0,
            "issues": []
        }

    def _generate_require_id(self) -> str:
        """生成需求ID（格式：REQ-模块-年月-序号）"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        digit = random.randint(100, 999)
        return f"REQ-{timestamp}-{digit}"  # 实际项目应查询最大序号

    def _extract_module_slug(self) -> str:
        """从文件名提取模块缩写（如：支付->PAY）"""
        name = self.filename.split('.')[0].upper()
        if '登录' in name: return 'AUTH'
        if '支付' in name: return 'PAY'
        return 'GEN'  # 默认通用

    def _parse_pdf(self) -> str:
        """解析PDF内容为文本"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(self.file_stream)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"PDF解析失败: {e}")
            raise ValueError("无效的PDF文档")
        return text.strip()

    def _analyze_quality(self, text: str) -> Dict:
        """评估需求质量（示例逻辑，实际项目需增强）"""
        # 规则1：完整性 = 是否包含"成功"和"失败"场景
        completeness = 3  # 基础分
        if re.search(r"(失败|异常|错误)", text):
            completeness += 1
        if re.search(r"(所有|全部|完整)", text):
            completeness += 1

        # 规则2：可测试性 = 明确输入输出的数量
        testability = min(5, len(re.findall(r"(输入|参数|条件).*?(输出|结果)", text)))

        # 规则3：清晰度 = 段落结构 + 模糊词检测
        clarity = 5 - len(re.findall(r"(可能|大约|若干)", text))

        # 规则4：一致性 = 检测冲突术语（示例）
        consistency = 5
        if len(set(re.findall(r"(用户|客户|会员)", text))) > 1:
            consistency -= 2
            self.record["issues"].append("术语不一致")

        return {
            "completeness": min(5, max(0, completeness)),
            "testability": testability,
            "clarity": clarity,
            "consistency": consistency
        }
    
    def load_prompt_template(self):

        prompt = dedent("""  
            你是一个专业的需求分析师，请从以下需求文档中提取结构化信息：

            **输入要求：**
            1. 原始需求文本（可能包含PDF解析的格式噪音）
            2. 文件名（辅助判断业务域）
            
            **处理规则：**
            0. self.record['original_text']是需求原始文本,self.record['require_name']是需求名;
            1. 你需要将其概述为不超过100字的description；
            2. 你需要识别需求的从属领域，例如支付/用户/风控/营销/商品，对应business_domain；
            3. 你需要识别需求包含哪些模块，例如支付网关/优惠券系统，对应module；
            4. 你需要识别进一步精简领域和模块信息，形成标签，例如：营销/优惠券，对应tags。

            **输出要求（JSON格式）：**
            {
                "description": "营销系统需要支持折扣券能力，用于618期间拉新和提升订单量，...",
                "business_domain": "营销",
                "module": "优惠券",
                "tags": ["营销", "优惠券"] // 技术或业务标签如API/安全/移动端
            }

            **待解析文本：**
            """ + self.record['original_text'] + """

            **文件名：**
            """ + self.record['require_name']
        )
        return prompt
        
    def _parse_context_by_big_model(self) -> 'Requirements':
        prompt = self.load_prompt_template()
        response = self.gpt.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt}
            ],
            # max_tokens='8K',
            temperature=1.0,
            response_format={"type": "json_object"},
            stream=False
        )
        # 这里将测试用例存入数据库
        requirement = json.loads(response.choices[0].message.content)
        logger.info(f'测试用例集：{requirement}')
        self.record['description'] = requirement.get('description')
        self.record['business_domain'] = requirement.get('business_domain')
        self.record['module'] = requirement.get('module')
        self.record['tags'] = requirement.get('tags')

        return self

    def evaluate(self) -> 'Requirements':
        """执行需求解析和质量评估"""
        # 1. 提取原始文本
        self.record["require_name"] = self.filename
        self.record["original_text"] = self._parse_pdf()
        
        self._parse_context_by_big_model()

        # 4. 质量评估
        quality = self._analyze_quality(self.record["original_text"])
        self.record["quality_score"] = quality
        self.record["total_score"] = sum(quality.values()) / len(quality)

        return self

    def save(self) -> bool:
        """使用ON DUPLICATE KEY UPDATE实现原子化操作"""
        try:
            with MysqlRepository() as db:
                data = {
                    "require_id": self.record["require_id"],
                    "require_name": self.record["require_name"],
                    "description": self.record["description"],
                    "original_text": self.record["original_text"],
                    "business_domain": self.record["business_domain"],
                    "module": self.record["module"],
                    "quality_score": json.dumps(self.record["quality_score"]),
                    "tags": json.dumps(self.record.get("tags", ["auto-import"])),
                    "source": self.filename,
                    "is_deleted": False
                }

                with db.connection.cursor() as cursor:
                    # 构造ON DUPLICATE KEY UPDATE语句
                    columns = ', '.join([f'`{k}`' for k in data.keys()])
                    placeholders = ', '.join(['%s'] * len(data))
                    updates = ', '.join([f'`{k}`=VALUES(`{k}`)' for k in data.keys() if k != 'require_id'])
                    
                    sql = f"""
                    INSERT INTO `requirements` ({columns}) 
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {updates}
                    """
                    
                    cursor.execute(sql, tuple(data.values()))
                    db.connection.commit()
                    return True
                    
        except Exception as e:
            logger.error(f"需求存储失败: {e}")
            db.connection.rollback()
            return False

    @classmethod
    def load(cls, require_id: str) -> Optional[Dict]:
        """从数据库加载需求"""
        try:
            with MysqlRepository() as db:
                results = db.search(
                    table="requirements",
                    where={"require_id": require_id}
                )
                return results[0] if results else None
        except Exception as e:
            logger.error(f"需求加载失败: {e}")
            return None

# 确保文件末尾有换行符