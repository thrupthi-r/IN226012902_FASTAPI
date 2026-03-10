from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
 
app = FastAPI()
 
# ── Pydantic model ───────────────────────────────────────────────────────────
class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
# ── Data ────────────────────────────────────────────────────────────────────
products = [
    {'id':1,'name':'Wireless Mouse','price':499,'category':'Electronics','in_stock':True},
    {'id':2,'name':'Notebook',      'price': 99,'category':'Stationery', 'in_stock':True},
    {'id':3,'name':'USB Hub',        'price':799,'category':'Electronics','in_stock':False},
    {'id':4,'name':'Pen Set',         'price': 49,'category':'Stationery', 'in_stock':True},
]
orders = []
order_counter = 1
 
# ── Endpoints ───────────────────────────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
@app.get('/products/filter')   # NOTE: must come BEFORE /products/{product_id}
def filter_products(
    category:  str  = Query(None),
    max_price: int  = Query(None),
    in_stock:  bool = Query(None)
):
    result = products
    if category:             result = [p for p in result if p['category']==category]
    if max_price:            result = [p for p in result if p['price']<=max_price]
    if in_stock is not None: result = [p for p in result if p['in_stock']==in_stock]
    return {'filtered_products': result, 'count': len(result)}
 
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}
 
@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = next((p for p in products if p['id']==order_data.product_id), None)
    if product is None:          return {'error': 'Product not found'}
    if not product['in_stock']:  return {'error': f"{product['name']} is out of stock"}
    total_price = product['price'] * order_data.quantity
    order = {'order_id': order_counter, 'customer_name': order_data.customer_name,
'product': product['name'], 'quantity': order_data.quantity,
'delivery_address': order_data.delivery_address,
'total_price': total_price, 'status': 'confirmed'}
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}
 
@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}