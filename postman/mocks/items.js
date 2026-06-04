const http = require('http');
const PORT = process.env.PORT || 4500;

const server = http.createServer((req, res) => {

  // @endpoint GET /items
  if (pm.mock.matchRequest('postman/collections/Items/items/List items.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/List items.resources/examples/A paginated list of items.example.yaml', res);
  }

  // @endpoint POST /items
  if (pm.mock.matchRequest('postman/collections/Items/items/Create item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/.resources/Create item.resources/examples/Item created successfully.example.yaml', res);
  }

  // @endpoint GET /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Get item by ID.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Get item by ID.resources/examples/Item found.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Get item by ID.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Get item by ID.resources/examples/Item not found.example.yaml', res);
  }

  // @endpoint PUT /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Full replace of an item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Full replace of an item.resources/examples/Item replaced successfully.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Full replace of an item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Full replace of an item.resources/examples/Item not found.example.yaml', res);
  }

  // @endpoint PATCH /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Partial update of an item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Partial update of an item.resources/examples/Item updated successfully.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Partial update of an item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Partial update of an item.resources/examples/Item not found.example.yaml', res);
  }

  // @endpoint DELETE /items/:id
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Delete item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Delete item.resources/examples/Item deleted successfully.example.yaml', res);
  }
  if (pm.mock.matchRequest('postman/collections/Items/items/{id}/Delete item.request.yaml', req)) {
    return pm.mock.sendExample('postman/collections/Items/items/{id}/.resources/Delete item.resources/examples/Item not found.example.yaml', res);
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Endpoint not defined' }));
});

server.listen(PORT);
