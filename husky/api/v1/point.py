import json
from flask import Blueprint, request, jsonify
from loguru import logger

from husky.services.task_service import TaskService
from husky.repositories.mysql_repository import MysqlRepository
from husky.utils import get_husky_id

# 创建蓝图
point_bp = Blueprint('point', __name__)

@point_bp.route('/analysis', methods=['POST'])
def point_analysis():
    data = request.get_json()
    require_id = data.get('require_id')
    
    if not require_id:
        return jsonify({
            'code': 400,
            'message': 'require_id is required',
            'data': None
        })
    
    # 生成唯一任务ID
    task_id = get_husky_id('TASK')
    # 初始化任务记录
    task_service = TaskService()
    task = task_service.init_task('point_analysis', task_id, require_id)
    if not task:
        return jsonify({
            'code': 500,
            'message': 'Failed to create task',
            'data': None
        })
    
    # 启动异步处理线程
    from threading import Thread
    thread = Thread(target=task_service.process_point_analysis, args=(task_id, require_id))
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

@point_bp.route('/delete', methods=['POST'])
def point_delete():
    data = request.get_json()
    point_id = data.get('point_id')  # 注意：POST请求参数应从请求体中获取
    
    if not point_id:
        return jsonify({
            'code': 400,
            'message': 'point_id is required',
            'data': None
        })
    
    try:
        # 使用Mysql类进行删除操作
        with MysqlRepository() as db:
            # 执行删除操作，假设表名为'test_points'
            affected_rows = db.delete(
                table='points',
                where={'point_id': point_id}
            )
            
            if affected_rows > 0:
                return jsonify({
                    'code': 0,
                    'message': '删除成功',
                    'data': {'deleted_rows': affected_rows}
                })
            else:
                return jsonify({
                    'code': 404,
                    'message': '未找到指定的测试点',
                    'data': None
                })
                
    except Exception as e:
        logger.error(f"删除测试点失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}',
            'data': None
        })

@point_bp.route('/update', methods=['POST'])
def point_update():
    data = request.get_json()
    
    # 必填字段验证
    required_fields = ['point_id', 'module', 'function_name', 'description', 'test_type', 'business_domain', 'chunks', 'preconditions']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({
                'code': 400,
                'message': f'{field} is required',
                'data': None
            })
    
    try:
        with MysqlRepository() as db:
            # 构建更新数据
            update_data = {
                'module': data['module'],
                'function_name': data['function_name'],
                'description': data['description'],
                'test_type': data['test_type'],
                'business_domain': data['business_domain'],
                'chunks': data['chunks'],
                'preconditions': data['preconditions']
            }
            
            # 如果有前置条件则处理
            if 'preconditions' in data:
                update_data['preconditions'] = json.dumps(data['preconditions'], ensure_ascii=False)
            
            # 执行更新操作
            affected_rows = db.update(
                table='points',
                update_data=update_data,
                where={'point_id': data['point_id']}
            )
            
            if affected_rows > 0:
                return jsonify({
                    'code': 0,
                    'message': '更新成功',
                    'data': {'updated_rows': affected_rows}
                })
            else:
                return jsonify({
                    'code': 404,
                    'message': '未找到指定的测试点或数据未变更',
                    'data': None
                })
                
    except Exception as e:
        logger.error(f"更新测试点失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}',
            'data': None
        })

@point_bp.route('/search', methods=['POST'])
def points_search():
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
            points = db.search(
                table='points',
                where={'task_id': task_id}
            )
            
            # 处理JSON格式的字段
            processed_points = []
            for point in points:
                # 转换preconditions字段
                if 'preconditions' in point and isinstance(point['preconditions'], str):
                    try:
                        point['preconditions'] = json.loads(point['preconditions'])
                    except json.JSONDecodeError:
                        point['preconditions'] = []
                
                processed_points.append(point)
            
            return jsonify({
                'code': 0,
                'message': 'Success',
                'data': {
                    'total': len(processed_points),
                    'list': processed_points
                }
            })
            
    except Exception as e:
        logger.error(f"Search points error: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'Internal server error: {str(e)}',
            'data': None
        })