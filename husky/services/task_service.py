import os
import json
import uuid

from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from openai import OpenAI

from husky.repositories.mysql_repository import MysqlRepository
from husky.utils import get_husky_id

class TaskService():
    
    def __init__(self):
        self.gpt = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.deepseek.com")
        self.task_status = {}

    def process_point_analysis(self, task_id: str, require_id: str) -> None:
        """协调处理流程"""
        # 初始化任务状态
        self.update_task_status(task_id, status='processing', progress=10, message="开始需求分块处理...")
            
        # 第一步：需求分块处理
        self.chunk_requirements(task_id, require_id)
        self.update_task_status(task_id, status='processing', progress=30, message="需求分块完成，开始提取功能点...")
            
        # 第二步：模块功能点提取
        self.extract_function_points(task_id)
        self.update_task_status(task_id, status='processing', progress=90, message="功能点提取完成，正在保存结果...")
            
        # 最终结果处理
        self.finalize_point_task(task_id, require_id)
        self.update_task_status(
            task_id,
            status='completed',
            progress=100,
            message="任务完成",
            result=json.dumps({
                'points_count': len(self.get_task_points(task_id)),
                'require_id': require_id
            })
        )

    def chunk_requirements(self, task_id: str, require_id: str):
        """第一步：需求分块处理"""
        try:
            with MysqlRepository() as db:
                requirement = db.search('requirements', columns=['original_text'], where={'require_id': require_id})
            logger.debug(f"需求拆分模块：{requirement}")
            original_text = requirement[0]['original_text'] if requirement else ""
            prompt = """
                目标：将大型需求文档分解为逻辑连贯的独立模块
                你是一个资深产品需求分析师，请将以下产品需求文档分解为逻辑独立的分析模块：

                **输入要求**：
                1. 原始需求文档全文（可能包含PRD、用户故事、技术描述等混合内容）
                2. 文档类型（如功能需求/性能需求/安全需求等）

                **处理规则**：
                1. 按业务领域和功能耦合度划分模块（如用户模块、支付模块、消息中心等）
                2. 每个模块应包含完整的功能闭环
                3. 截取文档原文作为chunks结果，不能对原文进行修改

                **输出格式**：
                1. 必须严格按以下JSON格式输出，不能随意增加或减少字段
                ```json
                {
                    "chunks": [
                        {
                            "module": "用户注册登录",
                            "business_domain": "用户体系",
                            "chunks": "包含手机号注册、第三方登录、密码找回等功能",
                        },
                        {...}
                    ]
                }
                待分析文档： """ + original_text

            response = self.gpt.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=1.0,
                response_format={"type": "json_object"},
                stream=False
            )

            # 这里将测试用例存入数据库
            chunks = json.loads(response.choices[0].message.content)
            logger.debug(f'需求模块切分结果：{chunks}')
            self.task_status[task_id] = {'chunks': chunks['chunks']}
            return self
        except Exception as error:
            logger.error(f"需求分块处理失败: {str(error)}")
            return 0

    def extract_function_points(self, task_id: str):
        """第二步：模块功能点提取"""
        try:
            for chunk in self.task_status[task_id]['chunks']:
                prompt = """
                    **目标**：对每个模块提取详细功能点
                    作为高级产品经理，请从以下需求模块中提取原子级功能点：
                    
                    **提取要求**：
                    1. 识别最小可交付功能单元（如"支持微信登录"而非"用户认证系统"）
                    2. 按CRUD分类（功能、性能、兼容性、交互）
                    3. 标注技术复杂度（简单/中等/复杂）
                    4. 识别前置条件
                    
                    **输出格式**：
                    1. 必须严格按以下JSON格式输出，不能随意增加或减少字段
                    2. 禁止自行添加complexity、technical_complexity这类字段，严格遵守格式输出第一条准则！
                    ```json
                    {
                        "points": [
                            {
                                "function_name": "手机号验证码注册",
                                "test_type": "兼容性",
                                "description": "用户通过手机号+短信验证码完成注册",
                                "preconditions": ["短信服务可用"]
                            },
                            {...}
                        ]
                    }

                    待分析内容：
                    1. 模块名称：""" + chunk['module'] + """
                    2. 业务领域：""" + chunk['business_domain'] + """
                    3. 原始内容：""" + chunk['chunks']

                response = self.gpt.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": prompt}
                    ],
                    temperature=1.0,
                    response_format={"type": "json_object"},
                    stream=False
                )

                points = json.loads(response.choices[0].message.content)
                logger.debug(f'需求功能点切分结果：{points}')
                chunk.setdefault("points", points['points'])
            return self
        except Exception as error:
            logger.error(f"功能点提取失败: {str(error)}")
            return 0
    
    def process_testcase_analysis(self, task_id: str, require_id: str, point_ids: list) -> None:
        # 初始化任务状态
        self.init_task('testcase_analysis', task_id, require_id)
        self.task_status[task_id]['require_id'] = require_id  # 存储 require_id
            
        # 第一步：获取需求和测试点
        self.update_task_status(task_id, 'processing', 20, "开始需求分块处理...")
        self.search_requirement_and_points(task_id, require_id, point_ids)
            
        # 第二步：使用需求和测试点生成测试用例
        self.update_task_status(task_id, 'processing', 90, "提取模块功能点...")
        self.generate_testcases(task_id)
            
        # 最终结果处理
        self.finalize_testcase_task(task_id, require_id)
        self.update_task_status(task_id, 'completed', 100, "完成需求分析...")
        
    def search_requirement_and_points(self, task_id: str, require_id: str, point_ids: list):
        # 查询原始需求内容
        with MysqlRepository() as db:
            requirements = db.search('requirements', columns=['require_name', 'original_text'], where={'require_id': require_id})
            if requirements:
                self.task_status[task_id] = {'requirement': requirements[0]['original_text']}
            logger.debug(f"需求内容是：{self.task_status[task_id]['requirement']}")
        
        # 查询所有测试点
        self.task_status[task_id]['points'] = []
        for point_id in point_ids:
            with MysqlRepository() as db:
                point = db.search('points', columns=['function_name', 'description', 'business_domain', 'module', 'chunks', 'preconditions'], where={'point_id': point_id})
                self.task_status[task_id]['points'].append(point[0])
                logger.debug(f"功能点内容是：{point[0]}")
    
    def generate_testcases(self, task_id: str):
        try:
            self.task_status[task_id]['testcases'] = []
            for point in self.task_status[task_id]['points']:
                prompt = """
            你是一位资深的测试工程师, 负责将产品需求转化为手工测试用例. 请严格遵循以下规则:
            # 角色与目标
            - 角色: 功能测试专家, 擅长用户场景分析
            - 输入: 自然语言描述的产品需求
            - 输出: 可直接执行的手工测试用例集
            - 结果: 尽可能多的生成测试用例, 每次生成不少于3条测试用例

                    # 输入示例
                    '''
                    产品需求：
                    用户登录功能
                    1. 支持手机号/邮箱+密码登录
                    2. 密码输入错误3次后锁定账户30分钟
                    3. 登录成功跳转至个人主页
                    '''

            # 生成规则
            1. 场景覆盖要求:
                1.1 正常流程(60%): 完整的主流程验证
                1.2 异常流程(20%): 错误操作/非法输入
                1.3 边界情况(20%): 极限值/特殊条件
            2. 步骤编写规范:
                2.1 步骤需明确操作主体(如"测试员输入...")
                2.2 包含验证点(如"检查页面显示...")
                2.3 使用祈使句("点击登录按钮")
            3. 输出示例:必须严格按以下JSON格式输出, 不能随意增加或减少字段
            ```json
                    {
                        "testcases": [
                            {
                                "case_name": "使用正确手机号密码登录",
                                "preconditions": ["已注册用户，账号未锁定"],
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
                    
            # 擅长技能
            1. 等价类划分法: 将输入域分为有效/无效等价类, 通过选取典型值覆盖所有类别。例如密码长度验证时, 划分8位有效类、7位无效类等。
            2. 边界值分析法: 针对输入边界及相邻值设计用例，如数值范围10-100时测试9、10、99、100等边界值。
            3. 正交实验法: 使用正交表覆盖多因素组合，例如同时测试浏览器类型(Chrome/Firefox)与操作系统(Windows/macOS)组合。
            4. 因果图法: 通过输入条件与输出结果的因果逻辑建立测试矩阵，适合复杂条件组合场景。
                    等等

                    # 特殊约束
                    1. 禁止使用代码术语（如"发送POST请求"）
                    2. 每个用例步骤数<=6步
                    3. 预期结果必须可观察验证
                    4. 测试类型最多选2个分类

                    # 需求内容如下：
                """ + self.task_status[task_id]['requirement'] + """
                    本次要生成的用范围是：
                1. 功能名称：""" + point['function_name'] + """
                2. 功能描述：""" + point['description'] + """
                3. 业务领域：""" + point['business_domain'] + """
                4. 功能模块：""" + point['module'] + """
                5. 需求片段：""" + point['chunks'] + """
                6. 前置条件：""" + point['preconditions'] + """
                请理解需求内容，并为需求片段生成完备的测试用例。"""

                response = self.gpt.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": prompt}
                    ],
                    temperature=1.0,
                    response_format={"type": "json_object"},
                    stream=False
                )

                # 这里将测试用例存入数据库
                testcases = json.loads(response.choices[0].message.content)
                logger.debug(f'生成测试用例结果：{testcases}')
                self.task_status[task_id]['testcases'].extend(testcases['testcases'])
            return self
        except Exception as error:
            logger.error(f"测试用例生成失败: {str(error)}")
            return 0

    def init_task(self, task_type: str, task_id: str, require_id: str = None) -> Dict:
        """初始化任务记录"""
        # 初始化内存中的任务状态
        self.task_status[task_id] = {}
        
        with MysqlRepository() as db:
            db.create('tasks', {
                'task_id': task_id,
                'require_id': require_id,
                'task_type': task_type,
                'status': 'pending',
                'progress': 0,
                'message': '等待开始',
                'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        return self.get_task_status(task_id)

    def update_task_status(self, task_id: str, **kwargs) -> Dict:
        """通用状态更新方法"""
        update_data = {'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        # 特殊字段处理
        if 'status' in kwargs and kwargs['status'] == 'completed':
            update_data['end_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        update_data.update(kwargs)
        
        with MysqlRepository() as db:
            db.update(
                table='tasks',
                update_data=update_data,
                where={'task_id': task_id}
            )
        return self.get_task_status(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取完整任务状态"""
        with MysqlRepository() as db:
            tasks = db.search(
                table='tasks',
                where={'task_id': task_id}
            )
            if not tasks:
                return None
            
            task = tasks[0]
            # 处理JSON字段
            if task.get('result'):
                try:
                    task['result'] = json.loads(task['result'])
                except json.JSONDecodeError:
                    task['result'] = None
            return task

    def finalize_point_task(self, task_id: str, require_id: str) -> None:
        """完成处理任务"""
        logger.info(f"最终数据是：{self.task_status[task_id]}")
        
        # 1. 准备扁平化数据
        flatten = []
        for chunk in self.task_status[task_id]['chunks']:   
            # 遍历每个point
            for point in chunk['points']:
                raw = {
                    'task_id': task_id,
                    'require_id': require_id,
                    'module': chunk['module'],
                    'chunks': chunk['chunks'],
                    'business_domain': chunk['business_domain'],
                    **point,
                }
                point_id = get_husky_id('POINT')
                flatten.append({'point_id': point_id, **raw})
        
        # 2. 批量更新插入
        with MysqlRepository() as db:
            for point_data in flatten:
                # 构建ON DUPLICATE KEY UPDATE语句
                with db.connection.cursor() as cursor:
                    # 转义列名
                    columns = ', '.join([f'`{k}`' for k in point_data.keys()])
                    placeholders = ', '.join(['%s'] * len(point_data))
                    
                    # 构建UPDATE部分
                    update_set = ', '.join([f'`{k}` = VALUES(`{k}`)' for k in point_data.keys()])
                    
                    sql = f"""
                    INSERT INTO `points` ({columns})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {update_set}
                    """
                    
                    # 准备值（处理JSON字段）
                    values = []
                    for v in point_data.values():
                        if isinstance(v, (list, dict)):
                            values.append(json.dumps(v, ensure_ascii=False))
                        else:
                            values.append(v)
                    
                    logger.debug(f"执行SQL: {sql}")
                    logger.debug(f"参数: {values}")
                    
                    cursor.execute(sql, tuple(values))
            
            db.connection.commit()
        
        logger.info(f"任务 {task_id} 处理完成，共处理 {len(flatten)} 条记录")
    
    
    def finalize_testcase_task(self, task_id: str, require_id: str) -> None:
        """完成处理任务"""
        logger.info(f"最终用例数据是：{self.task_status[task_id]}")
        
        for testcase in self.task_status[task_id]['testcases']:
            case_id = get_husky_id('CASE')
            testcase.setdefault('case_id', case_id)
            testcase.setdefault('task_id', task_id)
            testcase.setdefault('require_id', require_id)
        
            with MysqlRepository() as db:
                # 构建ON DUPLICATE KEY UPDATE语句
                with db.connection.cursor() as cursor:
                    # 转义列名
                    columns = ', '.join([f'`{k}`' for k in testcase.keys()])
                    placeholders = ', '.join(['%s'] * len(testcase))
                    
                    # 构建UPDATE部分
                    update_set = ', '.join([f'`{k}` = VALUES(`{k}`)' for k in testcase.keys()])
                    
                    sql = f"""
                    INSERT INTO `testcases` ({columns})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {update_set}
                    """
                    
                    # 准备值（处理JSON字段）
                    values = []
                    for v in testcase.values():
                        if isinstance(v, (list, dict)):
                            values.append(json.dumps(v, ensure_ascii=False))
                        else:
                            values.append(v)
                    
                    logger.debug(f"执行SQL: {sql}")
                    logger.debug(f"参数: {values}")
                    
                    cursor.execute(sql, tuple(values))
                    db.connection.commit()
        
        logger.info(f"任务 {task_id} 处理完成，共处理 {len(self.task_status[task_id]['testcases'])} 条记录")


    def get_task_points(self, task_id: str) -> List[Dict]:
        """获取任务生成的所有功能点"""
        with MysqlRepository() as db:
            return db.search(
                table='points',
                where={'task_id': task_id}
            )

    def get_task_testcases(self, task_id: str) -> List[Dict]:
        """获取任务生成的所有测试用例"""
        with MysqlRepository() as db:
            testcases = db.search(
                table='testcases',
                where={'task_id': task_id}
            )
            # 处理JSON字段
            for tc in testcases:
                for field in ['preconditions', 'test_steps', 'expected_result', 'test_type']:
                    if tc.get(field):
                        try:
                            tc[field] = json.loads(tc[field])
                        except json.JSONDecodeError:
                            tc[field] = []
            return testcases
    

if __name__ == '__main__':
    task = TaskService()
    task.process_testcase_analysis('TASK_001', "REQ-20250721160532-666", ['POINT_017edce9c287e69ebcee8da14f07b61a', 'POINT_5486422e6490690a9989b1c4612e0123'])