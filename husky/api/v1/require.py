import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from loguru import logger

from husky.repositories.mysql_repository import MysqlRepository
from husky.models.requirements import Requirements
# 已移除未使用的Knowledge导入
from io import BytesIO

# 创建蓝图
require_bp = Blueprint('require', __name__)

@require_bp.route('/search', methods=['POST'])
def require_search():
    with MysqlRepository() as db:
        requirements = db.search('requirements')
        logger.info(f"require: {requirements}")
        
        # 处理返回数据，将字符串转换为对象
        processed_requirements = []
        for req in requirements:
            processed_req = dict(req)  # 创建字典副本
            
            # 处理 tags 字段
            if 'tags' in processed_req and processed_req['tags']:
                try:
                    processed_req['tags'] = json.loads(processed_req['tags'])
                except json.JSONDecodeError:
                    # 如果解析失败，设置为空数组
                    processed_req['tags'] = []
            
            # 处理 quality_score 字段
            if 'quality_score' in processed_req and processed_req['quality_score']:
                try:
                    processed_req['quality_score'] = json.loads(processed_req['quality_score'])
                except json.JSONDecodeError:
                    # 如果解析失败，设置为默认评分对象
                    processed_req['quality_score'] = {
                        "clarity": 0,
                        "consistency": 0,
                        "testability": 0,
                        "completeness": 0
                    }
            
            processed_requirements.append(processed_req)
        
        return jsonify({
            'code': 0,
            'message': 'ok',
            'data': processed_requirements
        })

@require_bp.route('/update', methods=['POST'])
def require_update():
    data = request.get_json()
    
    # 检查必要字段
    required_fields = ['require_id', 'require_name', 'description', 'quality_score']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'code': 400,
                'message': f'缺少必要参数: {field}',
                'data': data
            })
    
    # 处理 quality_score 转换为字符串
    if isinstance(data['quality_score'], dict):
        data['quality_score'] = json.dumps(data['quality_score'], ensure_ascii=False)
    
    # 准备更新数据
    update_data = {
        'require_name': data['require_name'],
        'description': data['description'],
        'quality_score': data['quality_score'],
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with MysqlRepository() as db:
        try:
            # 执行更新
            update_count = db.update(
                table='requirements',  # 注意表名要与数据库一致
                update_data=update_data,
                where={'require_id': data['require_id']}
            )
            
            if update_count > 0:
                # 查询更新后的数据返回给前端
                updated_require = db.search(
                    'requirements',
                    where={'require_id': data['require_id']}
                )
                
                if updated_require:
                    # 处理返回数据格式
                    processed_require = dict(updated_require[0])
                    if 'tags' in processed_require and processed_require['tags']:
                        try:
                            processed_require['tags'] = json.loads(processed_require['tags'])
                        except json.JSONDecodeError:
                            processed_require['tags'] = []
                    
                    if 'quality_score' in processed_require and processed_require['quality_score']:
                        try:
                            processed_require['quality_score'] = json.loads(processed_require['quality_score'])
                        except json.JSONDecodeError:
                            processed_require['quality_score'] = {
                                "clarity": 0,
                                "consistency": 0,
                                "testability": 0,
                                "completeness": 0
                            }
                    
                    return jsonify({
                        'code': 0,
                        'message': '需求更新成功',
                        'data': processed_require
                    })
            
            return jsonify({
                'code': 404,
                'message': '未找到对应需求或更新失败',
                'data': data
            })
            
        except Exception as e:
            logger.error(f"更新需求失败: {str(e)}")
            return jsonify({
                'code': 500,
                'message': f'更新需求失败: {str(e)}',
                'data': data
            })

@require_bp.route('/delete', methods=['POST'])
def require_delete():
    data = request.get_json()
    if "require_id" not in data:
        return jsonify({
            'code': 400,
            'message': 'require parameter `require_id`',
            'data': data
        })
    
    require_id = data.get('require_id')
    with MysqlRepository() as db:
        result = db.delete('requirements', {'require_id': require_id})
        if result:
            return jsonify({
                'code': 0,
                'message': 'ok',
                'data': result
            })
        else:
            return jsonify({
                'code': 400,
                'message': 'not ok',
                'data': data
            })