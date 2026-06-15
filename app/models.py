from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Date, DateTime,
    Numeric, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


# ============================================================
# Phase 1: 无依赖的独立实体 — 公司主体、产品
# ============================================================

class CompanyEntity(Base, TimestampMixin):
    __tablename__ = "company_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_code = Column(String(20), unique=True, nullable=False, comment="主体编码")
    name = Column(String(200), nullable=False, comment="主体全称")
    short_name = Column(String(100), comment="简称")
    credit_code = Column(String(18), comment="统一社会信用代码")
    legal_representative = Column(String(50), comment="法定代表人")
    registered_address = Column(String(300), comment="注册地址")
    contact_phone = Column(String(20), comment="联系电话")
    entity_type = Column(
        SAEnum("母公司", "子公司", "分公司", "办事处", name="entity_type_enum"),
        nullable=False, comment="主体类型"
    )
    status = Column(
        SAEnum("启用", "禁用", name="entity_status_enum"),
        default="启用", nullable=False
    )
    remark = Column(Text, comment="备注")

    departments = relationship("Department", back_populates="company_entity")
    employees = relationship("Employee", back_populates="company_entity")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_code = Column(String(20), unique=True, nullable=False, comment="产品编码")
    name = Column(String(200), nullable=False, comment="产品名称")
    model = Column(String(100), comment="产品型号")
    category = Column(
        SAEnum("成品", "半成品", "原材料", "服务", name="product_category_enum"),
        nullable=False, comment="产品分类"
    )
    specification = Column(String(200), comment="规格描述")
    unit = Column(
        SAEnum("个", "台", "套", "件", "m", "t", "L", name="product_unit_enum"),
        nullable=False, comment="计量单位"
    )
    sales_price = Column(Numeric(12, 2), comment="标准售价")
    cost_price = Column(Numeric(12, 2), comment="成本价")
    tax_rate = Column(Numeric(4, 2), default=13.00, comment="税率(%)")
    status = Column(
        SAEnum("在售", "停产", "研发中", name="product_status_enum"),
        default="在售", nullable=False
    )
    remark = Column(Text, comment="备注")


# ============================================================
# Phase 2: 部门、部门角色 (依赖公司主体)
# ============================================================

class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_entity_id = Column(Integer, ForeignKey("company_entities.id"), nullable=False, comment="归属公司主体")
    parent_id = Column(Integer, ForeignKey("departments.id"), comment="上级部门(自引用)")
    department_code = Column(String(20), unique=True, nullable=False, comment="部门编码")
    name = Column(String(100), nullable=False, comment="部门名称")
    manager_id = Column(Integer, ForeignKey("employees.id"), comment="部门负责人")
    sort_order = Column(Integer, default=0, comment="排序号")
    status = Column(
        SAEnum("启用", "禁用", name="dept_status_enum"),
        default="启用", nullable=False
    )
    remark = Column(Text, comment="备注")

    company_entity = relationship("CompanyEntity", back_populates="departments")
    parent = relationship("Department", remote_side=[id], backref="children")
    manager = relationship("Employee", foreign_keys=[manager_id], post_update=True)
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")
    roles = relationship("DepartmentRole", back_populates="department")


class DepartmentRole(Base, TimestampMixin):
    __tablename__ = "department_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, comment="所属部门")
    name = Column(String(50), nullable=False, comment="角色名称")
    role_code = Column(String(20), unique=True, nullable=False, comment="角色编码")
    description = Column(String(200), comment="角色描述")
    status = Column(
        SAEnum("启用", "禁用", name="role_status_enum"),
        default="启用", nullable=False
    )

    department = relationship("Department", back_populates="roles")


# ============================================================
# Phase 3: 员工 (依赖部门、公司主体)
# ============================================================

class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_code = Column(String(20), unique=True, nullable=False, comment="工号")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(
        SAEnum("男", "女", name="gender_enum"),
        comment="性别"
    )
    phone = Column(String(20), nullable=False, comment="手机号")
    email = Column(String(100), comment="邮箱")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, comment="所属部门")
    position = Column(String(50), comment="职位")
    hire_date = Column(Date, comment="入职日期")
    status = Column(
        SAEnum("在职", "离职", "试用期", name="employee_status_enum"),
        default="在职", nullable=False
    )
    company_entity_id = Column(Integer, ForeignKey("company_entities.id"), comment="归属公司主体")
    remark = Column(Text, comment="备注")

    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    company_entity = relationship("CompanyEntity", back_populates="employees")


# ============================================================
# Phase 4-5: 客户、联系人、收货地
# ============================================================

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_code = Column(String(20), unique=True, nullable=False, comment="客户编号")
    name = Column(String(200), nullable=False, comment="客户全称")
    short_name = Column(String(100), comment="客户简称")
    customer_type = Column(
        SAEnum("企业客户", "个人客户", name="customer_type_enum"),
        nullable=False, comment="客户类型"
    )
    credit_code = Column(String(18), comment="统一社会信用代码")
    industry = Column(String(50), comment="所属行业")
    customer_level = Column(
        SAEnum("A", "B", "C", "D", name="customer_level_enum"),
        default="B", nullable=False, comment="客户等级"
    )
    status = Column(
        SAEnum("潜在", "活跃", "休眠", "黑名单", name="customer_status_enum"),
        default="潜在", nullable=False
    )
    source = Column(
        SAEnum("官网", "展会", "转介绍", "自主开发", name="customer_source_enum"),
        comment="客户来源"
    )
    remark = Column(Text, comment="备注")

    contacts = relationship("CustomerContact", back_populates="customer")
    addresses = relationship("CustomerAddress", back_populates="customer")


class CustomerContact(Base, TimestampMixin):
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, comment="所属客户")
    name = Column(String(50), nullable=False, comment="姓名")
    title = Column(String(50), comment="职务")
    phone = Column(String(20), nullable=False, comment="手机号")
    email = Column(String(100), comment="邮箱")
    is_default = Column(Boolean, default=False, comment="是否默认联系人")
    remark = Column(Text, comment="备注")

    customer = relationship("Customer", back_populates="contacts")


class CustomerAddress(Base, TimestampMixin):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, comment="所属客户")
    address_name = Column(String(100), nullable=False, comment="地址名称")
    contact_person = Column(String(50), nullable=False, comment="收货联系人")
    contact_phone = Column(String(20), nullable=False, comment="联系电话")
    province = Column(String(50), comment="省")
    city = Column(String(50), comment="市")
    district = Column(String(50), comment="区")
    detail_address = Column(String(300), nullable=False, comment="详细地址")
    is_default = Column(Boolean, default=False, comment="是否默认地址")
    remark = Column(Text, comment="备注")

    customer = relationship("Customer", back_populates="addresses")
