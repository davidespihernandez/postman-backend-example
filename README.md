# Items API

A RESTful API for managing Item resources, built with **FastAPI** and **SQLite**.  
Implements all endpoints defined in [`postman/specs/items-api.yaml`](postman/specs/items-api.yaml).

---

## Requirements

- Python 3.11+
- No external database — SQLite is bundled with Python

---

## Quick start

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn main:app --reload --port 3000
```

The API is now running at **http://localhost:3000**.  
The database file `items.db` is created automatically on first start — no migrations needed.

---

## Interactive docs

FastAPI generates live documentation automatically:

| UI | URL |
|----|-----|
| Swagger UI | http://localhost:3000/docs |
| ReDoc | http://localhost:3000/redoc |

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/items` | Paginated list of items |
| `POST` | `/items` | Create a new item |
| `GET` | `/items/{id}` | Retrieve item by ID |
| `PUT` | `/items/{id}` | Fully replace an item |
| `PATCH` | `/items/{id}` | Partially update an item |
| `DELETE` | `/items/{id}` | Delete an item |

### Pagination (`GET /items`)

| Query param | Default | Range | Description |
|-------------|---------|-------|-------------|
| `page` | `1` | ≥ 1 | Page number (1-based) |
| `size` | `20` | 1–100 | Items per page |

Response shape:

```json
{
  "total": 42,
  "next": "http://localhost:3000/items?page=3&size=20",
  "prev": "http://localhost:3000/items?page=1&size=20",
  "items": [ { "id": 1, "sku": "WIDGET-001", "name": "Blue Widget", "description": "..." } ]
}
```

`next` and `prev` are `null` when there is no next/previous page.

---

## Data model

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | integer | Auto-increment, read-only |
| `sku` | string | Required, unique |
| `name` | string | Required |
| `description` | string \| null | Optional |

---

## Error responses

All errors follow the same shape:

```json
{ "code": 404, "message": "Item not found." }
```

| Status | When |
|--------|------|
| `404` | Item ID does not exist |
| `409` | Duplicate `sku` on create or update |
| `422` | Invalid / missing required fields |

---

## Testing with Postman

Open the **Items** collection in this workspace and run requests against `http://localhost:3000`.  
The `Local` environment already has `baseUrl` set to `http://localhost:3000`.
