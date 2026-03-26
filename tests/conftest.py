#!/usr/bin/env python3
# coding=utf-8
# @Time     :2026/3/26 10:23
# @Author   :luye

import pytest
import requests
from urllib.parse import urljoin

# 基础 URL (指向 Nginx)
# 注意：如果你的测试机器无法解析 localhost 到 docker 容器，可能需要改为 http://127.0.0.1
BASE_URL = "http://localhost:88"

class APIClient:
    def __init__(self, base_url):
        self.session = requests.Session()
        self.base_url = base_url

    def _build_url(self, path):
        # 确保路径以 / 开头，并拼接 base_url
        if not path.startswith('/'):
            path = '/' + path
        return urljoin(self.base_url, path)

    def get(self, path, **kwargs):
        return self.session.get(self._build_url(path), **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(self._build_url(path), **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(self._build_url(path), **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(self._build_url(path), **kwargs)

@pytest.fixture(scope="session")
def api_client():
    """
    返回一个封装好的 API 客户端，自动处理 Base URL 拼接
    """
    client = APIClient(BASE_URL)
    yield client
    client.session.close()

@pytest.fixture
def cleanup_products(api_client):
    """用于记录创建的商品 ID"""
    created_ids = []
    yield created_ids
    # 这里可以添加清理逻辑，例如遍历 created_ids 调用删除接口