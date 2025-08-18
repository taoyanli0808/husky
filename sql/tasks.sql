CREATE TABLE `tasks` (
  `task_id` VARCHAR(50) NOT NULL PRIMARY KEY COMMENT '任务唯一ID',
  `require_id` VARCHAR(50) COMMENT '关联需求ID',
  `task_type` ENUM('point_analysis', 'testcase_analysis') NOT NULL COMMENT '任务类型',
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  `progress` TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '进度百分比(0-100)',
  `message` TEXT COMMENT '当前状态信息',
  `result` JSON COMMENT '最终结果数据',
  `start_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务开始时间',
  `end_time` DATETIME COMMENT '任务结束时间',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_require_id` (`require_id`),
  INDEX `idx_status` (`status`),
  FOREIGN KEY (`require_id`) REFERENCES `requirements`(`require_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异步任务状态表';