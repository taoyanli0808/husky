import json
from flask import Blueprint, request, jsonify
from loguru import logger

from husky.services.task_service import TaskService
from husky.repositories.mysql_repository import MysqlRepository
from husky.utils import get_husky_id

# 创建蓝图
testcase_bp = Blueprint('testcase', __name__)

@testcase_bp.route('/analysis', methods=['POST'])
def testcase_analysis():
    data = request.get_json()
    
    require_id = data.get('require_id')
    if not require_id:
        return jsonify({
            'code': 400,
            'message': 'require_id is required',
            'data': None
        })
    
    point_ids = data.get('point_ids')
    if not point_ids:
        return jsonify({
            'code': 400,
            'message': 'point_ids is required',
            'data': None
        })
    
    # 生成唯一任务ID
    task_id = get_husky_id('TASK')
    # 初始化任务记录
    task_service = TaskService()
    task = task_service.init_task('testcase_analysis', task_id, require_id)
    if not task:
        return jsonify({
            'code': 500,
            'message': 'Failed to create task',
            'data': None
        })
    
    # 启动异步处理线程
    from threading import Thread
    thread = Thread(target=task_service.process_testcase_analysis, args=(task_id, require_id, point_ids))
    thread.start()
    
    return jsonify({
        'code': 0,
        'message': 'Analysis started',
        'data': {
            'task_id': task_id,
            'status': task['status'],
            'progress': task['progress']
        }
    })

@testcase_bp.route('/search', methods=['POST'])
def testcase_search():
    # 获取请求参数
    data = request.get_json()
    task_id = data.get('task_id')  # 注意：POST请求参数应从请求体中获取
    
    if not task_id:
        return jsonify({
            'code': 400,
            'message': 'task_id is required',
            'data': None
        })
    
    try:
        # 使用Mysql类查询数据
        with MysqlRepository() as db:
            # 查询points表中所有task_id匹配的记录
            testcases = db.search(
                table='testcases',
                where={'task_id': task_id}
            )
            
            # 处理JSON格式的字段
            processed_testcases = []
            for testcase in testcases:
                # 转换preconditions字段
                if 'preconditions' in testcase and isinstance(testcase['preconditions'], str):
                    try:
                        testcase['preconditions'] = json.loads(testcase['preconditions'])
                    except json.JSONDecodeError:
                        testcase['preconditions'] = []
                
                processed_testcases.append(testcase)
            
            return jsonify({
                'code': 0,
                'message': 'Success',
                'data': {
                    'total': len(processed_testcases),
                    'list': processed_testcases
                }
            })
            
    except Exception as e:
        logger.error(f"Search points error: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None
        })