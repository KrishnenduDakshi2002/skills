# Test examples

## Behavior through a public interface

```typescript
test("user can checkout with a valid cart", async () => {
  const cart = createCart();
  cart.add(product);

  const result = await checkout(cart, paymentMethod);

  expect(result.status).toBe("confirmed");
});
```

This test names a caller-visible capability, uses the public interface, and can survive internal refactoring.

Avoid tests that only prove an internal collaborator was called:

```typescript
test("checkout calls paymentService.process", async () => {
  const payment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(payment.process).toHaveBeenCalledWith(cart.total);
});
```

## Verify through the interface

Avoid bypassing the public interface to inspect storage:

```typescript
// Bad: verifies through a side channel.
await createUser({ name: "Alice" });
const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
expect(row).toBeDefined();
```

Verify the observable capability instead:

```typescript
const user = await createUser({ name: "Alice" });
const retrieved = await getUser(user.id);
expect(retrieved.name).toBe("Alice");
```

## Use an independent expected value

Do not reconstruct the result with the same algorithm as production code:

```typescript
// Bad: expected value repeats the implementation.
const expected = items.reduce((sum, item) => sum + item.price, 0);
expect(calculateTotal(items)).toBe(expected);

// Good: expected value is a known worked example.
expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
```

