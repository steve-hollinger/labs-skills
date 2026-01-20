# Exercise 3: Shopping Cart State Management

## Objective

Implement a shopping cart using useReducer with TypeScript for type-safe state management.

## Requirements

1. Implement a shopping cart with:
   - Add item to cart
   - Remove item from cart
   - Update item quantity
   - Clear cart
   - Calculate totals

2. Create proper TypeScript types for:
   - Product
   - Cart item
   - Cart state
   - All action types

3. Features:
   - Persist cart to localStorage
   - Handle out-of-stock items
   - Apply discount codes
   - Calculate shipping based on total

## Data Types

```typescript
interface Product {
  id: string
  name: string
  price: number
  image: string
  stock: number
}

interface CartItem {
  product: Product
  quantity: number
}

interface CartState {
  items: CartItem[]
  discountCode: string | null
  discountPercent: number
}
```

## Tasks

### Task 1: Define Action Types

Create a discriminated union for all cart actions:

```typescript
type CartAction =
  | { type: 'ADD_ITEM'; payload: Product }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'APPLY_DISCOUNT'; payload: string }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: CartItem[] }
```

### Task 2: Implement Reducer

Create a reducer that handles all actions:

```typescript
function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM':
      // Handle adding item (check if exists, update quantity)
    case 'REMOVE_ITEM':
      // Remove item by product id
    case 'UPDATE_QUANTITY':
      // Update quantity, remove if 0
    case 'APPLY_DISCOUNT':
      // Validate and apply discount code
    case 'CLEAR_CART':
      // Reset to initial state
    case 'LOAD_CART':
      // Load from localStorage
  }
}
```

### Task 3: Create Cart Context

Build a context provider that:
- Provides cart state
- Provides dispatch actions
- Persists to localStorage
- Calculates derived values (subtotal, discount, shipping, total)

### Task 4: Build Cart Components

Create these components:
- `CartProvider` - Context provider
- `CartItem` - Individual cart item display
- `CartSummary` - Shows totals and checkout button
- `AddToCartButton` - Button to add product
- `CartIcon` - Shows cart item count

### Task 5: Implement Selectors

Create selector functions for:

```typescript
function selectCartItems(state: CartState): CartItem[]
function selectCartItemCount(state: CartState): number
function selectSubtotal(state: CartState): number
function selectDiscount(state: CartState): number
function selectShipping(state: CartState): number
function selectTotal(state: CartState): number
```

## Discount Codes

Implement these discount codes:
- `SAVE10` - 10% off
- `SAVE20` - 20% off
- `FREESHIP` - Free shipping

## Shipping Rules

- Orders under $50: $5.99 shipping
- Orders $50-$100: $3.99 shipping
- Orders over $100: Free shipping

## Example Usage

```tsx
function ProductCard({ product }: { product: Product }) {
  const { addItem, items } = useCart()
  const cartItem = items.find(i => i.product.id === product.id)

  return (
    <div>
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      {cartItem ? (
        <p>In cart: {cartItem.quantity}</p>
      ) : null}
      <AddToCartButton
        product={product}
        disabled={product.stock === 0}
      />
    </div>
  )
}

function Cart() {
  const { items, subtotal, discount, shipping, total, clearCart } = useCart()

  return (
    <div>
      {items.map(item => (
        <CartItem key={item.product.id} item={item} />
      ))}
      <CartSummary
        subtotal={subtotal}
        discount={discount}
        shipping={shipping}
        total={total}
      />
      <button onClick={clearCart}>Clear Cart</button>
    </div>
  )
}
```

## Bonus Challenges

1. Add undo functionality for item removal
2. Implement quantity limits based on stock
3. Add "Save for later" feature
4. Implement cart item notes

## Validation Checklist

- [ ] All types properly defined
- [ ] Reducer handles all actions
- [ ] Context provides state and actions
- [ ] LocalStorage persistence works
- [ ] Discount codes work correctly
- [ ] Shipping calculated correctly
- [ ] No TypeScript errors
- [ ] Tests pass
