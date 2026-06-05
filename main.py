"""
Items API — FastAPI + SQLite single-file implementation.
Matches the OpenAPI 3.0.3 spec at postman/specs/items-api.yaml.

Run:
    uvicorn main:app --reload
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# App & database setup
# ---------------------------------------------------------------------------

DB_FILE = "items.db"

app = FastAPI(
    title="Items API",
    version="1.0.0",
    description="CRUD API for managing items",
)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys and return dicts
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def db_conn():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the items table if it does not exist."""
    with db_conn() as conn:
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


# Initialise on startup
init_db()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ItemOut(BaseModel):
    id: int
    sku: str
    name: str
    description: Optional[str] = None


class ItemInput(BaseModel):
    sku: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., description="Name of the item")
    description: Optional[str] = Field(None, description="Optional description")


class ItemPatch(BaseModel):
    sku: Optional[str] = Field(None, description="Unique identifier for the item")
    name: Optional[str] = Field(None, description="Name of the item")
    description: Optional[str] = Field(None, description="Optional description")


class PaginatedItems(BaseModel):
    total: int
    next: Optional[str]
    prev: Optional[str]
    items: list[ItemOut]


class ErrorResponse(BaseModel):
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


def build_page_url(req: Request, page: int, size: int) -> str:
    base = str(req.base_url).rstrip("/")
    return f"{base}/api/v1/items?page={page}&size={size}"


def not_found(item_id: int) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": 404, "message": f"Item with id {item_id} not found"},
    )


def sku_conflict(sku: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={"code": 409, "message": f"An item with sku '{sku}' already exists"},
    )


# ---------------------------------------------------------------------------
# Custom error response shape — match the spec's Error schema
# ---------------------------------------------------------------------------

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
# Routes — mounted under /api/v1 to match the spec's server URL
# ---------------------------------------------------------------------------

PREFIX = "/api/v1"


@app.get(
    f"{PREFIX}/items",
    response_model=PaginatedItems,
    summary="List items",
    tags=["Items"],
)
def list_items(
    request: Request,
    page: int = 1,
    size: int = 20,
):
    if page < 1:
        raise HTTPException(status_code=422, detail={"code": 422, "message": "'page' must be >= 1"})
    if size < 1:
        raise HTTPException(status_code=422, detail={"code": 422, "message": "'size' must be >= 1"})

    offset = (page - 1) * size

    with db_conn() as conn:
        total: int = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        rows = conn.execute(
            "SELECT id, sku, name, description FROM items ORDER BY id LIMIT ? OFFSET ?",
            (size, offset),
        ).fetchall()

    items = [row_to_item(r) for r in rows]

    next_url = build_page_url(request, page + 1, size) if offset + size < total else None
    prev_url = build_page_url(request, page - 1, size) if page > 1 else None

    return PaginatedItems(total=total, next=next_url, prev=prev_url, items=items)


@app.post(
    f"{PREFIX}/items",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
    tags=["Items"],
)
def create_item(payload: ItemInput):
    with db_conn() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO items (sku, name, description) VALUES (?, ?, ?)",
                (payload.sku, payload.name, payload.description),
            )
        except sqlite3.IntegrityError:
            raise sku_conflict(payload.sku)

        row = conn.execute(
            "SELECT id, sku, name, description FROM items WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return row_to_item(row)


@app.get(
    f"{PREFIX}/items/{{item_id}}",
    response_model=ItemOut,
    summary="Get item by ID",
    tags=["Items"],
)
def get_item(item_id: int):
    with db_conn() as conn:
        row = conn.execute(
            "SELECT id, sku, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

    if row is None:
        raise not_found(item_id)

    return row_to_item(row)


@app.put(
    f"{PREFIX}/items/{{item_id}}",
    response_model=ItemOut,
    summary="Full replace of item",
    tags=["Items"],
)
def replace_item(item_id: int, payload: ItemInput):
    with db_conn() as conn:
        # Check existence first
        existing = conn.execute(
            "SELECT id FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if existing is None:
            raise not_found(item_id)

        try:
            conn.execute(
                "UPDATE items SET sku = ?, name = ?, description = ? WHERE id = ?",
                (payload.sku, payload.name, payload.description, item_id),
            )
        except sqlite3.IntegrityError:
            raise sku_conflict(payload.sku)

        row = conn.execute(
            "SELECT id, sku, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

    return row_to_item(row)


@app.patch(
    f"{PREFIX}/items/{{item_id}}",
    response_model=ItemOut,
    summary="Partial update of item",
    tags=["Items"],
)
def patch_item(item_id: int, payload: ItemPatch):
    with db_conn() as conn:
        row = conn.execute(
            "SELECT id, sku, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            raise not_found(item_id)

        # Only update fields that were explicitly provided
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            # Nothing to update — return current state
            return row_to_item(row)

        set_clause = ", ".join(f"{col} = ?" for col in updates)
        values = list(updates.values()) + [item_id]

        try:
            conn.execute(
                f"UPDATE items SET {set_clause} WHERE id = ?",
                values,
            )
        except sqlite3.IntegrityError:
            raise sku_conflict(updates["sku"])

        updated = conn.execute(
            "SELECT id, sku, name, description FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()

    return row_to_item(updated)


@app.delete(
    f"{PREFIX}/items/{{item_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item",
    tags=["Items"],
)
def delete_item(item_id: int):
    with db_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if existing is None:
            raise not_found(item_id)

        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
