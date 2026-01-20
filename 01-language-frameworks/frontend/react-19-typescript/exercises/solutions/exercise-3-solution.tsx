/**
 * Exercise 3 Solution: Shopping Cart State Management
 */

import React, {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useMemo,
  ReactNode,
} from 'react'

// ============================================
// Type Definitions
// ============================================

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

// ============================================
// Action Types (Discriminated Union)
// ============================================

type CartAction =
  | { type: 'ADD_ITEM'; payload: Product }
  | { type: 'REMOVE_ITEM'; payload: string }
  | { type: 'UPDATE_QUANTITY'; payload: { id: string; quantity: number } }
  | { type: 'APPLY_DISCOUNT'; payload: string }
  | { type: 'REMOVE_DISCOUNT' }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_CART'; payload: CartItem[] }

// ============================================
// Discount Codes
// ============================================

const DISCOUNT_CODES: Record<string, number> = {
  SAVE10: 10,
  SAVE20: 20,
  FREESHIP: 0, // Handled separately
}

// ============================================
// Reducer
// ============================================

const initialState: CartState = {
  items: [],
  discountCode: null,
  discountPercent: 0,
}

function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingIndex = state.items.findIndex(
        (item) => item.product.id === action.payload.id
      )

      if (existingIndex >= 0) {
        // Item exists, update quantity
        const newItems = [...state.items]
        const currentQty = newItems[existingIndex].quantity
        const maxQty = action.payload.stock

        newItems[existingIndex] = {
          ...newItems[existingIndex],
          quantity: Math.min(currentQty + 1, maxQty),
        }

        return { ...state, items: newItems }
      }

      // Add new item
      return {
        ...state,
        items: [...state.items, { product: action.payload, quantity: 1 }],
      }
    }

    case 'REMOVE_ITEM': {
      return {
        ...state,
        items: state.items.filter((item) => item.product.id !== action.payload),
      }
    }

    case 'UPDATE_QUANTITY': {
      const { id, quantity } = action.payload

      if (quantity <= 0) {
        return {
          ...state,
          items: state.items.filter((item) => item.product.id !== id),
        }
      }

      return {
        ...state,
        items: state.items.map((item) => {
          if (item.product.id !== id) return item

          const maxQty = item.product.stock
          return {
            ...item,
            quantity: Math.min(quantity, maxQty),
          }
        }),
      }
    }

    case 'APPLY_DISCOUNT': {
      const code = action.payload.toUpperCase()
      const discountPercent = DISCOUNT_CODES[code]

      if (discountPercent === undefined) {
        return state // Invalid code, no change
      }

      return {
        ...state,
        discountCode: code,
        discountPercent,
      }
    }

    case 'REMOVE_DISCOUNT': {
      return {
        ...state,
        discountCode: null,
        discountPercent: 0,
      }
    }

    case 'CLEAR_CART': {
      return initialState
    }

    case 'LOAD_CART': {
      return {
        ...state,
        items: action.payload,
      }
    }

    default:
      return state
  }
}

// ============================================
// Selectors
// ============================================

function selectCartItems(state: CartState): CartItem[] {
  return state.items
}

function selectCartItemCount(state: CartState): number {
  return state.items.reduce((total, item) => total + item.quantity, 0)
}

function selectSubtotal(state: CartState): number {
  return state.items.reduce(
    (total, item) => total + item.product.price * item.quantity,
    0
  )
}

function selectDiscount(state: CartState): number {
  const subtotal = selectSubtotal(state)
  return (subtotal * state.discountPercent) / 100
}

function selectShipping(state: CartState): number {
  // Free shipping with FREESHIP code
  if (state.discountCode === 'FREESHIP') {
    return 0
  }

  const subtotal = selectSubtotal(state) - selectDiscount(state)

  if (subtotal >= 100) return 0
  if (subtotal >= 50) return 3.99
  return 5.99
}

function selectTotal(state: CartState): number {
  const subtotal = selectSubtotal(state)
  const discount = selectDiscount(state)
  const shipping = selectShipping(state)

  return subtotal - discount + shipping
}

// ============================================
// Context
// ============================================

interface CartContextValue {
  state: CartState
  items: CartItem[]
  itemCount: number
  subtotal: number
  discount: number
  shipping: number
  total: number
  discountCode: string | null
  addItem: (product: Product) => void
  removeItem: (productId: string) => void
  updateQuantity: (productId: string, quantity: number) => void
  applyDiscount: (code: string) => boolean
  removeDiscount: () => void
  clearCart: () => void
}

const CartContext = createContext<CartContextValue | null>(null)

function useCart(): CartContextValue {
  const context = useContext(CartContext)
  if (!context) {
    throw new Error('useCart must be used within CartProvider')
  }
  return context
}

// ============================================
// Provider Component
// ============================================

const STORAGE_KEY = 'shopping-cart'

interface CartProviderProps {
  children: ReactNode
}

