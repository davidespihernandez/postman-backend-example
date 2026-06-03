const http = require('http');
const PORT = process.env.PORT || 4500;

const server = http.createServer((req, res) => {

  // @endpoint GET /items
  if (pm.mock.matchRequest('postman/collections/Items/items/List items.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/List items.resources/examples/A paginated list of items-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/List items.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/List items.resources/examples/Internal server error-.example.yaml', res);
  }

  // @endpoint POST /items
  if (pm.mock.matchRequest('postman/collections/Items/items/Create item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/Create item.resources/examples/The newly created item-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/Create item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/Create item.resources/examples/Internal server error-.example.yaml', res);
  }

  // @endpoint GET /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Get item by ID.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Get item by ID.resources/examples/The requested item-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Get item by ID.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Get item by ID.resources/examples/Item not found-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Get item by ID.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Get item by ID.resources/examples/Internal server error-.example.yaml', res);
  }

  // @endpoint PUT /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Replace item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Replace item.resources/examples/The updated item-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Replace item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Replace item.resources/examples/Item not found-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Replace item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Replace item.resources/examples/Internal server error-.example.yaml', res);
  }

  // @endpoint PATCH /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Partial update item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Partial update item.resources/examples/The patched item-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Partial update item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Partial update item.resources/examples/Item not found-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Partial update item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Partial update item.resources/examples/Internal server error-.example.yaml', res);
  }

  // @endpoint DELETE /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Delete item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Delete item.resources/examples/Item successfully deleted. No content returned-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Delete item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Delete item.resources/examples/Item not found-.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Delete item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Delete item.resources/examples/Internal server error-.example.yaml', res);
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Endpoint not defined' }));
});

server.listen(PORT);
