import json
from flask import Blueprint, request, jsonify
from loguru import logger

from husky.repositories.mysql_repository import MysqlRepository

# 创建蓝图
task_bp = Blueprint('task', __name__)

@task_bp.route('/search', methods=['GET'])
def task_search():
    # 获取请求参数
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 计算偏移量
    offset = (page - 1) * size
    
    # 构建排序字符串
    order_by = f'{sort} {order.upper()}'
    
    try:
        with MysqlRepository() as db:
            # 查询总数
            with db.connection.cursor() as cursor:
                sql = f"SELECT COUNT(*) as total FROM `tasks`"
                cursor.execute(sql)
                result = cursor.fetchone()
                total = result['total']

            # 分页查询任务
            with db.connection.cursor() as cursor:
                sql = f"SELECT * FROM `tasks` ORDER BY {order_by} LIMIT {size} OFFSET {offset}"
                cursor.execute(sql)
                tasks = cursor.fetchall()
            
            # 处理JSON字段
            processed_tasks = []
            for task in tasks:
                # 转换result字段
                if 'result' in task and task['result']:
                    try:
                        task['result'] = json.loads(task['result'])
                    except json.JSONDecodeError:
                        task['result'] = {}
                
                processed_tasks.append(task)
            
            return jsonify({
                'code': 0,
                'message': 'Success',
                'data': {
                    'total': total,
                    'list': processed_tasks
                }
            })
            
    except Exception as e:
        logger.error(f"Search tasks error: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None
        })

@task_bp.route('/cancel', methods=['POST'])
def task_cancel():
    data = request.get_json()
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({
            'code': 400,
            'message': 'task_id is required',
            'data': None
        })
    
    try:
        with MysqlRepository() as db:
            # 更新任务状态为已终止
            affected_rows = db.update(
                    table='tasks',
                    update_data={
                        'status': 'failed',
                        'message': 'Task cancelled by user',
                        'end_time': db.get_current_time()
                    },
                    where={'task_id': task_id}
                )
            
            if affected_rows > 0:
                return jsonify({
                    'code': 0,
                    'message': 'Task cancelled successfully',
                    'data': None
                })
            else:
                return jsonify({
                    'code': 404,
                    'message': 'Task not found or not in processing status',
                    'data': None
                })
                
    except Exception as e:
        logger.error(f"Cancel task error: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None
        })