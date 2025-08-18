import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from io import BytesIO

from husky.models.requirements import Requirements
from husky.services.knowledge_service import KnowledgeService

# 创建蓝图
file_bp = Blueprint('file', __name__)

@file_bp.route('/upload', methods=['POST'])
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

        # 第二步解析文档，并存储为llama_index本地知识。
        file_stream.seek(0)  # 重置文件流指针
        result = KnowledgeService().add_files([file_stream], [file.mimetype])
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