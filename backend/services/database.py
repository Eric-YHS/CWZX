from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cwzx.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class NewsDB(Base):
    __tablename__ = "news"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    publish_time = Column(DateTime, nullable=False)
    news_type = Column(String, nullable=False)
    stock_codes = Column(JSON)
    tags = Column(JSON)
    url = Column(String)
    sentiment = Column(String)
    impact_analysis = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class StockDB(Base):
    __tablename__ = "stocks"
    
    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    current_price = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float)
    market_cap = Column(Float)
    last_update = Column(DateTime, default=datetime.utcnow)

class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    messages = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

async def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()