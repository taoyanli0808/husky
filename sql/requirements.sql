CREATE TABLE `requirements` (
  `require_id` varchar(50) NOT NULL COMMENT '需求唯一ID（如REQ-支付-2023-001）',
  `require_name` text NOT NULL COMMENT '需求名称（如"用户登录支持短信验证码"）',
  `description` longtext COMMENT '需求详细描述',
  `original_text` longtext COMMENT '需求原文（完整原始描述）',
  `business_domain` varchar(50) DEFAULT NULL COMMENT '业务域（如电商/支付）',
  `module` varchar(50) DEFAULT NULL COMMENT '功能模块（如认证模块）',
  `priority` enum('P0','P1','P2','P3') DEFAULT 'P2' COMMENT '优先级',
  `quality_score` json NOT NULL COMMENT '质量评分JSON',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否逻辑删除',
  `tags` json DEFAULT NULL COMMENT '标签数组（如["API","安全"]）',
  `related_req_ids` json DEFAULT NULL COMMENT '关联需求ID列表',
  `source` varchar(100) DEFAULT NULL COMMENT '需求来源（如PRDv2.1）',
  `status` enum('draft','review','dev','released') DEFAULT 'draft' COMMENT '需求状态',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`require_id`),
  UNIQUE KEY `idx_require_id` (`require_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='需求主表';