CREATE TABLE points (
    point_id VARCHAR(50) PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL COMMENT '任务ID，每次创建用例生成唯一任务ID',
    require_id VARCHAR(50) NOT NULL COMMENT '需求ID',
    function_name VARCHAR(100) NOT NULL,
    test_type VARCHAR(50) NOT NULL COMMENT '测试类型: read/create/update/delete等',
    `description` TEXT NOT NULL,
    module VARCHAR(100) NOT NULL,
    business_domain VARCHAR(100) NOT NULL,
    chunks TEXT NOT NULL,
    preconditions JSON NOT NULL COMMENT '预条件数组，存储为JSON格式',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_task_id (task_id),
    INDEX idx_function_name (function_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='功能点明细表';