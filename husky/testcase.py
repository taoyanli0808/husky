# Please install OpenAI SDK first: `pip3 install openai`

import json

from loguru import logger
from openai import OpenAI
from PyPDF2 import PdfReader

from husky.mysql import Mysql

from husky.config import API_KEY


class Testcase:

    def __init__(self):
        self.gpt = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

    def load_prompt_template(self):
        prompt = """  
            你是一位资深的测试工程师，负责将产品需求转化为手工测试用例。请严格遵循以下规则：

            # 角色与目标  
            - 角色：功能测试专家，擅长用户场景分析  
            - 输入：自然语言描述的产品需求  
            - 输出：可直接执行的手工测试用例集  

            # 输入示例  
            '''
            产品需求：  
            用户登录功能  
            1. 支持手机号/邮箱+密码登录  
            2. 密码输入错误3次后锁定账户30分钟  
            3. 登录成功跳转至个人主页  
            '''

            # 生成规则  
            1. **用例结构**：  
            ```json  
            {
                "test_cases": [
                    {
                        "case_name": "测试场景描述",
                        "precondition": ["前置条件"],
                        "test_steps": [
                            "步骤1：...",
                            "步骤2：..."
                        ],
                        "expected_result": ["预期结果"],
                        "priority": "P0-P3",
                        "test_type": ["功能", "兼容性", "边界值"] 
                    }
                ]
            }
            2. 场景覆盖要求：
            正常流程（40%）：完整的主流程验证
            异常流程（30%）：错误操作/非法输入
            边界情况（30%）：极限值/特殊条件
            3. 步骤编写规范：
            步骤需明确操作主体（如"测试员输入..."）
            包含验证点（如"检查页面显示..."）
            使用祈使句（"点击登录按钮"）
            4. 输出示例
            {
                "test_cases": [
                    {
                        "case_name": "使用正确手机号密码登录",
                        "precondition": ["已注册用户，账号未锁定"],
                        "test_steps": [
                            "步骤1：在登录页输入有效的手机号",
                            "步骤2：输入正确的密码",
                            "步骤3：点击登录按钮",
                            "步骤4：检查页面跳转情况"
                        ],
                        "expected_result": ["1. 跳转至个人主页", "2. 显示用户昵称"],
                        "priority": "P0",
                        "test_type": ["功能"]
                    },
                    {
                        "case_name": "连续3次输入错误密码",
                        "precondition": ["新会话未登录状态"],
                        "test_steps": [
                            "步骤1：输入有效手机号",
                            "步骤2：输入错误密码（第1次）",
                            "步骤3：点击登录后重新输入错误密码（第2次）",
                            "步骤4：再次输入错误密码（第3次）"
                        ],
                        "expected_result": [
                            "1. 显示账户锁定提示",
                            "2. 30分钟内无法登录"
                        ],
                        "priority": "P1",
                        "test_type": ["异常", "边界值"]
                    }
                ]
            }
            
            # 特殊约束
            1. 禁止使用代码术语（如"发送POST请求"）
            2. 每个用例步骤数≤6步
            3. 预期结果必须可观察验证
            4. 测试类型最多选2个分类
            请根据以下需求生成测试用例：
        """
        return prompt

    def generate_testcase(self, require):
        try:
            response = self.gpt.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.load_prompt_template()},
                    {"role": "user", "content": require['content']},
                ],
                # max_tokens='8K',
                temperature=1.0,
                response_format={"type": "json_object"},
                stream=False
            )

            # 这里将本次生成用例的消耗存入数据看
            costs = dict(response.usage)
            logger.warning(f"本次用例生成的成本是：{costs}")
            costs.pop('completion_tokens_details')
            costs.pop('prompt_tokens_details')
            costs.setdefault('model', 'deepseek-r1')
            _mysql = Mysql()
            _mysql.create('costs', costs)

            # 这里将测试用例存入数据库
            testsuite = json.loads(response.choices[0].message.content)
            logger.info(f'测试用例集：{testsuite}')
            testcases = testsuite.get('test_cases')
            if testcases is None:
                logger.error("返回测试用例集为空")
            _mysql = Mysql()
            for testcase in testcases:
                testcase['require_id'] = require['require_id']
                testcase['require_name'] = require['require_name']
                # 确保数据格式是list，大模型可能返回的数据类型是str
                testcase['precondition'] = [testcase['precondition']] if type(testcase['precondition']) == str else testcase['precondition']
                testcase['test_steps'] = [testcase['test_steps']] if type(testcase['test_steps']) == str else testcase['test_steps']
                testcase['expected_result'] = [testcase['expected_result']] if type(testcase['expected_result']) == str else testcase['expected_result']
                testcase['test_type'] = [testcase['test_type']] if type(testcase['test_type']) == str else testcase['test_type']
                # 添加默认值
                testcase.setdefault('create', False)
                testcase.setdefault('modify', False)
                testcase.setdefault('accept', False)
                testcase.setdefault('review', False)
                testcase.setdefault('verify', False)
                # 这里将测试用例写入数据库
                _mysql.create('testcase', testcase)
            return True
        except json.JSONDecodeError:
            logger.error("JSON格式解析失败")
            return False
