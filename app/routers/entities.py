from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from app.database import SessionLocal
from app.models import CompanyEntity
from app.config import settings
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/company-entities", tags=["entities"])
env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def entity_list(request: Request, search: str = "", status: str = "", page: int = 1):
    db = SessionLocal()
    query = select(CompanyEntity)
    if search:
        query = query.where(
            (CompanyEntity.entity_code.contains(search)) | (CompanyEntity.name.contains(search))
        )
    if status:
        query = query.where(CompanyEntity.status == status)

    total = db.execute(query).scalars().all()
    per_page = 15
    offset = (page - 1) * per_page
    entities = total[offset:offset + per_page]
    total_pages = (len(total) + per_page - 1) // per_page
    db.close()

    template = env.get_template("entities/list.html")
    return HTMLResponse(template.render(
        entities=entities, search=search, status=status,
        page=page, total_pages=total_pages, total=len(total)
    ))


@router.get("/new", response_class=HTMLResponse)
async def entity_new_form():
    template = env.get_template("entities/form.html")
    return HTMLResponse(template.render(entity=None))


@router.get("/{id}/edit", response_class=HTMLResponse)
async def entity_edit_form(id: int):
    db = SessionLocal()
    entity = db.get(CompanyEntity, id)
    db.close()
    if not entity:
        raise HTTPException(status_code=404)
    template = env.get_template("entities/form.html")
    return HTMLResponse(template.render(entity=entity))


@router.post("/save")
async def entity_save(
    request: Request,
    id: int = Form(None),
    entity_code: str = Form(...), name: str = Form(...),
    short_name: str = Form(""), credit_code: str = Form(""),
    legal_representative: str = Form(""), registered_address: str = Form(""),
    contact_phone: str = Form(""), entity_type: str = Form(...),
    status: str = Form("启用"), remark: str = Form("")
):
    db = SessionLocal()
    if id:
        entity = db.get(CompanyEntity, id)
        if not entity:
            db.close()
            raise HTTPException(status_code=404)
    else:
        entity = CompanyEntity()
        db.add(entity)

    entity.entity_code = entity_code
    entity.name = name
    entity.short_name = short_name
    entity.credit_code = credit_code
    entity.legal_representative = legal_representative
    entity.registered_address = registered_address
    entity.contact_phone = contact_phone
    entity.entity_type = entity_type
    entity.status = status
    entity.remark = remark
    db.commit()
    db.close()
    return RedirectResponse(url="/company-entities", status_code=303)


@router.get("/{id}/delete")
async def entity_delete(id: int):
    db = SessionLocal()
    entity = db.get(CompanyEntity, id)
    if entity:
        db.delete(entity)
        db.commit()
    db.close()
    return RedirectResponse(url="/company-entities", status_code=303)
