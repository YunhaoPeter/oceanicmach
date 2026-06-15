from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from app.database import SessionLocal
from app.models import Product
from app.config import settings
from jinja2 import Environment, FileSystemLoader

router = APIRouter(prefix="/products", tags=["products"])
env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def product_list(request: Request, search: str = "", category: str = "", status: str = "", page: int = 1):
    db = SessionLocal()
    query = select(Product)
    if search:
        query = query.where(
            (Product.product_code.contains(search)) | (Product.name.contains(search))
        )
    if category:
        query = query.where(Product.category == category)
    if status:
        query = query.where(Product.status == status)

    total = db.execute(query).scalars().all()
    per_page = 15
    offset = (page - 1) * per_page
    products = total[offset:offset + per_page]
    total_pages = (len(total) + per_page - 1) // per_page
    db.close()

    template = env.get_template("products/list.html")
    return HTMLResponse(template.render(
        products=products, search=search, category=category, status=status,
        page=page, total_pages=total_pages, total=len(total)
    ))


@router.get("/new", response_class=HTMLResponse)
async def product_new_form():
    template = env.get_template("products/form.html")
    return HTMLResponse(template.render(product=None))


@router.get("/{id}/edit", response_class=HTMLResponse)
async def product_edit_form(id: int):
    db = SessionLocal()
    product = db.get(Product, id)
    db.close()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    template = env.get_template("products/form.html")
    return HTMLResponse(template.render(product=product))


@router.post("/save")
async def product_save(
    request: Request,
    id: int = Form(None),
    product_code: str = Form(...), name: str = Form(...),
    model: str = Form(""), category: str = Form(...),
    specification: str = Form(""), unit: str = Form(...),
    sales_price: float = Form(None), cost_price: float = Form(None),
    tax_rate: float = Form(13.0), status: str = Form("在售"),
    remark: str = Form("")
):
    db = SessionLocal()
    if id:
        product = db.get(Product, id)
        if not product:
            db.close()
            raise HTTPException(status_code=404)
    else:
        product = Product()
        db.add(product)

    product.product_code = product_code
    product.name = name
    product.model = model
    product.category = category
    product.specification = specification
    product.unit = unit
    product.sales_price = sales_price
    product.cost_price = cost_price
    product.tax_rate = tax_rate
    product.status = status
    product.remark = remark
    db.commit()
    db.close()
    return RedirectResponse(url="/products", status_code=303)


@router.get("/{id}/delete")
async def product_delete(id: int):
    db = SessionLocal()
    product = db.get(Product, id)
    if product:
        db.delete(product)
        db.commit()
    db.close()
    return RedirectResponse(url="/products", status_code=303)