function CartProvider({ children }: CartProviderProps) {
  const [state, dispatch] = useReducer(cartReducer, initialState)

  // Load cart from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const items = JSON.parse(saved) as CartItem[]
        dispatch({ type: 'LOAD_CART', payload: items })
      }
    } catch (error) {
      console.warn('Failed to load cart from localStorage:', error)
    }
  }, [])

  // Save cart to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.items))
    } catch (error) {
      console.warn('Failed to save cart to localStorage:', error)
    }
  }, [state.items])

  // Memoized computed values
  const items = useMemo(() => selectCartItems(state), [state])
  const itemCount = useMemo(() => selectCartItemCount(state), [state])
  const subtotal = useMemo(() => selectSubtotal(state), [state])
  const discount = useMemo(() => selectDiscount(state), [state])
  const shipping = useMemo(() => selectShipping(state), [state])
  const total = useMemo(() => selectTotal(state), [state])

  // Action creators
  const addItem = (product: Product) => {
    dispatch({ type: 'ADD_ITEM', payload: product })
  }

  const removeItem = (productId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: productId })
  }

  const updateQuantity = (productId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { id: productId, quantity } })
  }

  const applyDiscount = (code: string): boolean => {
    const upperCode = code.toUpperCase()
    if (DISCOUNT_CODES[upperCode] !== undefined) {
      dispatch({ type: 'APPLY_DISCOUNT', payload: code })
      return true
    }
    return false
  }

  const removeDiscount = () => {
    dispatch({ type: 'REMOVE_DISCOUNT' })
  }

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' })
  }

  const value: CartContextValue = {
    state,
    items,
    itemCount,
    subtotal,
    discount,
    shipping,
    total,
    discountCode: state.discountCode,
    addItem,
    removeItem,
    updateQuantity,
    applyDiscount,
    removeDiscount,
    clearCart,
  }

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

// ============================================
// Components
// ============================================

interface CartItemComponentProps {
  item: CartItem
}

function CartItemComponent({ item }: CartItemComponentProps) {
  const { removeItem, updateQuantity } = useCart()
  const { product, quantity } = item

  return (
    <div className="cart-item">
      <img src={product.image} alt={product.name} />
      <div className="cart-item-details">
        <h4>{product.name}</h4>
        <p>${product.price.toFixed(2)}</p>
      </div>
      <div className="cart-item-quantity">
        <button
          onClick={() => updateQuantity(product.id, quantity - 1)}
          disabled={quantity <= 1}
        >
          -
        </button>
        <span>{quantity}</span>
        <button
          onClick={() => updateQuantity(product.id, quantity + 1)}
          disabled={quantity >= product.stock}
        >
          +
        </button>
      </div>
      <div className="cart-item-total">
        ${(product.price * quantity).toFixed(2)}
      </div>
      <button
        className="remove-btn"
        onClick={() => removeItem(product.id)}
      >
        Remove
      </button>
    </div>
  )
}

function CartSummary() {
  const { subtotal, discount, shipping, total, discountCode, removeDiscount } =
    useCart()

  return (
    <div className="cart-summary">
      <div className="summary-row">
        <span>Subtotal:</span>
        <span>${subtotal.toFixed(2)}</span>
      </div>

      {discount > 0 && (
        <div className="summary-row discount">
          <span>
            Discount ({discountCode}):
            <button onClick={removeDiscount}>Remove</button>
          </span>
          <span>-${discount.toFixed(2)}</span>
        </div>
      )}

      <div className="summary-row">
        <span>Shipping:</span>
        <span>{shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}</span>
      </div>

      <div className="summary-row total">
        <span>Total:</span>
        <span>${total.toFixed(2)}</span>
      </div>
    </div>
  )
}

interface DiscountFormProps {
  onError?: (message: string) => void
}

function DiscountForm({ onError }: DiscountFormProps) {
  const { applyDiscount, discountCode } = useCart()
  const [code, setCode] = React.useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!applyDiscount(code)) {
      onError?.('Invalid discount code')
    }
    setCode('')
  }

  if (discountCode) {
    return <p>Discount applied: {discountCode}</p>
  }

  return (
    <form onSubmit={handleSubmit} className="discount-form">
      <input
        type="text"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Discount code"
      />
      <button type="submit">Apply</button>
    </form>
  )
}

interface AddToCartButtonProps {
  product: Product
  disabled?: boolean
}

function AddToCartButton({ product, disabled }: AddToCartButtonProps) {
  const { addItem, items } = useCart()
  const cartItem = items.find((i) => i.product.id === product.id)

  const isMaxQuantity = cartItem && cartItem.quantity >= product.stock

  return (
    <button
      onClick={() => addItem(product)}
      disabled={disabled || isMaxQuantity}
    >
      {isMaxQuantity ? 'Max quantity' : 'Add to Cart'}
    </button>
  )
}

function CartIcon() {
  const { itemCount } = useCart()

  return (
    <div className="cart-icon">
      <span className="icon">Cart</span>
      {itemCount > 0 && <span className="badge">{itemCount}</span>}
    </div>
  )
}

// ============================================
// Full Cart Component
// ============================================

function Cart() {
  const { items, clearCart } = useCart()

  if (items.length === 0) {
    return (
      <div className="cart-empty">
        <p>Your cart is empty</p>
      </div>
    )
  }

  return (
    <div className="cart">
      <div className="cart-items">
        {items.map((item) => (
          <CartItemComponent key={item.product.id} item={item} />
        ))}
      </div>

      <DiscountForm />

      <CartSummary />

      <div className="cart-actions">
        <button onClick={clearCart}>Clear Cart</button>
        <button className="checkout-btn">Checkout</button>
      </div>
    </div>
  )
}

// ============================================
// Exports
// ============================================

export {
  CartProvider,
  useCart,
  Cart,
  CartItemComponent,
  CartSummary,
  DiscountForm,
  AddToCartButton,
  CartIcon,
  cartReducer,
  selectCartItems,
  selectCartItemCount,
  selectSubtotal,
  selectDiscount,
  selectShipping,
  selectTotal,
}

export type { Product, CartItem, CartState, CartAction, CartContextValue }
