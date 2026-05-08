"""
Items API — FastAPI + SQLite implementation.
Matches the OpenAPI spec at postman/specs/items-api.yaml exactly.

Run:
    uvicorn main:app --reload --port 3000
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DB_PATH = Path("items.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enforce foreign-key constraints and return proper dict-like rows
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the items table if it does not already exist."""
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sku         TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL,
                description TEXT
            )
            """
        )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: Optional[str] = None


class ItemCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None


class ItemPatch(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class ItemList(BaseModel):
    total: int
    next: Optional[str] = None
    prev: Optional[str] = None
    items: list[ItemOut]


class ErrorOut(BaseModel):
    code: int
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def row_to_item(row: sqlite3.Row) -> ItemOut:
    return ItemOut(
        id=row["id"],
        sku=row["sku"],
        name=row["name"],
        description=row["description"],
    )


def fetch_item_or_404(conn: sqlite3.Connection, item_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "Item not found."},
        )
    return row


def build_page_url(request: Request, page: int, size: int) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/items?page={page}&size={size}"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Items API",
    version="1.0.0",
    description="A RESTful API for managing Item resources with full CRUD operations.",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# Override FastAPI's default 422 validation error shape to match the spec's
# Error schema: { code, message }.
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "Invalid request body."},
    )


# HTTPException handler so { code, message } is always returned.
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(detail)},
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/items", response_model=ItemList, status_code=200)
def list_items(
    request: Request,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(default=20, ge=1, le=100, description="Number of items per page"),
):
    """GET /items — paginated list."""
    offset = (page - 1) * size

    with db() as conn:
        total: int = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        rows = conn.execute(
            "SELECT * FROM items ORDER BY id LIMIT ? OFFSET ?", (size, offset)
        ).fetchall()

    items = [row_to_item(r) for r in rows]

    next_url = build_page_url(request, page + 1, size) if offset + size < total else None
    prev_url = build_page_url(request, page - 1, size) if page > 1 else None

    return ItemList(total=total, next=next_url, prev=prev_url, items=items)


@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(body: ItemCreate):
    """POST /items — create a new item."""
    with db() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO items (sku, name, description) VALUES (?, ?, ?)",
                (body.sku, body.name, body.description),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail={"code": 409, "message": f"An item with sku '{body.sku}' already exists."},
            )
        row = conn.execute(
            "SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return row_to_item(row)


@app.get("/items/{id}", response_model=ItemOut, status_code=200)
def get_item(id: int):
    """GET /items/{id} — retrieve a single item."""
    with db() as conn:
        row = fetch_item_or_404(conn, id)
    return row_to_item(row)


@app.put("/items/{id}", response_model=ItemOut, status_code=200)
def replace_item(id: int, body: ItemCreate):
    """PUT /items/{id} — fully replace an item."""
    with db() as conn:
        fetch_item_or_404(conn, id)  # 404 if not found
        try:
            conn.execute(
                "UPDATE items SET sku = ?, name = ?, description = ? WHERE id = ?",
                (body.sku, body.name, body.description, id),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail={"code": 409, "message": f"An item with sku '{body.sku}' already exists."},
            )
        row = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()

    return row_to_item(row)


@app.patch("/items/{id}", response_model=ItemOut, status_code=200)
def update_item(id: int, body: ItemPatch):
    """PATCH /items/{id} — partially update an item."""
    with db() as conn:
        fetch_item_or_404(conn, id)  # 404 if not found

        # Build SET clause only for fields that were explicitly provided
        updates = body.model_dump(exclude_unset=True)
        if not updates:
            # Nothing to update — return the item as-is
            row = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
            return row_to_item(row)

        set_clause = ", ".join(f"{col} = ?" for col in updates)
        values = list(updates.values()) + [id]

        try:
            conn.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=409,
                detail={"code": 409, "message": f"An item with sku '{updates.get('sku')}' already exists."},
            )
        row = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()

    return row_to_item(row)


@app.delete("/items/{id}", status_code=204)
def delete_item(id: int):
    """DELETE /items/{id} — delete an item, return 204 No Content."""
    with db() as conn:
        fetch_item_or_404(conn, id)  # 404 if not found
        conn.execute("DELETE FROM items WHERE id = ?", (id,))

    return Response(status_code=204)
