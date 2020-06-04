# 苏大易表单

本项目为 eForm 项目的主要后台。

## 整体架构

整个系统目前分为三块，主后端（`eForm-Resource`）、单点登录服务（`eForm-Auth`、`eForm-Auth-Broker`）、Web 页面（`eForm-Web`、`eForm-SSR`）

基础设施：Caddy2、PostgreSQL、Jenkins Pipeline（Coding.net 企业版）、Docker

技术选型：
- 单点登录: JWT / Tornado（`Auth-Broker`）、Flask + Gunicorn（`Auth`）
- 主后端: RESTful API / Flask + Gunicorn、SQLAlchemy
- <s>主后端（*已废弃*）：GraphQL / Flask、Graphene、SQLAlchemy</s>
- Web 页面（Admin）: SPA / Vue、Element-UI
- Web 页面（问卷）：SSR / Nuxt、Vue、Element-UI、Vant-UI
- 持续部署：Jenkins / Coding.net 企业版、Docker
- 反向代理：Caddy2

目前进度：
- 单点登录：98%，本地开发与远端路由不一致，此问题暂不修复
- 主后端：100%
- Web 页面（Admin）：90%，没有添加分享到微博、微信的功能
- Web 页面（问卷）：90%，计划中的部分问卷设置没有实现
- 持续部署：100%

## 项目结构

```
.
├── config.py: 整个项目的配置文件
├── requirements.txt
├── resource: Flask App Package
│   ├── __init__.py: Flask App (create_app)
│   ├── models.py: SQLALchemy Model
│   ├── restful.py: RESTful API 的 Flask Blueprint
│   └── utils.py: 一些通用函数
├── setup.cfg: 用于做 pytest 的配置
├── setup.py: Python Package 的配置入口，实际意义也是 pytest
└── tests: 单元测试
    ├── __init__.py
    └── conftest.py: 一些 test fixture
```

## 开发流程

核心依赖：Python 3.6/3.7

请注意配置好 PostgreSQL 的数据库和表，链接请在 `config.py` 中配置，建表时按照 `resource/models.py` 中的配置即可。

或者也可以直接在此文件夹的虚拟环境内运行 `db.create_all()`。

### Flask 开发环境运行

```sh
# 创建虚拟环境（可选）
python3 -m venv ./venv

# 进入虚拟环境
source ./venv/bin/activate

# 安装依赖
python3 -m pip install -r requirements.txt

# 运行 Flask
flask run
```

### Gunicorn 运行

```sh
gunicorn --config=gunicorn.conf.py resource:create_app()
```

### Docker 运行

```sh
docker run --name EFR --net host -v /home/amber/upload:/opt/resource/upload -p 127.0.0.1:8080:8080 -d ${DOCKER_REPO}/${DOCKER_TAG}
```

