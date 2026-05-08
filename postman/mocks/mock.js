const http = require('http');
const url = require('url');

// Examples keyed by status code per endpoint.
// The first key in each map is the default response code.

const EXAMPLES = {
  'GET /items': {
    200: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        "total": 42,
        "next": "http://localhost:3000/items?page=3&size=20",
        "prev": "http://localhost:3000/items?page=1&size=20",
        "items": [
          { "id": 21, "sku": "WIDGET-021", "name": "Green Widget", "description": "A medium green widget for outdoor use." },
          { "id": 22, "sku": "WIDGET-022", "name": "Red Widget", "description": null },
          { "id": 23, "sku": "GADGET-001", "name": "Pocket Gadget", "description": "A compact gadget that fits in any pocket." }
        ]
      })
    }
  },
  'POST /items': {
    201: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "id": 1, "sku": "WIDGET-001", "name": "Blue Widget", "description": "A small blue widget used in assembly line B." })
    }
  },
  'GET /items/:id': {
    200: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "id": 1, "sku": "WIDGET-001", "name": "Blue Widget", "description": "A small blue widget used in assembly line B." })
    },
    404: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "code": 404, "message": "Item not found." })
    }
  },
  'PUT /items/:id': {
    200: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "id": 1, "sku": "WIDGET-001", "name": "Blue Widget", "description": "A small blue widget used in assembly line B." })
    },
    404: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "code": 404, "message": "Item not found." })
    }
  },
  'PATCH /items/:id': {
    200: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "id": 1, "sku": "WIDGET-001", "name": "Blue Widget", "description": "A small blue widget used in assembly line B." })
    },
    404: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "code": 404, "message": "Item not found." })
    }
  },
  'DELETE /items/:id': {
    204: {
      headers: {},
      body: ''
    },
    404: {
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ "code": 404, "message": "Item not found." })
    }
  }
};

// Returns the example for the given endpoint key and requested status code.
// Falls back to the first (default) example if the requested code doesn't exist.
function resolve(endpointKey, requestedCode) {
  const map = EXAMPLES[endpointKey];
  const code = requestedCode && map[requestedCode] ? Number(requestedCode) : Number(Object.keys(map)[0]);
  return { statusCode: code, ...map[code] };
}

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  const pathname = parsed.pathname;
  const method = req.method.toUpperCase();
  const mockCode = req.headers['x-mock-response-code'];

  function send(endpointKey) {
    const example = resolve(endpointKey, mockCode);
    res.writeHead(example.statusCode, example.headers);
    res.end(example.body);
  }

  // @endpoint GET /items
  if (method === 'GET' && pathname === '/items') return send('GET /items');

  // @endpoint POST /items
  if (method === 'POST' && pathname === '/items') return send('POST /items');

  const idMatch = /^\/items\/(\d+)$/.exec(pathname);

  // @endpoint GET /items/:id
  if (method === 'GET' && idMatch) return send('GET /items/:id');

  // @endpoint PUT /items/:id
  if (method === 'PUT' && idMatch) return send('PUT /items/:id');

  // @endpoint PATCH /items/:id
  if (method === 'PATCH' && idMatch) return send('PATCH /items/:id');

  // @endpoint DELETE /items/:id
  if (method === 'DELETE' && idMatch) return send('DELETE /items/:id');

  // Fallback 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ code: 404, message: 'Route not found.' }));
});

server.listen(process.env.PORT || 4501);