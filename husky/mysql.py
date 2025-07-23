
import json
import pymysql

from loguru import logger

from typing import Dict, List, Optional, Union

from husky.config import MYSQL


class Mysql:
    def __init__(self):
        self.connection = pymysql.connect(**MYSQL, cursorclass=pymysql.cursors.DictCursor)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def create(
        self, 
        table: str, 
        data: Dict[str, Union[str, int, bool]]
    ) -> bool:
        """通用插入操作"""
        try:
            # 序列化所有JSON字段
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    processed_data[f"{key}"] = json.dumps(value, ensure_ascii=False)
                else:
                    processed_data[f"{key}"] = value

            with self.connection.cursor() as cursor:
                # 1. 转义所有列名（防止保留字冲突）
                columns = ', '.join([f'`{k}`' for k in processed_data.keys()])

                # 2. 转换布尔值为整型
                values = []
                for v in processed_data.values():
                    if isinstance(v, bool):
                        values.append(int(v))
                    else:
                        values.append(v)

                # 3. 构造参数化SQL
                placeholders = ', '.join(['%s'] * len(values))
                sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"

                # 4. 记录完整SQL（调试用）
                logger.debug(f"Execute SQL: {sql}")
                logger.debug(f"With values: {values}")

                cursor.execute(sql, tuple(values))
            self.connection.commit()
            return True
        except pymysql.Error as e:
            logger.error(f"Create error: {e}")
            self.connection.rollback()
            return False

    def search(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[Dict[str, Union[str, int]]] = None
    ) -> List[Dict]:
        """通用查询操作"""
        try:
            with self.connection.cursor() as cursor:
                # 选择列处理
                select_columns = '*' if not columns else ', '.join(columns)
                
                # 条件处理
                where_clause = ''
                params = ()
                if where:
                    conditions = [f"{k} = %s" for k in where.keys()]
                    where_clause = " WHERE " + " AND ".join(conditions)
                    params = tuple(where.values())
                
                sql = f"SELECT {select_columns} FROM `{table}`{where_clause}"
                logger.info(f"search: {sql}")
                cursor.execute(sql, params)
                return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Read error: {e}")
            return []

    def update(
        self,
        table: str,
        update_data: Dict[str, Union[str, int, bool]],
        where: Dict[str, Union[str, int]]
    ) -> int:
        """通用更新操作"""
        try:
            with self.connection.cursor() as cursor:
                # 更新字段处理
                set_clause = ', '.join([f"`{k}` = %s" for k in update_data.keys()])
                
                # 条件处理
                where_clause = ' AND '.join([f"`{k}` = %s" for k in where.keys()])
                
                sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
                params = tuple(update_data.values()) + tuple(where.values())
                
                cursor.execute(sql, params)
                self.connection.commit()
                return cursor.rowcount
        except pymysql.Error as e:
            print(f"Update error: {e}")
            self.connection.rollback()
            return 0

    def delete(
        self,
        table: str,
        where: Dict[str, Union[str, int]]
    ) -> int:
        """通用删除操作"""
        try:
            with self.connection.cursor() as cursor:
                where_clause = ' AND '.join([f"{k} = %s" for k in where.keys()])
                sql = f"DELETE FROM `{table}` WHERE {where_clause}"
                logger.info(f'sql: {sql}')
                cursor.execute(sql, tuple(where.values()))
                self.connection.commit()
                return cursor.rowcount
        except pymysql.Error as e:
            print(f"Delete error: {e}")
            self.connection.rollback()
            return 0
