
import uuid
import random
import pymysql
import os
from loguru import logger

from husky.config import MYSQL

def create_database_if_not_exists():
    # 获取项目根目录
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sql_dir = os.path.join(root_dir, 'sql')
    # 创建一个不指定数据库的连接
    config = MYSQL.copy()
    db_name = config.pop('database')
    
    try:
        # 连接到MySQL服务器但不指定数据库
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if not result:
            # 创建数据库
            logger.info(f"创建数据库: {db_name}")
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"数据库 {db_name} 创建成功")
        else:
            logger.info(f"数据库 {db_name} 已存在")

        cursor.close()
        conn.close()

        # 连接到创建的数据库
        try:
            config_with_db = MYSQL.copy()
            conn_with_db = pymysql.connect(**config_with_db)
            cursor_with_db = conn_with_db.cursor()

            # 读取并执行所有SQL文件
            sql_files = [f for f in os.listdir(sql_dir) if f.endswith('.sql')]
            for sql_file in sql_files:
                sql_file_path = os.path.join(sql_dir, sql_file)
                logger.info(f"执行SQL文件: {sql_file_path}")
                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    # 执行SQL脚本
                    for sql_statement in sql_content.split(';'):
                        sql_statement = sql_statement.strip()
                        if sql_statement:
                            cursor_with_db.execute(sql_statement)
            conn_with_db.commit()
            logger.info("所有SQL文件执行成功")
            cursor_with_db.close()
            conn_with_db.close()
        except pymysql.Error as e:
            logger.error(f"执行SQL文件失败: {e}")
    except pymysql.Error as e:
        logger.error(f"创建数据库失败: {e}")

def get_husky_id(prefix=None):
    magic = random.randint(10000, 99999)
    id = f"{prefix}-{str(uuid.uuid4())[:8].upper()}-{magic}"
    return id
