import sqlite3
import os
from datetime import datetime
from typing import List
from langchain_core.documents import Document


class QueryLogger:
    """记录RAG查询文档信息的数据库管理类"""
    
    def __init__(self, db_path="backend/data/logs/query_logs.db"):
        """初始化数据库连接和创建必要的表结构"""
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 连接数据库
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 创建文档日志表(如果不存在)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS doc_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_manual TEXT,
            Header1 TEXT,
            Header2 TEXT,
            type TEXT
        )
        ''')
        
        self.conn.commit()
    
    def log_documents(self, docs: List[Document]) -> None:
        """将文档信息记录到数据库中"""
        timestamp = datetime.now().isoformat()
        
        for doc in docs:
            # 提取文档元数据
            source_manual = doc.metadata.get('source_manual', '')
            header1 = doc.metadata.get('Header1', '')
            header2 = doc.metadata.get('Header2', '')
            doc_type = doc.metadata.get('type', 'text')
            
            # 插入数据库
            self.cursor.execute(
                "INSERT INTO doc_logs (timestamp, source_manual, Header1, Header2, type) VALUES (?, ?, ?, ?, ?)",
                (timestamp, source_manual, header1, header2, doc_type)
            )
        
        self.conn.commit()
    
    def get_document_stats(self, days=7):
        """获取最近几天最常被检索的文档来源"""
        cutoff_date = (datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        self.cursor.execute(
            """SELECT source_manual, COUNT(*) as count 
               FROM doc_logs 
               WHERE timestamp > ? 
               GROUP BY source_manual 
               ORDER BY count DESC""",
            (cutoff_date,)
        )
        
        return self.cursor.fetchall()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 单例模式，确保全局只有一个数据库连接实例
_logger_instance = None

def get_query_logger():
    """获取QueryLogger单例实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = QueryLogger()
    return _logger_instance