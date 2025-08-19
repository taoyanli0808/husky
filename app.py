
import json
from loguru import logger
from flask_cors import CORS
from flask import Flask, request, jsonify

# 导入API蓝图
from husky.api.v1 import v1_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制上传文件100MB

# 注册API蓝图
app.register_blueprint(v1_bp)

# 保留根路由或其他非API路由
@app.route('/')
def index():
    return jsonify({
        'message': 'Husky API Server is running',
        'version': '1.0.0'
    })

# 保留搜索路由
@app.route('/search', methods=['POST'])
def handle_search():
    question = request.get_json()
    if 'q' not in question or not question['q']:
        return jsonify({"error": "缺少查询参数 q"}), 400
    
    top_k = int(request.args.get('top_k', 5))
    from husky.services.knowledge_service import KnowledgeService
    results = KnowledgeService().query(question['q'], top_k)
    logger.info(f"知识库查询结果：{results}")
    return jsonify({"results": results})

# 全局错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'code': 500,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
