# Mocking

Mock only at system boundaries:

- External APIs
- Time and randomness
- File systems when a real temporary filesystem is inappropriate
- Databases when a real test database is impractical

Do not mock your own modules or internal collaborators. Prefer exercising their real behavior through the public seam.

## Design boundary adapters

Accept external dependencies instead of constructing them internally:

```typescript
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}
```

Prefer operation-specific adapter methods over a generic conditional fetcher:

```typescript
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch("/orders", { method: "POST", body: data }),
};
```

Each boundary mock should return one stable shape without reproducing production branching logic.

