# Oceanicmach 实体清单

> 版本 1.0.0 | 更新日期: 2026-06-28
> 此文件为 docs/entity-inventory.json 的可读版本，作为实体变更治理的基线依据。

---

## 概览

| 维度 | 内容 |
|:--|:--|
| 实体总数 | 8 张数据表 |
| 值集总数 | 13 个 SAEnum 选项集 |
| 业务域 | 公司主体 → 部门/角色 → 员工（内部链路）；客户 → 联系人/收货地（外部链路）；产品（独立链路） |
| 通用混入 | 所有实体含 TimestampMixin（created_at + updated_at） |
| 当前阶段 | 主数据框架阶段，业务编码规则均未定义，外键均未配置级联删除 |

---

## 实体关系图

```
外部链路:                    内部链路:
                            公司主体 (company_entities)
客户 (customers)               │
  ├── 联系人 (customer_contacts) 部门 (departments, 自引用树)
  └── 收货地 (customer_addresses)  ├── 部门角色 (department_roles)
                                  └── 员工 (employees)

独立: 产品 (products)
```

---

## 值集清单

| 值集编码 | 描述 | 枚举值 |
|:--|:--|:--|
| entity_type_enum | 公司主体类型 | 母公司, 子公司, 分公司, 办事处 |
| entity_status_enum | 公司主体状态 | 启用, 禁用 |
| product_category_enum | 产品分类 | 成品, 半成品, 原材料, 服务 |
| product_unit_enum | 计量单位 | 个, 台, 套, 件, m, t, L |
| product_status_enum | 产品状态 | 在售, 停产, 研发中 |
| dept_status_enum | 部门状态 | 启用, 禁用 |
| role_status_enum | 角色状态 | 启用, 禁用 |
| gender_enum | 性别 | 男, 女 |
| employee_status_enum | 员工状态 | 在职, 离职, 试用期 |
| customer_type_enum | 客户类型 | 企业客户, 个人客户 |
| customer_level_enum | 客户等级 | A, B, C, D |
| customer_status_enum | 客户状态 | 潜在, 活跃, 休眠, 黑名单 |
| customer_source_enum | 客户来源 | 官网, 展会, 转介绍, 自主开发 |

---

## 实体 1：公司主体（CompanyEntity）

表名: `company_entities` | 模型路径: `app/models.py` | 阶段: Phase 1

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| entity_code | 主体编码 | Entity Code | 公司主体业务编号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | COM-001 |
| name | 主体全称 | Full Name | 公司法定全称 | — | String(200) | 是 | — | — | 海洋机械制造有限公司 |
| short_name | 简称 | Short Name | 日常使用简称 | — | String(100) | — | — | — | 海洋机械 |
| credit_code | 统一社会信用代码 | Unified Social Credit Code | 18位信用代码 | — | String(18) | — | — | — | 91310115MA1H123456 |
| legal_representative | 法定代表人 | Legal Representative | 企业法人姓名 | — | String(50) | — | — | — | 张三 |
| registered_address | 注册地址 | Registered Address | 营业执照注册地址 | — | String(300) | — | — | — | 上海市浦东新区XX路1号 |
| contact_phone | 联系电话 | Contact Phone | 公司对外联系电话 | — | String(20) | — | — | — | 021-12345678 |
| entity_type | 主体类型 | Entity Type | 法律组织形态分类 | SAEnum枚举列 | SAEnum | 是 | entity_type_enum | — | 母公司 |
| status | 状态 | Status | 启用/禁用控制 | SAEnum枚举列，默认启用 | SAEnum | 默认启用 | entity_status_enum | — | 启用 |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 集团总部 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- has_many → Department (via company_entity_id)
- has_many → Employee (via company_entity_id)

---

## 实体 2：产品（Product）

表名: `products` | 模型路径: `app/models.py` | 阶段: Phase 1

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| product_code | 产品编码 | Product Code | 产品唯一业务编号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | PROD-001 |
| name | 产品名称 | Product Name | 产品品名全称 | — | String(200) | 是 | — | — | 数控机床X200 |
| model | 产品型号 | Model | 产品规格型号 | — | String(100) | — | — | — | X200-A |
| category | 产品分类 | Category | 产品所属业务类别 | SAEnum枚举列 | SAEnum | 是 | product_category_enum | — | 成品 |
| specification | 规格描述 | Specification | 产品规格参数说明 | — | String(200) | — | — | — | 2000x1000x800mm |
| unit | 计量单位 | Unit of Measure | 出入库计量单位 | SAEnum枚举列 | SAEnum | 是 | product_unit_enum | — | 台 |
| sales_price | 标准售价 | Standard Sales Price | 对外标准销售单价 | Numeric(12,2) | Numeric(12,2) | — | — | — | 150000.00 |
| cost_price | 成本价 | Cost Price | 产品核算成本单价 | Numeric(12,2) | Numeric(12,2) | — | — | — | 120000.00 |
| tax_rate | 税率(%) | Tax Rate (%) | 适用增值税税率 | Numeric(4,2)，默认13.00 | Numeric(4,2) | 默认13.00 | — | — | 13.00 |
| status | 状态 | Status | 产品生命周期阶段 | SAEnum枚举列，默认在售 | SAEnum | 默认在售 | product_status_enum | — | 在售 |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 主力机型 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

