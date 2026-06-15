from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Customer, CustomerContact, CustomerAddress
from app.config import settings
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/customers", tags=["customers"])
env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def customer_list(request: Request, search: str = "", customer_type: str = "", status: str = "", page: int = 1):
    db = SessionLocal()
    query = select(Customer)
    if search:
        query = query.where(
            (Customer.customer_code.contains(search)) | (Customer.name.contains(search))
        )
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    if status:
        query = query.where(Customer.status == status)

    total = db.execute(query).scalars().all()
    per_page = 15
    offset = (page - 1) * per_page
    customers = total[offset:offset + per_page]
    total_pages = (len(total) + per_page - 1) // per_page
    db.close()

    template = env.get_template("customers/list.html")
    return HTMLResponse(template.render(
        customers=customers, search=search, customer_type=customer_type, status=status,
        page=page, total_pages=total_pages, total=len(total)
    ))


@router.get("/new", response_class=HTMLResponse)
async def customer_new_form():
    template = env.get_template("customers/form.html")
    return HTMLResponse(template.render(customer=None))


@router.get("/{id}/edit", response_class=HTMLResponse)
async def customer_edit_form(id: int):
    db = SessionLocal()
    customer = db.get(Customer, id)
    db.close()
    if not customer:
        raise HTTPException(status_code=404)
    template = env.get_template("customers/form.html")
    return HTMLResponse(template.render(customer=customer))


@router.post("/save")
async def customer_save(
    id: int = Form(None),
    customer_code: str = Form(...), name: str = Form(...),
    short_name: str = Form(""), customer_type: str = Form(...),
    credit_code: str = Form(""), industry: str = Form(""),
    customer_level: str = Form("B"), status: str = Form("潜在"),
    source: str = Form(""), remark: str = Form("")
):
    db = SessionLocal()
    if id:
        cust = db.get(Customer, id)
        if not cust:
            db.close()
            raise HTTPException(status_code=404)
    else:
        cust = Customer()
        db.add(cust)

    cust.customer_code = customer_code
    cust.name = name
    cust.short_name = short_name if short_name else None
    cust.customer_type = customer_type
    cust.credit_code = credit_code if credit_code else None
    cust.industry = industry if industry else None
    cust.customer_level = customer_level
    cust.status = status
    cust.source = source if source else None
    cust.remark = remark if remark else None
    db.commit()
    db.close()
    return RedirectResponse(url="/customers", status_code=303)


@router.get("/{id}/delete")
async def customer_delete(id: int):
    db = SessionLocal()
    cust = db.get(Customer, id)
    if cust:
        db.delete(cust)
        db.commit()
    db.close()
    return RedirectResponse(url="/customers", status_code=303)


# --- Customer Detail (Tabs: info, contacts, addresses) ---

@router.get("/{id}", response_class=HTMLResponse)
async def customer_detail(id: int, tab: str = "info"):
    db = SessionLocal()
    cust = db.get(Customer, id)
    if not cust:
        db.close()
        raise HTTPException(status_code=404)
    contacts = db.execute(
        select(CustomerContact).where(CustomerContact.customer_id == id)
    ).scalars().all()
    addresses = db.execute(
        select(CustomerAddress).where(CustomerAddress.customer_id == id)
    ).scalars().all()
    db.close()

    template = env.get_template("customers/detail.html")
    return HTMLResponse(template.render(customer=cust, contacts=contacts, addresses=addresses, tab=tab))


@router.post("/{cust_id}/contacts/save")
async def contact_save(
    cust_id: int,
    id: int = Form(None),
    name: str = Form(...), title: str = Form(""),
    phone: str = Form(...), email: str = Form(""),
    is_default: bool = Form(False), remark: str = Form("")
):
    db = SessionLocal()
    if id:
        contact = db.get(CustomerContact, id)
        if not contact:
            db.close()
            raise HTTPException(status_code=404)
    else:
        contact = CustomerContact(customer_id=cust_id)
        db.add(contact)
    contact.name = name
    contact.title = title if title else None
    contact.phone = phone
    contact.email = email if email else None
    contact.is_default = is_default
    contact.remark = remark if remark else None
    db.commit()
    db.close()
    return RedirectResponse(url=f"/customers/{cust_id}?tab=contacts", status_code=303)


@router.get("/{cust_id}/contacts/{contact_id}/delete")
async def contact_delete(cust_id: int, contact_id: int):
    db = SessionLocal()
    contact = db.get(CustomerContact, contact_id)
    if contact:
        db.delete(contact)
        db.commit()
    db.close()
    return RedirectResponse(url=f"/customers/{cust_id}?tab=contacts", status_code=303)


@router.post("/{cust_id}/addresses/save")
async def address_save(
    cust_id: int,
    id: int = Form(None),
    address_name: str = Form(...), contact_person: str = Form(...),
    contact_phone: str = Form(...), province: str = Form(""),
    city: str = Form(""), district: str = Form(""),
    detail_address: str = Form(...),
    is_default: bool = Form(False), remark: str = Form("")
):
    db = SessionLocal()
    if id:
        addr = db.get(CustomerAddress, id)
        if not addr:
            db.close()
            raise HTTPException(status_code=404)
    else:
        addr = CustomerAddress(customer_id=cust_id)
        db.add(addr)
    addr.address_name = address_name
    addr.contact_person = contact_person
    addr.contact_phone = contact_phone
    addr.province = province if province else None
    addr.city = city if city else None
    addr.district = district if district else None
    addr.detail_address = detail_address
    addr.is_default = is_default
    addr.remark = remark if remark else None
    db.commit()
    db.close()
    return RedirectResponse(url=f"/customers/{cust_id}?tab=addresses", status_code=303)


@router.get("/{cust_id}/addresses/{address_id}/delete")
async def address_delete(cust_id: int, address_id: int):
    db = SessionLocal()
    addr = db.get(CustomerAddress, address_id)
    if addr:
        db.delete(addr)
        db.commit()
    db.close()
    return RedirectResponse(url=f"/customers/{cust_id}?tab=addresses", status_code=303)
