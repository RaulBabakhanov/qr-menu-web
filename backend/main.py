from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title='Lokanta QR Menu API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])
stocks = [{'id': 1, 'name': 'Adana Kebap', 'price': 250, 'createdAt': datetime.now().isoformat()}]
class StockInput(BaseModel):
    name: str
    price: float
@app.get('/api/stocks')
def list_stocks(): return stocks
@app.post('/api/stocks')
def create_stock(item: StockInput):
    stock = {'id': len(stocks) + 1, **item.model_dump(), 'createdAt': datetime.now().isoformat()}; stocks.insert(0, stock); return stock
@app.put('/api/stocks/{stock_id}')
def update_stock(stock_id: int, item: StockInput):
    for stock in stocks:
        if stock['id'] == stock_id: stock.update(item.model_dump()); return stock
    raise HTTPException(404, 'Stok bulunamadı')
@app.delete('/api/stocks/{stock_id}')
def delete_stock(stock_id: int):
    global stocks; stocks = [stock for stock in stocks if stock['id'] != stock_id]; return {'ok': True}
@app.post('/api/stocks/import')
async def import_stocks(file: UploadFile = File(...)):
    frame = pd.read_excel(await file.read()); imported = []
    for _, row in frame.iterrows():
        name, price = str(row.get('Stok Adı', '')).strip(), row.get('Fiyat')
        if name and pd.notna(price): imported.append(create_stock(StockInput(name=name, price=float(price))))
    return {'imported': imported, 'total': len(imported)}
@app.get('/api/menu/{slug}')
def public_menu(slug: str): return {'slug': slug, 'business': 'Lokanta', 'stocks': stocks}
