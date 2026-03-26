#!/usr/bin/env python3
# coding=utf-8
# @Time     :2026/3/26 10:23
# @Author   :luye

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import redis
import os
import json

# 配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://tester:tester123@localhost:3306/testshop_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 数据库初始化
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis 客户端
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="TestShop API", description="MySQL 5.7 + Redis Performance Test App")


# 模型定义
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    price = Column(Float)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    # 确保表存在 (生产环境通常用 Alembic 迁移)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified.")


@app.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = f"product:{product_id}"

    # 1. 尝试从 Redis 获取
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {"source": "cache", "data": json.loads(cached_data)}

    # 2. 从 MySQL 获取
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product_data = {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }

    # 3. 写入 Redis (过期时间 300 秒)
    redis_client.setex(cache_key, 300, json.dumps(product_data))

    return {"source": "database", "data": product_data}


@app.post("/products/")
def create_product(name: str, price: float, stock: int = 0, db: Session = Depends(get_db)):
    new_product = Product(name=name, price=price, stock=stock)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 清除可能的旧缓存 (如果存在相同 ID 的缓存，虽然新 ID 通常不会有)
    return {"status": "success", "id": new_product.id, "name": new_product.name}


@app.get("/health")
def health_check():
    return {"status": "healthy", "db": "connected", "redis": "connected"}