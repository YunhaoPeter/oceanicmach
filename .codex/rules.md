# Oceanicmach 开发规则

## 项目定位
企业内部管理系统，技术栈 FastAPI + SQLAlchemy + Jinja2 + WeasyPrint + MySQL。
部署在阿里云 ECS (8.153.204.48)，通过域名或 IP 公网访问。

## 开发流程

1. 本地修改代码，用 SQLite（自动）跑通
2. `git add . && git commit -m "feat: xxx"` 提交
3. `git push` 推送到 GitHub (git@github.com:YunhaoPeter/oceanicmach.git)
4. SSH 到 ECS 部署：
```bash
ssh root@8.153.204.48
cd /opt/oceanicmach && git pull && systemctl restart oceanicmach
```

## 数据库规则

- 数据库结构变更：先改 `app/models.py`，再改 Router，启动时自动建表
- 本地开发：默认使用 SQLite (`oceanicmach.db`)，无需安装 MySQL
- 生产（ECS）：MySQL 8.0，连接信息通过 systemd 环境变量注入
- 不要手动写 SQL 操作表结构，用 SQLAlchemy ORM

## 新增模块标准流程

1. `app/models.py` — 添加 Model 类
2. `app/routers/xxx.py` — 创建 Router（CRUD + 模板渲染）
3. `app/templates/xxx/` — 创建 Jinja2 模板（list.html, form.html）
4. `app/main.py` — 注册 Router
5. 更新导航栏 `app/templates/base.html`
6. 更新 README.md 目录结构

## 代码规范

- 模板复用：列表页继承 `base.html`，表单页放回列表链接
- 路由命名：复数形式，如 `/products`、`/customers`
- 枚举值用中文（SAEnum），与业务人员沟通一致
- 所有新建文件加注释说明用途

## 部署注意事项

- ECS 上不写代码，只 `git pull` + 重启
- 本地 `requirements.txt` 适配 Python 3.9，ECS 用 Python 3.11（不混用）
- 重启服务：`systemctl restart oceanicmach`
- 查看日志：`tail -f /opt/oceanicmach/logs/stdout.log`

## 密码与敏感信息

- 数据库密码不入库（已在 .gitignore）
- systemd 环境变量存放 ECS 端配置
- ECS root 密码：不要写进代码或 README
