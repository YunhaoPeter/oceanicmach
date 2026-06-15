from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Department, DepartmentRole, CompanyEntity, Employee
from app.config import settings
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/departments", tags=["departments"])
env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


def _build_tree(depts):
    """把扁平列表转成树形结构，每个节点额外带 level 用于缩进"""
    by_id = {}
    roots = []
    for d in sorted(depts, key=lambda x: (x.sort_order or 0, x.department_code)):
        d._children = []
        by_id[d.id] = d
    for d in sorted(depts, key=lambda x: (x.sort_order or 0, x.department_code)):
        if d.parent_id and d.parent_id in by_id:
            by_id[d.parent_id]._children.append(d)
        else:
            roots.append(d)
    result = []
    def walk(nodes, level):
        for n in nodes:
            n._level = level
            result.append(n)
            walk(n._children, level + 1)
    walk(roots, 0)
    return result


@router.get("/", response_class=HTMLResponse)
async def department_list(request: Request, search: str = "", status: str = ""):
    db = SessionLocal()
    query = select(Department).order_by(Department.sort_order, Department.department_code)
    if search:
        query = query.where(Department.name.contains(search))
    if status:
        query = query.where(Department.status == status)
    depts = db.execute(query).scalars().all()

    # For the tree view, we need all departments (for parent lookup)
    all_depts = db.execute(select(Department).order_by(Department.sort_order, Department.department_code)).scalars().all()
    tree = _build_tree(all_depts)

    # Get all company entities for the filter/form
    entities = db.execute(select(CompanyEntity).where(CompanyEntity.status == "启用")).scalars().all()
    db.close()

    template = env.get_template("departments/list.html")
    return HTMLResponse(template.render(
        departments=tree, search=search, status=status, entities=entities
    ))


@router.get("/new", response_class=HTMLResponse)
async def department_new_form():
    db = SessionLocal()
    depts = db.execute(select(Department).order_by(Department.sort_order, Department.department_code)).scalars().all()
    entities = db.execute(select(CompanyEntity).where(CompanyEntity.status == "启用")).scalars().all()
    db.close()
    tree = _build_tree(depts)
    template = env.get_template("departments/form.html")
    return HTMLResponse(template.render(department=None, departments=tree, entities=entities))


@router.get("/{id}/edit", response_class=HTMLResponse)
async def department_edit_form(id: int):
    db = SessionLocal()
    department = db.get(Department, id)
    if not department:
        db.close()
        raise HTTPException(status_code=404)
    depts = db.execute(select(Department).order_by(Department.sort_order, Department.department_code)).scalars().all()
    entities = db.execute(select(CompanyEntity).where(CompanyEntity.status == "启用")).scalars().all()
    db.close()
    tree = _build_tree(depts)
    template = env.get_template("departments/form.html")
    return HTMLResponse(template.render(department=department, departments=tree, entities=entities))


@router.post("/save")
async def department_save(
    id: int = Form(None),
    company_entity_id: int = Form(...),
    parent_id: str = Form(""),
    department_code: str = Form(...),
    name: str = Form(...),
    sort_order: int = Form(0),
    status: str = Form("启用"),
    remark: str = Form("")
):
    db = SessionLocal()
    if id:
        dept = db.get(Department, id)
        if not dept:
            db.close()
            raise HTTPException(status_code=404)
    else:
        dept = Department()
        db.add(dept)

    dept.company_entity_id = company_entity_id
    dept.parent_id = int(parent_id) if parent_id and parent_id != "0" else None
    dept.department_code = department_code
    dept.name = name
    dept.sort_order = sort_order
    dept.status = status
    dept.remark = remark
    db.commit()
    db.close()
    return RedirectResponse(url="/departments", status_code=303)


@router.get("/{id}/delete")
async def department_delete(id: int):
    db = SessionLocal()
    dept = db.get(Department, id)
    if dept:
        db.delete(dept)
        db.commit()
    db.close()
    return RedirectResponse(url="/departments", status_code=303)


# --- Department Roles ---

@router.get("/{dept_id}/roles", response_class=HTMLResponse)
async def role_list(request: Request, dept_id: int):
    db = SessionLocal()
    dept = db.get(Department, dept_id)
    if not dept:
        db.close()
        raise HTTPException(status_code=404)
    roles = db.execute(
        select(DepartmentRole).where(DepartmentRole.department_id == dept_id)
    ).scalars().all()
    db.close()
    template = env.get_template("departments/roles.html")
    return HTMLResponse(template.render(department=dept, roles=roles))


@router.post("/{dept_id}/roles/save")
async def role_save(
    dept_id: int,
    id: int = Form(None),
    role_code: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    status: str = Form("启用")
):
    db = SessionLocal()
    if id:
        role = db.get(DepartmentRole, id)
        if not role:
            db.close()
            raise HTTPException(status_code=404)
    else:
        role = DepartmentRole(department_id=dept_id)
        db.add(role)

    role.role_code = role_code
    role.name = name
    role.description = description
    role.status = status
    db.commit()
    db.close()
    return RedirectResponse(url=f"/departments/{dept_id}/roles", status_code=303)


@router.get("/{dept_id}/roles/{role_id}/delete")
async def role_delete(dept_id: int, role_id: int):
    db = SessionLocal()
    role = db.get(DepartmentRole, role_id)
    if role:
        db.delete(role)
        db.commit()
    db.close()
    return RedirectResponse(url=f"/departments/{dept_id}/roles", status_code=303)
