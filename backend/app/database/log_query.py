import sqlite3
import os
from datetime import datetime
from typing import List
from langchain_core.documents import Document


class QueryLogger:
    """Database management class for recording RAG query document information"""
    
    def __init__(self, db_path="backend/data/logs/query_logs.db"):
        """Initialize database connection and create necessary table structures"""
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to database
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create document logs table (if not exists)
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
        """Record document information to the database"""
        timestamp = datetime.now().isoformat()
        
        for doc in docs:
            # Extract document metadata
            source_manual = doc.metadata.get('source_manual', '')
            header1 = doc.metadata.get('Header1', '')
            header2 = doc.metadata.get('Header2', '')
            doc_type = doc.metadata.get('type', 'text')
            
            # Insert into database
            self.cursor.execute(
                "INSERT INTO doc_logs (timestamp, source_manual, Header1, Header2, type) VALUES (?, ?, ?, ?, ?)",
                (timestamp, source_manual, header1, header2, doc_type)
            )
        
        self.conn.commit()
    
    def get_document_stats(self, days=7):
        """Get most frequently retrieved document sources from recent days"""
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
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


# Singleton pattern, ensuring only one database connection instance globally
_logger_instance = None

def get_query_logger():
    """Get QueryLogger singleton instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = QueryLogger()
    return _logger_instance