from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Employee, Department, CompanyEntity
from app.config import settings
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/employees", tags=["employees"])
env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def employee_list(request: Request, search: str = "", department_id: str = "", status: str = "", page: int = 1):
    db = SessionLocal()
    query = select(Employee)
    if search:
        query = query.where(
            (Employee.employee_code.contains(search)) | (Employee.name.contains(search))
        )
    if department_id:
        query = query.where(Employee.department_id == int(department_id))
    if status:
        query = query.where(Employee.status == status)

    total = db.execute(query).scalars().all()
    per_page = 15
    offset = (page - 1) * per_page
    employees = total[offset:offset + per_page]
    total_pages = (len(total) + per_page - 1) // per_page

    departments = db.execute(select(Department).where(Department.status == "启用")).scalars().all()
    db.close()

    template = env.get_template("employees/list.html")
    return HTMLResponse(template.render(
        employees=employees, departments=departments, search=search,
        department_id=department_id, status=status,
        page=page, total_pages=total_pages, total=len(total)
    ))


@router.get("/new", response_class=HTMLResponse)
async def employee_new_form():
    db = SessionLocal()
    departments = db.execute(select(Department).where(Department.status == "启用")).scalars().all()
    entities = db.execute(select(CompanyEntity).where(CompanyEntity.status == "启用")).scalars().all()
    db.close()
    template = env.get_template("employees/form.html")
    return HTMLResponse(template.render(employee=None, departments=departments, entities=entities))


@router.get("/{id}/edit", response_class=HTMLResponse)
async def employee_edit_form(id: int):
    db = SessionLocal()
    employee = db.get(Employee, id)
    if not employee:
        db.close()
        raise HTTPException(status_code=404)
    departments = db.execute(select(Department).where(Department.status == "启用")).scalars().all()
    entities = db.execute(select(CompanyEntity).where(CompanyEntity.status == "启用")).scalars().all()
    db.close()
    template = env.get_template("employees/form.html")
    return HTMLResponse(template.render(employee=employee, departments=departments, entities=entities))


@router.post("/save")
async def employee_save(
    id: int = Form(None),
    employee_code: str = Form(...), name: str = Form(...),
    gender: str = Form(""), phone: str = Form(...),
    email: str = Form(""), department_id: int = Form(...),
    position: str = Form(""), hire_date: str = Form(""),
    status: str = Form("在职"),
    company_entity_id: int = Form(None),
    remark: str = Form("")
):
    db = SessionLocal()
    if id:
        emp = db.get(Employee, id)
        if not emp:
            db.close()
            raise HTTPException(status_code=404)
    else:
        emp = Employee()
        db.add(emp)

    emp.employee_code = employee_code
    emp.name = name
    emp.gender = gender if gender else None
    emp.phone = phone
    emp.email = email if email else None
    emp.department_id = department_id
    emp.position = position if position else None
    emp.hire_date = hire_date if hire_date else None
    emp.status = status
    emp.company_entity_id = company_entity_id
    emp.remark = remark if remark else None
    db.commit()
    db.close()
    return RedirectResponse(url="/employees", status_code=303)


@router.get("/{id}/delete")
async def employee_delete(id: int):
    db = SessionLocal()
    emp = db.get(Employee, id)
    if emp:
        db.delete(emp)
        db.commit()
    db.close()
    return RedirectResponse(url="/employees", status_code=303)
