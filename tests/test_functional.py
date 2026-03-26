#!/usr/bin/env python3
# coding=utf-8
# @Time     :2026/3/26 10:23
# @Author   :luye
import pytest
import time


class TestProductAPI:

    def test_health_check(self, api_client):
        """测试健康检查接口"""
        resp = api_client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"

    def test_get_existing_product(self, api_client):
        """测试获取已存在商品 (验证缓存逻辑)"""
        # 第一次请求 (预期从数据库读取)
        resp1 = api_client.get("/products/1")
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["data"]["name"] == "iPhone 15"
        # 注意：由于并发或其他测试可能已经预热了缓存，这里不强制断言 source == database
        # 但在干净环境中，第一次通常是 database

        # 第二次请求 (预期从缓存读取)
        resp2 = api_client.get("/products/1")
        assert resp2.status_code == 200
        data2 = resp2.json()
        # 在单线程测试中，第二次通常肯定是 cache
        assert data2["source"] == "cache", f"Expected cache, got {data2['source']}"

    def test_create_product(self, api_client):
        """测试创建商品"""
        unique_name = f"TestItem_{int(time.time())}"
        # FastAPI 通常通过 query params 或 body 接收数据
        # 根据 main.py 定义: def create_product(name: str, price: float, stock: int = 0...)
        # 这些是 query parameters (因为没写 Pydantic model 接收 body)
        params = {"name": unique_name, "price": 10.5, "stock": 5}

        resp = api_client.post("/products/", params=params)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "id" in data

        new_id = data["id"]

        # 验证写入后可查
        verify_resp = api_client.get(f"/products/{new_id}")
        assert verify_resp.status_code == 200
        assert verify_resp.json()["data"]["name"] == unique_name

    def test_get_not_found(self, api_client):
        """测试获取不存在的商品"""
        resp = api_client.get("/products/999999")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()