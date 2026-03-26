# 介绍
项目覆盖docker容器化部署、接口自动化测试、接口性能测试

## 涉及技术
python、docker、mysql、redis、nginx、fastapi、pytest、locust、requests

## 项目结构
testshop-project/
├── app/                  # 被测应用代码 (Python)
│   ├── main.py
│   ├── Dockerfile        # 构建文件
│   └── requirements.txt
├── tests/                # 测试代码 (Pytest)
│   ├── conftest.py       # 全局配置 (Fixture)
│   ├── test_functional.py      # 接口测试用例
│   └── performance/             # 性能测试（locust）
│   │   └── locustfile.py
├── docker/               # 配置文件
│   ├── nginx/
│   │   └── nginx.conf
│   └── mysql/
│       └── init.sql      # 数据库初始化脚本
├── docker-compose.yml    # 编排文件
├── .env                  # 环境变量
└── README.md

## 项目启动
在项目根目录 (testshop-performance) 执行：
```shell
docker compose up -d --build
```
启动状态检查
```shell
docker compose ps
```

# 自动化测试
## 接口测试
在同一个网段系统上执行测试
```shell
pip install pytest requests
cd tests
pytest test_functional.py -v
```

## 性能测试
### web 访问
浏览器访问：http://localhost:8089

### 命令行访问
docker exec -it testshop-locust locust -f /home/locust/locustfile.py --host http://app:8000 --users 100 --spawn-rate 10 --run-time 30s --headless --csv=/home/locust/result

# 环境清理
```shell
docker-compose down -v
```