---

## 实体 3：部门（Department）

表名: `departments` | 模型路径: `app/models.py` | 阶段: Phase 2

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| company_entity_id | 归属公司主体 | Belonging Company Entity ID | 部门所属法人主体 | 外键FK -> company_entities.id | Integer (FK) | 是 | — | — | 1 |
| parent_id | 上级部门 | Parent Department ID | 上级部门，树形层级 | 自引用FK -> departments.id | Integer (FK, self-ref) | — | — | — | null |
| department_code | 部门编码 | Department Code | 部门唯一业务编号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | DEPT-001 |
| name | 部门名称 | Department Name | 部门中文名称 | — | String(100) | 是 | — | — | 技术研发部 |
| manager_id | 部门负责人 | Department Manager ID | 部门负责人 | 外键FK -> employees.id | Integer (FK) | — | — | — | 3 |
| sort_order | 排序号 | Sort Order | 同级排序，数值越小越靠前 | Integer，默认0 | Integer | 默认0 | — | — | 1 |
| status | 状态 | Status | 启用/禁用控制 | SAEnum枚举列，默认启用 | SAEnum | 默认启用 | dept_status_enum | — | 启用 |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 负责公司核心产品研发 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- belongs_to → CompanyEntity (via company_entity_id)
- has_many → Department (parent_id 自引用，下级子部门)
- belongs_to → Department (parent_id 自引用，上级部门)
- has_many → DepartmentRole (via department_id)
- has_many → Employee (via department_id)

---

## 实体 4：部门角色（DepartmentRole）

表名: `department_roles` | 模型路径: `app/models.py` | 阶段: Phase 2

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| department_id | 所属部门 | Belonging Department ID | 角色所属部门 | 外键FK -> departments.id | Integer (FK) | 是 | — | — | 1 |
| name | 角色名称 | Role Name | 角色中文名称 | — | String(50) | 是 | — | — | 项目经理 |
| role_code | 角色编码 | Role Code | 角色唯一业务编号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | ROLE-PM |
| description | 角色描述 | Role Description | 角色职责说明 | — | String(200) | — | — | — | 负责项目整体推进与交付 |
| status | 状态 | Status | 启用/禁用控制 | SAEnum枚举列，默认启用 | SAEnum | 默认启用 | role_status_enum | — | 启用 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- belongs_to → Department (via department_id)

---

## 实体 5：员工（Employee）

表名: `employees` | 模型路径: `app/models.py` | 阶段: Phase 3

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| employee_code | 工号 | Employee Code | 员工唯一工号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | EMP-001 |
| name | 姓名 | Full Name | 员工真实姓名 | — | String(50) | 是 | — | — | 李四 |
| gender | 性别 | Gender | 员工性别 | SAEnum枚举列 | SAEnum | — | gender_enum | — | 男 |
| phone | 手机号 | Phone Number | 员工个人手机号 | — | String(20) | 是 | — | — | 13800138000 |
| email | 邮箱 | Email | 员工企业或个人邮箱 | — | String(100) | — | — | — | lisi@oceanicmach.com |
| department_id | 所属部门 | Department ID | 员工当前部门 | 外键FK -> departments.id | Integer (FK) | 是 | — | — | 1 |
| position | 职位 | Position | 员工岗位名称 | — | String(50) | — | — | — | 高级工程师 |
| hire_date | 入职日期 | Hire Date | 首次入职日期 | Date类型 | Date | — | — | — | 2025-03-01 |
| status | 状态 | Status | 在职状态 | SAEnum枚举列，默认在职 | SAEnum | 默认在职 | employee_status_enum | — | 在职 |
| company_entity_id | 归属公司主体 | Belonging Company Entity ID | 劳动/合同所属法人主体 | 外键FK -> company_entities.id | Integer (FK) | — | — | — | 1 |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 核心研发人员 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- belongs_to → Department (via department_id)
- belongs_to → CompanyEntity (via company_entity_id)

---

## 实体 6：客户（Customer）

