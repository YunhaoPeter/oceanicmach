# Oceanicmach 开发规则

## 项目定位
企业内部管理系统，技术栈 FastAPI + SQLAlchemy + Jinja2 + WeasyPrint + MySQL。
部署在阿里云 ECS (8.153.204.48)，通过域名或 IP 公网访问。

## 开发流程
1. 本地修改代码，用 SQLite（自动）跑通
2. 跑完本地测试清单
3. `git add . && git commit -m "feat: xxx"` 提交
4. `git push` 推送到 GitHub (git@github.com:YunhaoPeter/oceanicmach.git)
5. SSH 到 ECS 部署：
```bash
ssh root@8.153.204.48
cd /opt/oceanicmach && git pull && systemctl restart oceanicmach
```

## 本地测试清单（每次 push 前必跑）
1. 全模块列表页可正常加载（200）
2. 新增表单可提交，数据写入后可回查
3. 编辑功能正常回显已有数据
4. 删除操作有二次确认，删除后数据不再出现
5. 客户详情 Tab 可正常切换（联系人 / 收货地）
6. 部门树形结构正常展示父子关系
7. 导航栏五个入口全部可达
8. 翻页和筛选组合正常（如有分页模块）

## 数据库规则
- 数据库结构变更：先改 `app/models.py`，再改 Router，启动时自动建表
- 本地开发：默认使用 SQLite (`oceanicmach.db`)，无需安装 MySQL
- 生产（ECS）：MySQL 8.0，连接信息通过 systemd 环境变量注入
- 不要手动写 SQL 操作表结构，用 SQLAlchemy ORM

## 数据库变更安全规则
- `Base.metadata.create_all()` 只会**创建新表**和**新增字段**，不会自动删改已有结构
- 修改已有表的字段类型、删除字段、重命名：必须登录 ECS 手动执行 SQL
- 新部署包含数据库结构变更时，先备份生产库：
```bash
mkdir -p /opt/backups
mysqldump -u root -p oceanicmach > /opt/backups/oceanicmach_$(date +%Y%m%d_%H%M).sql
```
- 在本地 SQLite 验证过 Model 导入无误后再 push

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

## 发布前安全检查
- `git pull` 前先在 ECS 上确认无未提交代码：`git status`
- 重启后立即验证：
```bash
curl -s http://127.0.0.1:8000/health
systemctl status oceanicmach | grep Active
```
- 如有报错，查看日志定位问题：
```bash
tail -50 /opt/oceanicmach/logs/stderr.log
```
- 新增 Python 依赖时，先在 ECS 上安装：
```bash
cd /opt/oceanicmach && source venv/bin/activate && pip install xxx
```

## 回滚流程（上线后发现异常）
```bash
ssh root@8.153.204.48
cd /opt/oceanicmach
git log --oneline -5       # 找上一个稳定提交
git reset --hard <commit>  # 回滚到指定版本
systemctl restart oceanicmach
curl -s http://127.0.0.1:8000/health  # 验证恢复
```

## 开发边界提醒
- 本地 SQLite vs 生产 MySQL：注意字段类型差异（如 DateTime/Enum）
- 不要在本地连 ECS 的 MySQL 做开发测试
- 静态文件（CSS/JS）和模板（Jinja2）变更同样需要在浏览器测试
- htmx 请求走的是页面级渲染，新增动态交互需确认不破坏已有模板

## 部署注意事项
- ECS 上不写代码，只 `git pull` + 重启
- 本地 `requirements.txt` 适配 Python 3.9，ECS 用 Python 3.11（不混用）
- 重启服务：`systemctl restart oceanicmach`
- 查看日志：`tail -f /opt/oceanicmach/logs/stdout.log`

## 密码与敏感信息
- 数据库密码不入库（已在 .gitignore）
- systemd 环境变量存放 ECS 端配置
- ECS root 密码、GitHub Token：不要写进任何项目文件
