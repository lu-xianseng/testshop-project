#!/usr/bin/env python3
# coding=utf-8
# @Time     :2026/3/26 10:24
# @Author   :luye

from locust import HttpUser, task, between, events
import random
import time


class ShopUser(HttpUser):
    wait_time = between(0.5, 2)  # 用户思考时间 0.5-2 秒

    # 预定义存在的商品 ID
    existing_ids = [1, 2, 3, 4]

    @task(4)
    def browse_product(self):
        """高频读操作：模拟用户浏览商品，测试 Redis 命中率"""
        product_id = random.choice(self.existing_ids)
        with self.client.get(f"/products/{product_id}", catch_response=True) as response:
            if response.status_code == 200:
                source = response.json().get("source")
                if source == "cache":
                    response.success()  # 命中缓存，完美
                elif source == "database":
                    response.success()  # 命中数据库，允许但希望比例低
                else:
                    response.failure("Unknown source")
            else:
                response.failure(f"Status: {response.status_code}")

    @task(1)
    def create_product_heavy(self):
        """低频写操作：模拟下单/创建，测试 MySQL 写入压力"""
        unique_name = f"LoadTest_{time.time()}_{random.randint(1000, 9999)}"
        payload = {
            "name": unique_name,
            "price": round(random.uniform(10, 500), 2),
            "stock": random.randint(1, 100)
        }

        with self.client.post("/products/", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                new_id = response.json().get("id")
                if new_id:
                    self.existing_ids.append(new_id)  # 动态增加可查询 ID
                    response.success()
                else:
                    response.failure("Created but no ID")
            else:
                response.failure(f"Create Failed: {response.status_code}")


@events.test_start.add_listener
def on_start(environment, **kwargs):
    print("🚀 [Locust] 开始性能测试...")
    print(f"🎯 目标主机: {environment.host}")


@events.test_stop.add_listener
def on_stop(environment, **kwargs):
    print("🛑 [Locust] 测试结束。请检查报告。")