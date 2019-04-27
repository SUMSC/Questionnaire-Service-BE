# SUMSC eForm 项目总文档

> 此文档未完工，随项目进度更新。

系统的主要需求为两个：问卷、活动报名。为了以后的功能添加和迭代更加方便，不再需要将原有的代码进行重新分割，我们将这两个较为相似的功能点分别建表和编码。

整个系统目前分为三块，Auth Service、Resource Service、Web Service。
基础设施：Confluent Kafka, Elastic stack，Kong API Gateway，ZomboDB

技术选型：
- Auth Service: JWT / ...
- Resource Service: RESTful API / Flask、SQLAlchemy <s>(已废弃 v0.1：GraphQL / Flask、Graphene、SQLAlchemy)</s>
- Web Service: 服务器端渲染 / Nuxt、Vue、Koa

目前进度：
- Auth Service: 90%
- Resource Service: 80%
- Web Service: 40%

## 需求分析

首先从整个APP的目标开始说起，为了内嵌进入你好苏大，需要实现 H5 移动端页面。由于在手机端无法很好地制作问卷和活动报名表单，因此需要实现 PC 端网页。

从用户端看，需要实现的用例有：
- 用户登陆：使用苏大统一身份认证进行登陆；
- 活动报名系统
    - 创建活动：填写活动基本信息、创建活动报名表（PC Only）、发布活动**获得邀请码**（？）；
    - 分享：将活动的报名方式分享到朋友圈；
    - 收集报名信息：从页面上提供的入口下载报名信息；
    - 参加活动：从分享链接或者首页上的入口进入活动页面填写报名表；
- 问卷系统
    - 创建问卷：填写问卷基本信息、创建问卷、发布问卷
    - 分享：将问卷分享到朋友圈；
    - 收集问卷数据：可以采集到所有的问卷信息，以及问卷的数据统计信息；
    - 填写问卷：填写匿名问卷无需登陆；
- 搜索：可以通过搜索查询到公开的活动信息；
- 【我的】：用户在【我的】界面可以使用的功能
    - 发布过的活动：查看发布过的活动信息，下载过去的活动数据，修改活动信息；
    - 报名参加的活动：查看报名参加过的活动信息，修改填写的报名表；
    - 发布过的问卷：查看发布过的问卷，下载已经填写的问卷。

### 需求待解决问题

- 用户权限是否需要用 RBAC 进行控制？
- 文件上传如何实现？（Flask、七牛云、腾讯云）
- Elastic Search如何对接？（定时 REINDEX）
- 分页问题不适用 Relay 是否有更好的解决方案？（重写 RESTful API）

## Auth Service

## 数据存储设计

数据库：PostgreSQL 10

### 表

- `user`: 用户表
    - `id`: `INT`, `Primary Key`, 自增主键
    - `id_tag`: `VARCHAR(16)`, `UNIQUE`, 统一认证学号
    - `name`: `VARCHAR(12)`, 用户姓名
- `event`: 活动表
    - `id`: `INT`, `Primary Key`, 自增主键
    - `name`: `VARCHAR(32)`, `UNIQUE`, 活动名称
    - `detail`: `TEXT`, 活动信息
    - `start_time`: `TIMESTAMP`, 活动开始时间
    - `deadline`: `TIMESTAMP`, 报名截止时间
    - `form`:`JSON`，存储活动报名表单样式
    - `creator_id`: `INT`, `Foreign Key`, 创建者ID
    - `_active`: `BOOLEAN`, 活动是否还可以报名
- `participate`: 参与活动表
    - `event_id`: `INT`, `Foreign Key`
    - `user_id`: `INT`, `Foreign Key`
    - `join_data`: `JSON`, 用户填写的表单数据
- `qnaire`: 问卷表
    - `id`: `INT`, `Primary Key`, 自增主键
    - `name`: `VARCHAR(32)`, 问卷名称
    - `detail`: `TEXT`, 问卷信息
    - `deadline`: `TIMESTAMP`, 问卷截止时间
    - `form`: `JSON`, 存储问卷表单样式
    - `creator_id`: `INT`, `Foreign Key`, 创建者ID
    - `is_anonymous`: `BOOLEAN`, 问卷是否匿名
    - `_active`: `BOOLEAN`, 问卷是否还可以填写
- `answer`: 实名答卷表 
    -`id`: `INT`, `Primary Key`, 自增主键
    - `answer_data`: `JSON`, 用户填写的问卷
    - `user_id`: `INT`, 填写人
    - `qnaire_id`: `INT`, 问卷ID
- `AnonymousAnswer`: 匿名答卷表
    - `id`: `INT`, `Primary Key`, 自增主键
    - `answer_data`: `JSON`, 用户填写的问卷
    - `qnaire_id`: `INT`, 问卷ID

## API 设计

### 项目结构

```
.
├── config.py: 理论上是整个项目的配置文件，但是这里并没有真正使用
├── requirements.txt: pip freeze
├── resource: Flask App Package
│   ├── __init__.py: Flask App (create_app)
│   ├── models.py: SQLALchemy Model
│   ├── restful.py: RESTful API 的 Flask Blueprint (api)
│   ├── schema.py: 已废弃的 Graphene Schema
│   └── utils.py: 一些通用函数，事实上并没有用到
├── setup.cfg: 用于做 pytest 的配置
├── setup.py: Python Package 的配置入口，实际意义也是 pytest
└── tests: 单元测试
    ├── __init__.py
    ├── conftest.py: 一些 test fixture
    ├── test_api.py：RESTful API 的单元测试
    ├── test_mutations.py: GraphQL 的 Mutation 单元测试
    └── test_query.py: GraphQL 的 Query 单元测试（无效）
```

### RESTful API



### GraphQL API（已废弃）

#### Query

直接照抄 Model 即可。

#### Mutations

- CreateUser: 创建用户
- CreateEvent: 创建活动
- CreateNaire: 创建问卷
- JoinEvent: 加入活动
- AnswerNaire: 填写问卷
- AnonymousAnswerNaire: 填写匿名问卷
- UpdateNaire: 更新问卷
- UpdateAnswer: 更新答卷
- UpdateEvent: 更新活动
- UpdateParticipation: 更新报名信息

## 基础设施

> 目前部署仅支持Docker-compose

### Kafka

用于解耦合,使用社区免费版本的Confluent Kafka辅以开源前端监控

### Elastic Stack

用于提供数据库搜索API以及日志分析监控。

#### 使用方法

[RESTful API](https://www.elastic.co/guide/index.html)

>  **重置数据库及 ELK INDEX 方法**:
> - `进入`Kibana/Management`，删除索引` ，
> - `flask shell > db.drop_all(); db.create_all()`，
> - 访问`<RESOURCE_URL>/build_index`。

### Kong

用于解决负载均衡，缓存，路由，访问控制，服务代理，监控，日志等

### Zombodb

用于将PG数据导入elastic

## 表单格式文档

- 表单种类见：`表单种类.md`，
- 表单格式见：`表单格式.json`，
- 答案格式见：`答案格式.json`。
