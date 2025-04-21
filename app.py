
from io import BytesIO

from loguru import logger
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template

from husky.mysql import Mysql
from husky.require import Require
from husky.testcase import Testcase
from husky.knowledge import KnowledgeBaseManager


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制上传文件100MB


# 这个接口用于插叙生成的测试用例，返回testcase表数据
@app.route('/api/v1/testcase/create', methods=['POST'])
def api_v1_testcase_create():
    data = request.get_json()
    if "require_id" not in data:
        return jsonify({
            'code': 400,
            'message': 'require parameter `require_id`',
            'data': data
        })
    
    require_id = data.get('require_id')
    with Mysql() as db:
        requires = db.search('require', columns=['require_id', 'require_name', 'content'], where={'require_id': require_id})
        require = requires[0] if requires else []
        if not require or not require['content']:
            return jsonify({
                'code': 0,
                'message': 'require error',
                'data': require
            })
    
        testcase = Testcase()
        success = testcase.generate_testcase(require)
        if success:
            return jsonify({
                'code': 0,
                'message': 'generate testcase success',
                'data': require
            })
        else:
            return jsonify({
                'code': 0,
                'message': 'generate testcase failed',
                'data': require
            })

@app.route('/api/v1/testcase/delete', methods=['POST'])
def api_v1_testcase_delete():
    data = request.get_json()
    # 前端带的编辑态回到数据库更新失败
    if 'case_id' not in data:
        return jsonify({
            'code': 0,
            'message': f'need parameter `case_id`',
            'data': data
        })
    
    case_id = data.get('case_id')
    with Mysql() as db:
        result = db.delete('testcase', {'case_id': case_id})
        return jsonify({
            'code': 0,
            'message': f'测试用例{case_id}已删除',
            'data': result
        })

@app.route('/api/v1/testcase/update', methods=['POST'])
def api_v1_testcase_update():
    data = request.get_json()
    # 前端带的编辑态回到数据库更新失败
    if 'editing' in data:
        data.pop('editing')
    data.pop('created_at')
    data.pop('updated_at')

    with Mysql() as db:
        update_count = db.update(
            table='testcase',
            update_data=data,
            where={'case_id': data['case_id']}
        )
        return jsonify({
            'code': 0,
            'message': f'更新了{update_count}条数据',
            'data': {}
        })

# 这个接口用于插叙生成的测试用例，返回testcase表数据
@app.route('/api/v1/testcase/search', methods=['POST'])
def api_v1_testcase_search():
    data = request.get_json()
    if 'require_id' not in data:
        return jsonify({
            'code': 400,
            'message': 'need parameter `require_id`',
            'data': data
        })
    
    require_id = data.get('require_id')
    with Mysql() as db:
        testcases = db.search('testcase', where={'require_id': require_id})
        return jsonify({
            'code': 0,
            'message': 'ok',
            'data': testcases
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
    filename = secure_filename(file.filename)
    if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"error": "仅支持PDF/Markdown格式"}), 400

    try:
        # 第一步解析文档，并存储需求到require表格。
        file_stream = BytesIO(file.read())
        require = Require(file_stream, filename)
        require.evaluate().save()

        # 第二部解析文档，并存储为llama_index本地知识。
        result = KnowledgeBaseManager().add_files(filename, file.mimetype)
        return jsonify({
            "status": "success",
            "name": require.record["name"],
            "completeness": require.record["completeness"],
            "testability": require.record["testability"],
            "clarity": require.record["clarity"],
            "consistency": require.record["consistency"],
            "total_score": require.record["total_score"],
            "issues": require.record["issues"],
            "added_nodes": result['added_nodes'],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 这个接口用于查询上传的需求文档，返回reqiure表格字段
@app.route('/api/v1/require/search', methods=['POST'])
def api_v1_require_search():
    with Mysql() as db:
        requires = db.search('require')
        logger.info(f"require: {requires}")
        return jsonify({
            'code': 0,
            'message': 'ok',
            'data': requires
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
        result = db.delete('require', {'require_id': require_id})
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

@app.route('/search', methods=['POST'])
def handle_search():
    question = request.get_json()
    if 'q' not in question or not question['q']:
        return jsonify({"error": "缺少查询参数 q"}), 400
    
    top_k = int(request.args.get('top_k', 5))
    results = KnowledgeBaseManager().query(question['q'], top_k)
    logger.info(f"知识库查询结果：{results}")
    return jsonify({"results": results})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
