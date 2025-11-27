"""
MySQL数据库管理器
提供数据库连接、查询执行等功能
"""

import pymysql
from pymysql.cursors import DictCursor
from typing import List, Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBManager:
    """MySQL数据库管理器类"""
    
    def __init__(self, host='localhost', port=3306, user='root', 
                 password='', database=''):
        """
        初始化数据库管理器
        
        Args:
            host: 数据库主机地址
            port: 数据库端口
            user: 用户名
            password: 密码
            database: 数据库名
            charset: 字符编码
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        # self.charset = charset
        self.connection = None
        
    def connect(self) -> bool:
        """
        连接到MySQL数据库
        
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                # charset=self.charset,
                cursorclass=DictCursor,
                autocommit=False
            )
            logger.info(f"成功连接到数据库: {self.database}@{self.host}:{self.port}")
            return True
        except pymysql.Error as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
            self.connection = None
    
    def is_connected(self) -> bool:
        """
        检查数据库是否已连接
        
        Returns:
            bool: 已连接返回True，否则返回False
        """
        return self.connection is not None and self.connection.open


# 使用示例
if __name__ == "__main__":
    # 创建数据库管理器实例
    db = DBManager(
        host='localhost',
        user='root',
        password='',  # 请修改为实际密码
        database=''    # 请修改为实际数据库名
    )
    
    # 方式1: 手动连接和断开
    if db.connect():
        print('连接成功')
        # 查询示例
        results = db.select('your_table', limit=10)
        if results:
            for row in results:
                print(row)
        
        db.disconnect()
