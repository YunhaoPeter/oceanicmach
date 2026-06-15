Oceanicmach — 企业内部管理平台
=============================

## 项目概述

Oceanicmach 是一个基于 Python FastAPI 的企业内部管理系统，部署在阿里云 ECS 上，
通过浏览器访问。当前已完成八大主数据管理模块，支持报价单 PDF 生成（WeasyPrint）。

## 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 后端框架 | FastAPI | 0.128+ |
| ORM | SQLAlchemy | 2.0+ |
| 模板引擎 | Jinja2 | 3.1+ |
| PDF 生成 | WeasyPrint | 66+ |
| 数据库 (本地) | SQLite | — |
| 数据库 (生产) | MySQL | 8.0 |
| Web 服务器 | Nginx → Uvicorn | — |
| 前端增强 | htmx | 1.9 CDN |

## 项目结构

```
app/
├── main.py              # FastAPI 入口，注册所有 Router
├── config.py            # 应用配置常量
├── database.py          # 数据库连接（SQLite 本地 / MySQL 生产）
├── models.py            # 8 张主数据表的 SQLAlchemy Model
├── routers/
│   ├── customers.py     # 客户 + 联系人 + 收货地 CRUD
│   ├── departments.py   # 部门树形 + 部门角色 CRUD
│   ├── employees.py     # 员工 CRUD
│   ├── entities.py      # 公司主体 CRUD
│   └── products.py      # 产品 CRUD
├── templates/
│   ├── base.html        # 公共布局（导航栏 + htmx）
│   ├── index.html       # 首页
│   ├── customers/       # 客户列表、表单、详情(Tab)
│   ├── departments/     # 部门树形列表、表单、角色管理
│   ├── employees/       # 员工列表、表单
│   ├── entities/        # 公司主体列表、表单
│   └── products/        # 产品列表、表单
└── static/css/style.css
```

## 数据库设计 (8 张表)

```
外部链路:                    内部链路:
                            公司主体 (company_entities)
客户 (customers)               │
  ├── 联系人 (customer_contacts) 部门 (departments, 自引用树)
  └── 收货地 (customer_addresses)  ├── 部门角色 (department_roles)
                                  └── 员工 (employees)

独立: 产品 (products)
```

SQLAlchemy Model 定义在 `app/models.py`，启动时自动建表。

## 本地开发

```bash
cd oceanicmach
python3 -m venv venv        # Python 3.9+
source venv/bin/activate
pip install -r requirements.txt

# 本地用 SQLite（默认，无需安装 MySQL）
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 如需连 MySQL，设置环境变量：
export MYSQL_HOST=127.0.0.1
export MYSQL_USER=root
export MYSQL_PASSWORD=xxx
export MYSQL_DB=oceanicmach
```

打开 http://127.0.0.1:8000

## 生产部署

生产服务器: 阿里云 ECS (Alibaba Cloud Linux 3), 2G 内存
公网地址: http://8.153.204.48

部署流程:
```bash
ssh root@8.153.204.48
cd /opt/oceanicmach
git pull
systemctl restart oceanicmach    # 开机自启，systemd 管理
```

服务栈: Nginx (80 → 8000) → Uvicorn (2 workers) → FastAPI

## 版本管理

GitHub: https://github.com/YunhaoPeter/oceanicmach
master 分支直接开发，提交前缀: feat: / fix: / chore:

```bash
# 日常工作流
git add . && git commit -m "feat: 描述" && git push
```

## 注意事项

- 本地开发使用 SQLite，生产使用 MySQL
- Nginx 配置: /etc/nginx/conf.d/oceanicmach.conf
- systemd 配置: /etc/systemd/system/oceanicmach.service
- 应用日志: /opt/oceanicmach/logs/
- 数据库密码和连接信息勿入库 (.gitignore 已处理)
- 新增实体需要同步更新 models.py, routers/, templates/
