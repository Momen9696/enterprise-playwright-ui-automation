"""HarborDesk HTTP application: HTML UI and a small JSON API for test setup."""

from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from demo_app import repository, services
from demo_app.constants import (
    CSRF_FAIL,
    FORBIDDEN_TEXT,
    NOTICES,
    PAGE_SIZE,
    PRIORITIES,
    PRIORITY_LABELS,
    STATUS_LABELS,
    STATUSES,
)
from demo_app.db import init_db
from demo_app.sessions import COOKIE_NAME, SessionStore
from demo_app.validation import parse_page

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
store = SessionStore(ttl_seconds=3600)

NOT_FOUND_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Not found</title></head>
<body><main><h1 data-testid="not-found">Page not found</h1></main></body></html>
"""


def hooks_enabled() -> bool:
    return os.environ.get("DEMO_ALLOW_TEST_HOOKS", "").lower() in {"1", "true", "yes"}


def tokens_match(expected: str, provided: str) -> bool:
    if not expected or not provided or len(expected) != len(provided):
        return False
    return hmac.compare_digest(expected, provided)


def render(request: Request, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
    payload = {**context, "request": request}
    return templates.TemplateResponse(request, name, payload, status_code=status_code)


def current_user(request: Request) -> dict | None:
    record = request.state.session
    if record is None or record.user_id is None:
        return None
    return repository.get_user(record.user_id)


def render_page(request: Request, name: str, status_code: int = 200, **extra) -> HTMLResponse:
    record = request.state.session
    return render(
        request,
        name,
        {
            "user": current_user(request),
            "csrf_token": record.csrf if record else "",
            "notice": NOTICES.get(request.query_params.get("notice", ""), ""),
            "statuses": STATUSES,
            "priorities": PRIORITIES,
            "status_labels": STATUS_LABELS,
            "priority_labels": PRIORITY_LABELS,
            "errors": {},
            **extra,
        },
        status_code,
    )


def redirect(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


def require_user(request: Request):
    user = current_user(request)
    if user:
        return user
    notice = "session_expired" if request.state.session_expired else "auth_required"
    return redirect(f"/login?notice={notice}")


def csrf_problem(request: Request, token: str, template: str, **extra) -> HTMLResponse | None:
    record = request.state.session
    expected = record.csrf if record else ""
    if tokens_match(expected, token):
        return None
    return render_page(
        request,
        template,
        status_code=400,
        errors={"form": CSRF_FAIL},
        **extra,
    )


def can_manage(user: dict, item: dict) -> bool:
    return user["role"] == "admin" or item["owner_id"] == user["id"]


def visible_owner(user: dict) -> int | None:
    if user["role"] == "admin":
        return None
    return user["id"]


def item_label(total: int) -> str:
    return "1 item" if total == 1 else f"{total} items"


def list_query(page: int, term: str, status: str, priority: str) -> str:
    return "/items?" + urlencode({"q": term, "status": status, "priority": priority, "page": page})


def clean_filter(value: str, allowed: tuple[str, ...]) -> str:
    return value if value in allowed else ""


class LoginIn(BaseModel):
    email: str = ""
    password: str = ""


class RegisterIn(BaseModel):
    name: str = ""
    email: str = ""
    password: str = ""


class ItemIn(BaseModel):
    title: str = ""
    description: str = ""
    status: str = "open"
    priority: str = "medium"


def json_errors(errors: dict[str, str], status_code: int) -> JSONResponse:
    return JSONResponse({"errors": errors}, status_code=status_code)


def api_user(request: Request) -> dict | None:
    return current_user(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    db_path = os.environ.get("DEMO_DB_PATH", str(Path(".run") / "harbordesk.sqlite"))
    ttl = int(os.environ.get("DEMO_SESSION_SECONDS", "3600"))
    store = SessionStore(ttl_seconds=ttl)
    init_db(db_path)
    repository.seed_if_empty()
    yield


app = FastAPI(title="HarborDesk", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id, record, expired = store.get(request.cookies.get(COOKIE_NAME))
    created = False
    if record is None and request.url.path != "/api/health":
        session_id, record = store.start()
        created = True
    request.state.session_id = session_id
    request.state.session = record
    request.state.session_expired = expired
    request.state.clear_session_cookie = expired
    response = await call_next(request)
    if request.state.clear_session_cookie:
        response.delete_cookie(COOKIE_NAME, path="/")
    elif created or getattr(request.state, "refresh_cookie", False):
        response.set_cookie(
            COOKIE_NAME,
            request.state.session_id,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=store.ttl_seconds,
        )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; img-src 'self' data:"
    )
    return response


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        if request.url.path.startswith("/api"):
            return json_errors({"form": "Not found."}, 404)
        return HTMLResponse(NOT_FOUND_HTML, status_code=404)
    return JSONResponse({"errors": {"form": exc.detail}}, status_code=exc.status_code)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root(request: Request):
    if current_user(request):
        return redirect("/dashboard")
    return redirect("/login")


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if current_user(request):
        return redirect("/dashboard")
    return render_page(request, "login.html")


@app.post("/login")
def login_submit(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    csrf_token: str = Form(""),
):
    problem = csrf_problem(request, csrf_token, "login.html", email_value=email)
    if problem:
        return problem
    errors, user = services.login_account(email, password)
    if errors:
        return render_page(
            request,
            "login.html",
            status_code=400,
            errors=errors,
            email_value=email,
        )
    request.state.session.user_id = user["id"]
    return redirect("/dashboard")


@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    if current_user(request):
        return redirect("/dashboard")
    return render_page(request, "register.html", values={"name": "", "email": ""})


@app.post("/register")
def register_submit(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    confirm: str = Form(""),
    csrf_token: str = Form(""),
):
    problem = csrf_problem(
        request,
        csrf_token,
        "register.html",
        values={"name": name, "email": email},
    )
    if problem:
        return problem
    errors, user = services.register_account(name, email, password, confirm, check_confirm=True)
    if errors:
        return render_page(
            request,
            "register.html",
            status_code=400,
            errors=errors,
            values={"name": name, "email": email},
        )
    request.state.session.user_id = user["id"]
    return redirect("/dashboard?notice=welcome")


@app.post("/logout")
def logout(request: Request, csrf_token: str = Form("")):
    problem = csrf_problem(request, csrf_token, "login.html")
    if problem:
        return problem
    store.destroy(request.state.session_id)
    request.state.session = None
    request.state.clear_session_cookie = True
    return redirect("/login?notice=logged_out")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    owner_id = visible_owner(user)
    counts = repository.status_counts(owner_id)
    recent, _total = repository.search_items(
        owner_id=owner_id,
        term="",
        status="",
        priority="",
        page=1,
        page_size=5,
    )
    return render_page(request, "dashboard.html", counts=counts, recent=recent)


@app.get("/profile", response_class=HTMLResponse)
def profile_form(request: Request):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    return render_page(request, "profile.html", name_value=user["name"])


@app.post("/profile")
def profile_submit(request: Request, name: str = Form(""), csrf_token: str = Form("")):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    if not tokens_match(request.state.session.csrf, csrf_token):
        return render_page(
            request,
            "profile.html",
            status_code=400,
            errors={"form": CSRF_FAIL},
            name_value=name,
        )
    errors, updated = services.update_profile(user["id"], name)
    if errors:
        return render_page(request, "profile.html", status_code=400, errors=errors, name_value=name)
    return redirect("/profile?notice=profile_saved") if updated else redirect("/login")


@app.get("/items", response_class=HTMLResponse)
def items_page(
    request: Request,
    q: str = "",
    status: str = "",
    priority: str = "",
    page: str = "1",
):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    selected_status = clean_filter(status, STATUSES)
    selected_priority = clean_filter(priority, PRIORITIES)
    current_page = parse_page(page)
    items, total = repository.search_items(
        owner_id=visible_owner(user),
        term=q.strip(),
        status=selected_status,
        priority=selected_priority,
        page=current_page,
        page_size=PAGE_SIZE,
    )
    pages = 1 if total == 0 else (total + PAGE_SIZE - 1) // PAGE_SIZE
    return render_page(
        request,
        "items.html",
        items=items,
        total=total,
        result_label=item_label(total),
        page=current_page,
        pages=pages,
        term=q,
        selected_status=selected_status,
        selected_priority=selected_priority,
        prev_url=list_query(current_page - 1, q, selected_status, selected_priority),
        next_url=list_query(current_page + 1, q, selected_status, selected_priority),
    )


def _item_form(
    request: Request,
    *,
    item: dict | None,
    values: dict | None = None,
    errors: dict | None = None,
    status_code: int = 200,
):
    form_values = (
        values
        or item
        or {
            "title": "",
            "description": "",
            "status": "open",
            "priority": "medium",
        }
    )
    action = "/items" if item is None else f"/items/{item['id']}"
    return render_page(
        request,
        "item_form.html",
        status_code=status_code,
        item=item,
        values=form_values,
        errors=errors or {},
        action=action,
        submit_label="Create item" if item is None else "Save changes",
        heading="New work item" if item is None else "Edit work item",
    )


@app.get("/items/new", response_class=HTMLResponse)
def new_item(request: Request):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    return _item_form(request, item=None)


@app.post("/items")
def create_item(
    request: Request,
    title: str = Form(""),
    description: str = Form(""),
    status: str = Form("open"),
    priority: str = Form("medium"),
    csrf_token: str = Form(""),
):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    fields = {"title": title, "description": description, "status": status, "priority": priority}
    if not tokens_match(request.state.session.csrf, csrf_token):
        return _item_form(
            request, item=None, values=fields, errors={"form": CSRF_FAIL}, status_code=400
        )
    errors, _item = services.save_item(user["id"], fields)
    if errors:
        return _item_form(request, item=None, values=fields, errors=errors, status_code=400)
    return redirect("/items?notice=created")


@app.get("/items/{item_id}/edit", response_class=HTMLResponse)
def edit_item(request: Request, item_id: int):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    item = repository.get_item(item_id)
    if item is None:
        return HTMLResponse(NOT_FOUND_HTML, status_code=404)
    if not can_manage(user, item):
        return render_page(request, "forbidden.html", status_code=403, message=FORBIDDEN_TEXT)
    return _item_form(request, item=item)


@app.post("/items/{item_id}")
def update_item(
    request: Request,
    item_id: int,
    title: str = Form(""),
    description: str = Form(""),
    status: str = Form("open"),
    priority: str = Form("medium"),
    csrf_token: str = Form(""),
):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    item = repository.get_item(item_id)
    if item is None:
        return HTMLResponse(NOT_FOUND_HTML, status_code=404)
    if not can_manage(user, item):
        return render_page(request, "forbidden.html", status_code=403, message=FORBIDDEN_TEXT)
    fields = {
        "id": item_id,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
    }
    if not tokens_match(request.state.session.csrf, csrf_token):
        return _item_form(
            request, item=item, values=fields, errors={"form": CSRF_FAIL}, status_code=400
        )
    errors, _updated = services.save_item(user["id"], fields, item_id=item_id)
    if errors:
        return _item_form(request, item=item, values=fields, errors=errors, status_code=400)
    return redirect("/items?notice=saved")


@app.post("/items/{item_id}/delete")
def delete_item(request: Request, item_id: int, csrf_token: str = Form("")):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    item = repository.get_item(item_id)
    if item is None:
        return HTMLResponse(NOT_FOUND_HTML, status_code=404)
    if not can_manage(user, item):
        return render_page(request, "forbidden.html", status_code=403, message=FORBIDDEN_TEXT)
    if not tokens_match(request.state.session.csrf, csrf_token):
        return _item_form(request, item=item, errors={"form": CSRF_FAIL}, status_code=400)
    repository.delete_item(item_id)
    return redirect("/items?notice=deleted")


@app.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request):
    user = require_user(request)
    if not isinstance(user, dict):
        return user
    if user["role"] != "admin":
        return render_page(request, "forbidden.html", status_code=403, message=FORBIDDEN_TEXT)
    return render_page(request, "admin_users.html", people=repository.list_users())


@app.post("/api/auth/register")
def api_register(payload: RegisterIn):
    errors, user = services.register_account(
        payload.name, payload.email, payload.password, check_confirm=False
    )
    if errors:
        return json_errors(errors, 422)
    return JSONResponse(user, status_code=201)


@app.post("/api/auth/login")
def api_login(request: Request, payload: LoginIn):
    errors, user = services.login_account(payload.email, payload.password)
    if errors.get("form"):
        return json_errors(errors, 401)
    if errors:
        return json_errors(errors, 422)
    request.state.session.user_id = user["id"]
    return user


@app.get("/api/items")
def api_list_items(
    request: Request,
    q: str = "",
    status: str = "",
    priority: str = "",
    page: str = "1",
):
    user = api_user(request)
    if user is None:
        return json_errors({"form": NOTICES["auth_required"]}, 401)
    current_page = parse_page(page)
    items, total = repository.search_items(
        owner_id=visible_owner(user),
        term=q.strip(),
        status=clean_filter(status, STATUSES),
        priority=clean_filter(priority, PRIORITIES),
        page=current_page,
        page_size=PAGE_SIZE,
    )
    return {"items": items, "total": total, "page": current_page}


@app.post("/api/items")
def api_create_item(request: Request, payload: ItemIn):
    user = api_user(request)
    if user is None:
        return json_errors({"form": NOTICES["auth_required"]}, 401)
    fields = payload.model_dump()
    errors, item = services.save_item(user["id"], fields)
    if errors:
        return json_errors(errors, 422)
    return JSONResponse(item, status_code=201)


@app.put("/api/items/{item_id}")
def api_update_item(request: Request, item_id: int, payload: ItemIn):
    user = api_user(request)
    if user is None:
        return json_errors({"form": NOTICES["auth_required"]}, 401)
    item = repository.get_item(item_id)
    if item is None:
        return json_errors({"form": "Not found."}, 404)
    if not can_manage(user, item):
        return json_errors({"form": FORBIDDEN_TEXT}, 403)
    errors, updated = services.save_item(user["id"], payload.model_dump(), item_id=item_id)
    if errors:
        return json_errors(errors, 422)
    return updated


@app.delete("/api/items/{item_id}")
def api_delete_item(request: Request, item_id: int):
    user = api_user(request)
    if user is None:
        return json_errors({"form": NOTICES["auth_required"]}, 401)
    item = repository.get_item(item_id)
    if item is None:
        return json_errors({"form": "Not found."}, 404)
    if not can_manage(user, item):
        return json_errors({"form": FORBIDDEN_TEXT}, 403)
    repository.delete_item(item_id)
    return {"deleted": item_id}


@app.post("/api/test/expire-session")
def api_expire(request: Request):
    if not hooks_enabled():
        return json_errors({"form": "Not found."}, 404)
    expired = store.expire(request.cookies.get(COOKIE_NAME))
    return {"expired": expired}


@app.post("/api/test/reset")
def api_reset():
    if not hooks_enabled():
        return json_errors({"form": "Not found."}, 404)
    repository.reset_and_seed()
    store.clear()
    return {"reset": True}