表名: `customers` | 模型路径: `app/models.py` | 阶段: Phase 4-5

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| customer_code | 客户编号 | Customer Code | 客户唯一业务编号 | 唯一约束String(20)，编码待定 | String(20) | 是 | — | — | CUST-001 |
| name | 客户全称 | Customer Full Name | 客户企业或个人全名 | — | String(200) | 是 | — | — | 华东钢铁集团 |
| short_name | 客户简称 | Short Name | 日常称呼简称 | — | String(100) | — | — | — | 华东钢铁 |
| customer_type | 客户类型 | Customer Type | 企业客户/个人客户 | SAEnum枚举列 | SAEnum | 是 | customer_type_enum | — | 企业客户 |
| credit_code | 统一社会信用代码 | Unified Social Credit Code | 企业客户18位信用代码 | — | String(18) | — | — | — | 91310115MA1H654321 |
| industry | 所属行业 | Industry | 客户所在行业 | — | String(50) | — | — | — | 钢铁制造 |
| customer_level | 客户等级 | Customer Level | A/B/C/D价值评级 | SAEnum枚举列，默认B | SAEnum | 默认B | customer_level_enum | — | A |
| status | 状态 | Status | 客户生命周期状态 | SAEnum枚举列，默认潜在 | SAEnum | 默认潜在 | customer_status_enum | — | 活跃 |
| source | 客户来源 | Customer Source | 客户获取渠道 | SAEnum枚举列 | SAEnum | — | customer_source_enum | — | 展会 |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 年度战略客户 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- has_many → CustomerContact (via customer_id)
- has_many → CustomerAddress (via customer_id)

---

## 实体 7：客户联系人（CustomerContact）

表名: `customer_contacts` | 模型路径: `app/models.py` | 阶段: Phase 4-5

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| customer_id | 所属客户 | Belonging Customer ID | 联系人归属客户 | 外键FK -> customers.id | Integer (FK) | 是 | — | — | 1 |
| name | 姓名 | Name | 联系人真实姓名 | — | String(50) | 是 | — | — | 王五 |
| title | 职务 | Job Title | 联系人在客户方职务 | — | String(50) | — | — | — | 采购经理 |
| phone | 手机号 | Phone Number | 联系人手机号 | — | String(20) | 是 | — | — | 13900139000 |
| email | 邮箱 | Email | 联系人企业邮箱 | — | String(100) | — | — | — | wangwu@hdsteel.com |
| is_default | 是否默认联系人 | Is Default Contact | 标记是否默认联系人 | Boolean，默认False | Boolean | 默认False | — | — | true |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 负责设备采购决策 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- belongs_to → Customer (via customer_id)

---

## 实体 8：客户收货地（CustomerAddress）

表名: `customer_addresses` | 模型路径: `app/models.py` | 阶段: Phase 4-5

| 字段名 | 中文描述 | 英文描述 | 业务含义 | 技术含义 | 类型 | 必填 | 选项集 | 主键 | 样例 |
|:--|:--|:--|:--|:--|:--|:--:|:--|:--:|:--|
| id | 主键ID | Primary Key ID | 记录唯一标识 | 自增整数主键 | Integer | 系统自动 | — | 是 | 1 |
| customer_id | 所属客户 | Belonging Customer ID | 收货地址归属客户 | 外键FK -> customers.id | Integer (FK) | 是 | — | — | 1 |
| address_name | 地址名称 | Address Name | 收货地业务标识 | — | String(100) | 是 | — | — | 华东钢铁总部仓库 |
| contact_person | 收货联系人 | Contact Person | 现场收货对接人 | — | String(50) | 是 | — | — | 赵六 |
| contact_phone | 联系电话 | Contact Phone | 对接人电话 | — | String(20) | 是 | — | — | 13700137000 |
| province | 省 | Province | 地址省份 | — | String(50) | — | — | — | 江苏省 |
| city | 市 | City | 地址城市 | — | String(50) | — | — | — | 南京市 |
| district | 区 | District | 地址区县 | — | String(50) | — | — | — | 鼓楼区 |
| detail_address | 详细地址 | Detailed Address | 街道门牌号等 | — | String(300) | 是 | — | — | XX工业园1号门 |
| is_default | 是否默认地址 | Is Default Address | 标记是否默认收货地址 | Boolean，默认False | Boolean | 默认False | — | — | true |
| remark | 备注 | Remark | 自由文本备注 | — | Text | — | — | — | 仅限工作日收货 |
| created_at | 创建时间 | Created At | 记录创建时间 | TimestampMixin自动填充 | DateTime | 系统自动 | — | — | 2026-01-15 10:30:00 |
| updated_at | 更新时间 | Updated At | 记录最后更新时间 | TimestampMixin自动刷新 | DateTime | 系统自动 | — | — | 2026-06-28 14:00:00 |

**关联关系**:
- belongs_to → Customer (via customer_id)

---

## 变更治理规则

见 `.codex/rules.md` 中的「实体变更治理规则」章节。
