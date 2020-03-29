# 苏大易表单

## 整体架构

整个系统目前分为三块，主后端（`eForm-Resource`）、单点登录服务（`eForm-Auth`、`eForm-Auth-Broker`）、Web 页面（`eForm-Web`、`eForm-SSR`）

基础设施：Caddy2、PostgreSQL、Jenkins Pipeline（Coding.net）、Docker

技术选型：
- 单点登录: JWT / Tornado（`Auth-Broker`）、Flask + Gunicorn（`Auth`）
- 主后端: RESTful API / Flask + Gunicorn、SQLAlchemy
- <s>主后端（*已废弃*）：GraphQL / Flask、Graphene、SQLAlchemy</s>
- Web 页面（Admin）: SPA / Vue、Element-UI
- Web 页面（问卷）：SSR / Nuxt、Vue、Element-UI、Vant-UI
- 持续部署：Jenkins / Coding.net 企业版、Docker
- 反向代理：Caddy2

目前进度：
- 单点登录：100%
- 主后端：80%
- Web 页面（Admin）：70%
- Web 页面（问卷）：60%
- 持续部署：90%

### 项目结构

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
