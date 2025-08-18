from flask import Blueprint
from husky.api.v1.testcase import testcase_bp
from husky.api.v1.require import require_bp
from husky.api.v1.point import point_bp
from husky.api.v1.file import file_bp
from husky.api.v1.task import task_bp

# 创建v1蓝图
v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# 注册子蓝图
v1_bp.register_blueprint(testcase_bp, url_prefix='/testcase')
v1_bp.register_blueprint(require_bp, url_prefix='/require')
v1_bp.register_blueprint(point_bp, url_prefix='/point')
v1_bp.register_blueprint(file_bp, url_prefix='/file')
v1_bp.register_blueprint(task_bp, url_prefix='/task')