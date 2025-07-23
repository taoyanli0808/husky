
import json
import uuid

from io import BytesIO
from threading import Thread
from datetime import datetime

from loguru import logger
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template

from husky.task import Task
from husky.mysql import Mysql
from husky.utils import get_husky_id
from husky.Requirements import Requirements
from husky.testcase import Testcase
from husky.knowledge import Knowledge


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制上传文件100MB

task_manager = Task()  # 创建全局Task实例

@app.route('/api/v1/testcase/analysis', methods=['POST'])
def api_v1_testcase_analysis():
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
    
    # 启动异步处理线程
    thread = Thread(target=task_manager.process_testcase_analysis, args=(task_id, require_id, point_ids))
    thread.start()
    
    return jsonify({
        'code': 0,
        'message': 'Analysis started',
        'data': {
            'task_id': task_id
        }
    })

@app.route('/api/v1/testcase/status', methods=['POST'])
def api_v1_testcase_status():
    task_id = request.args.get('task_id')
    
    if not task_id:
        return jsonify({
            'code': 400,
            'message': 'task_id is required',
            'data': None
        })
    
    task_info = task_manager.task_status.get(task_id)
    
    if not task_info:
        return jsonify({
            'code': 404,
            'message': 'Task not found',
            'data': None
        })
    
    response_data = {
        'task_id': task_id,
        'status': task_info['status'],
        'progress': task_info['progress'],
        'message': task_info.get('message', ''),
        'require_id': task_info.get('require_id', '')
    }
    
    if task_info['status'] == 'completed':
        response_data['result'] = task_info.get('result', None)
    
    return jsonify({
        'code': 0,
        'message': 'Success',
        'data': response_data
    })

@app.route('/api/v1/testcase/search', methods=['POST'])
def api_v1_testcase_search():
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
        with Mysql() as db:
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

# Flask 路由
@app.route('/api/v1/file/upload', methods=['POST'])
def handle_upload():
    # 检查字段名是否为file
    if 'file' not in request.files:
        return jsonify({"error": "请通过'file'字段上传文件"}), 400
    
    file = request.files['file']  # 注意是get不是getlist
     # 验证文件名
    if file.filename == '':
        return jsonify({"error": "空文件名"}), 400
    
    # 验证文件类型
    allowed_extensions = {'pdf', 'md'}
    # filename = secure_filename(file.filename)
    filename = file.filename
    if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "仅支持PDF/Markdown格式"}), 400

    try:
        # 第一步解析文档，并存储需求到require表格。
        file_stream = BytesIO(file.read())
        require = Requirements(file_stream, filename)
        require.evaluate().save()

        # 第二部解析文档，并存储为llama_index本地知识。
        result = Knowledge().add_files(filename, file.mimetype)
        # 构建响应数据（适配新表结构）
        response_data = {
            "status": "success",
            "data": {
                "require_id": require.record["require_id"],
                "require_name": require.record["require_name"],
                "description": require.record["description"],
                "business_domain": require.record["business_domain"],
                "module": require.record["module"],
                "quality_score": require.record["quality_score"],
                "total_score": require.record["total_score"],
                "tags": require.record.get("tags", []),
                "source": filename,
                "issues": require.record["issues"],
                "added_nodes": result['added_nodes']
            },
            "metadata": {
                "file_type": file.mimetype,
                "file_size": len(file_stream.getvalue())
            },
            "added_nodes": result['added_nodes']
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/require/search', methods=['POST'])
def api_v1_require_search():
    with Mysql() as db:
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

@app.route('/api/v1/require/update', methods=['POST'])
def api_v1_require_update():
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
    
    with Mysql() as db:
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

# 这个接口用于查询上传的需求文档，返回reqiure表格字段
@app.route('/api/v1/require/delete', methods=['POST'])
def api_v1_require_delete():
    data = request.get_json()
    if "require_id" not in data:
        return jsonify({
            'code': 400,
            'message': 'require parameter `require_id`',
            'data': data
        })
    
    require_id = data.get('require_id')
    with Mysql() as db:
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


@app.route('/api/v1/point/analysis', methods=['POST'])
def api_v1_point_analysis():
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
    
    # 启动异步处理线程
    thread = Thread(target=task_manager.process_point_analysis, args=(task_id, require_id))
    thread.start()
    
    return jsonify({
        'code': 0,
        'message': 'Analysis started',
        'data': {
            'task_id': task_id
        }
    })


@app.route('/api/v1/point/status', methods=['GET'])
def api_v1_point_status():
    task_id = request.args.get('task_id')
    
    if not task_id:
        return jsonify({
            'code': 400,
            'message': 'task_id is required',
            'data': None
        })
    
    task_info = task_manager.task_status.get(task_id)
    
    if not task_info:
        return jsonify({
            'code': 404,
            'message': 'Task not found',
            'data': None
        })
    
    response_data = {
        'task_id': task_id,
        'status': task_info['status'],
        'progress': task_info['progress'],
        'message': task_info.get('message', ''),
        'require_id': task_info.get('require_id', '')
    }
    
    if task_info['status'] == 'completed':
        response_data['result'] = task_info.get('result', None)
    
    return jsonify({
        'code': 0,
        'message': 'Success',
        'data': response_data
    })
    
@app.route('/api/v1/point/delete', methods=['POST'])
def api_v1_point_delete():
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
        with Mysql() as db:
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

@app.route('/api/v1/point/update', methods=['POST'])
def api_v1_point_update():
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
        with Mysql() as db:
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
    
@app.route('/api/v1/point/search', methods=['POST'])
def api_v1_points_search():
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
        with Mysql() as db:
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


@app.route('/search', methods=['POST'])
def handle_search():
    question = request.get_json()
    if 'q' not in question or not question['q']:
        return jsonify({"error": "缺少查询参数 q"}), 400
    
    top_k = int(request.args.get('top_k', 5))
    results = Knowledge().query(question['q'], top_k)
    logger.info(f"知识库查询结果：{results}")
    return jsonify({"results": results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
