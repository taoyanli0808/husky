CREATE TABLE testcases (
    `case_id` VARCHAR(50) NOT NULL PRIMARY KEY COMMENT '测试用例唯一标识符',
    `task_id` VARCHAR(50) NOT NULL COMMENT '任务ID，每次创建用例生成唯一任务ID',
    `require_id` VARCHAR(50) NOT NULL COMMENT '需求ID',
    `case_name` VARCHAR(255) NOT NULL COMMENT '测试用例名称',
    `preconditions` JSON COMMENT '前置条件(JSON数组)',
    `test_steps` JSON NOT NULL COMMENT '测试步骤(JSON数组)',
    `expected_result` JSON NOT NULL COMMENT '预期结果(JSON数组)',
    `priority` VARCHAR(10) NOT NULL COMMENT '优先级(P0-P3)',
    `test_type` JSON COMMENT '测试类型(JSON数组)',
    `create` BOOLEAN DEFAULT 0 COMMENT '是否手工添加',
    `modify` BOOLEAN DEFAULT 0 COMMENT '是否修改',
    `accept` BOOLEAN DEFAULT 0 COMMENT '是否验收',
    `review` BOOLEAN DEFAULT 0 COMMENT '是否评审',
    `verify` BOOLEAN DEFAULT 0 COMMENT '是否验证',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;