# Items API

A demo CRUD API for an **Item** resource, built with **FastAPI** and **SQLite**.  
The implementation follows the OpenAPI 3.0.3 spec at [`postman/specs/items-api.yaml`](postman/specs/items-api.yaml).

---

## Requirements

- Python 3.11+

---

## Quick start

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.  
The SQLite database file (`items.db`) is created automatically on first run — no migrations needed.

---

## Interactive docs

| UI | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## Endpoints

All routes are prefixed with `/api/v1`.

| Method | Path | Description | Success |
|--------|------|-------------|---------|
| `GET` | `/api/v1/items` | Paginated list of items | 200 |
| `POST` | `/api/v1/items` | Create a new item | 201 |
| `GET` | `/api/v1/items/{id}` | Get item by ID | 200 |
| `PUT` | `/api/v1/items/{id}` | Fully replace an item | 200 |
| `PATCH` | `/api/v1/items/{id}` | Partially update an item | 200 |
| `DELETE` | `/api/v1/items/{id}` | Delete an item | 204 |

### Pagination (GET /api/v1/items)

| Query param | Default | Description |
|---|---|---|
| `page` | `1` | Page number (1-based) |
| `size` | `20` | Items per page |

Response shape:
```json
{
  "total": 42,
  "next": "http://127.0.0.1:8000/api/v1/items?page=3&size=20",
  "prev": "http://127.0.0.1:8000/api/v1/items?page=1&size=20",
  "items": [ ... ]
}
```

### Item object

```json
{
  "id": 1,
  "sku": "ITEM-001",
  "name": "Widget Pro",
  "description": "A high-quality widget for professional use"
}
```

---

## Error responses

All errors follow the spec's `Error` schema:

```json
{
  "code": 404,
  "message": "Item with id 99 not found"
}
```

| Status | Trigger |
|---|---|
| `404` | Item ID does not exist |
| `409` | Duplicate `sku` on create or update |
| `422` | Invalid request body (FastAPI validation) |

---

## Project structure

```
.
├── main.py                        # FastAPI app (single file)
├── requirements.txt
├── README.md
├── items.db                       # SQLite DB — auto-created, git-ignored
└── postman/
    └── specs/
        └── items-api.yaml         # OpenAPI 3.0.3 specification
```
