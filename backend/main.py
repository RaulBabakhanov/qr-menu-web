import base64, hashlib, hmac, os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import DateTime, Float, ForeignKey, String, create_engine, delete, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./qr_menu.db')
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    company: Mapped[str]=mapped_column(String(180)); first_name: Mapped[str]=mapped_column(String(80)); last_name: Mapped[str]=mapped_column(String(80))
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True); phone: Mapped[str]=mapped_column(String(40),default='')
    password_hash: Mapped[str]=mapped_column(String(255)); slug: Mapped[str]=mapped_column(String(100),unique=True,index=True)
    license_start: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    license_end: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    menu_logo: Mapped[str|None]=mapped_column(String,nullable=True)
    menu_banner: Mapped[str|None]=mapped_column(String,nullable=True)
    menu_title: Mapped[str|None]=mapped_column(String(180),nullable=True)
class Stock(Base):
    __tablename__='stocks'
    id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
    name: Mapped[str]=mapped_column(String(180)); price: Mapped[float]=mapped_column(Float); category: Mapped[str]=mapped_column(String(100),default='Ana Yemekler')
    status: Mapped[str]=mapped_column(String(20),default='active'); image: Mapped[str|None]=mapped_column(String,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
class AuthSession(Base):
    __tablename__='auth_sessions'
    token: Mapped[str]=mapped_column(String(128),primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
class Category(Base):
    __tablename__='categories'
    id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
    name: Mapped[str]=mapped_column(String(100)); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
Base.metadata.create_all(engine)
if DATABASE_URL.startswith('postgresql'):
    with engine.begin() as connection:
        for statement in [
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_start TIMESTAMPTZ',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_end TIMESTAMPTZ',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_logo TEXT',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_banner TEXT',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_title VARCHAR(180)']:
            connection.execute(text(statement))
        connection.execute(text('UPDATE users SET license_start=NOW() WHERE license_start IS NULL'))
        connection.execute(text("UPDATE users SET license_end=license_start + INTERVAL '365 days' WHERE license_end IS NULL"))
        connection.execute(text('UPDATE users SET menu_title=company WHERE menu_title IS NULL'))

app=FastAPI(title='QR Menu API')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['*'],allow_headers=['*'])
class RegisterInput(BaseModel):
    company:str; firstName:str; lastName:str; email:EmailStr; phone:str=''; password:str
class LoginInput(BaseModel): email:EmailStr; password:str
class StockInput(BaseModel):
    name:str; price:float; category:str='Ana Yemekler'; status:str='active'; image:str|None=None
class CategoryInput(BaseModel): name:str
class MenuSettingsInput(BaseModel): company:str; menuTitle:str=''; logo:str|None=None; banner:str|None=None
def get_db():
    with SessionLocal() as db: yield db
def hash_password(password):
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,310000)
    return f'{base64.b64encode(salt).decode()}:{base64.b64encode(digest).decode()}'
def verify_password(password,encoded):
    salt,digest=encoded.split(':',1); actual=hashlib.pbkdf2_hmac('sha256',password.encode(),base64.b64decode(salt),310000)
    return hmac.compare_digest(actual,base64.b64decode(digest))
def user_dict(u):
    start=u.license_start or datetime.now(timezone.utc); end=u.license_end or start+timedelta(days=365)
    remaining=max(0,(end.replace(tzinfo=timezone.utc)-datetime.now(timezone.utc)).days)
    return {'id':u.id,'company':u.company,'firstName':u.first_name,'lastName':u.last_name,'fullName':f'{u.first_name} {u.last_name}','email':u.email,'phone':u.phone,'slug':u.slug,
            'licenseStart':start.isoformat(),'licenseEnd':end.isoformat(),'licenseDaysRemaining':remaining,'menuTitle':u.menu_title or u.company,'logo':u.menu_logo,'banner':u.menu_banner}
def stock_dict(s): return {'id':s.id,'name':s.name,'price':s.price,'category':s.category,'status':s.status,'image':s.image,'createdAt':s.created_at.isoformat()}
def issue_token(db,u):
    token=secrets.token_urlsafe(48); db.add(AuthSession(token=token,user_id=u.id,expires_at=datetime.now(timezone.utc)+timedelta(days=30))); db.commit()
    return {'token':token,'user':user_dict(u)}
def current_user(authorization:str|None=Header(None),db:Session=Depends(get_db)):
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Oturum açmanız gerekiyor')
    auth=db.get(AuthSession,authorization[7:])
    if not auth or auth.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(401,'Oturum süresi doldu')
    user=db.get(User,auth.user_id)
    if not user: raise HTTPException(401,'Kullanıcı bulunamadı')
    return user

@app.get('/api/health')
def health(): return {'ok':True}
@app.post('/api/auth/register',status_code=201)
def register(data:RegisterInput,db:Session=Depends(get_db)):
    email=data.email.lower().strip()
    if len(data.password)<6: raise HTTPException(400,'Şifre en az 6 karakter olmalıdır')
    if db.scalar(select(User).where(User.email==email)): raise HTTPException(409,'Bu e-posta zaten kayıtlı')
    root=''.join(c if c.isalnum() else '-' for c in data.company.lower()).strip('-') or 'menu'; slug=root
    while db.scalar(select(User).where(User.slug==slug)): slug=f'{root}-{secrets.token_hex(2)}'
    start=datetime.now(timezone.utc)
    u=User(company=data.company.strip(),first_name=data.firstName.strip(),last_name=data.lastName.strip(),email=email,phone=data.phone.strip(),password_hash=hash_password(data.password),slug=slug,license_start=start,license_end=start+timedelta(days=365),menu_title=data.company.strip())
    db.add(u); db.commit(); db.refresh(u)
    for name in ['Ana Yemekler','Tatlılar','İçecekler']: db.add(Category(user_id=u.id,name=name))
    db.commit(); return issue_token(db,u)
@app.post('/api/auth/login')
def login(data:LoginInput,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.email==data.email.lower().strip()))
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,'E-posta veya şifre hatalı')
    return issue_token(db,u)
@app.get('/api/auth/me')
def me(u:User=Depends(current_user)): return user_dict(u)
@app.get('/api/stocks')
def list_stocks(u:User=Depends(current_user),db:Session=Depends(get_db)): return [stock_dict(s) for s in db.scalars(select(Stock).where(Stock.user_id==u.id).order_by(Stock.id.desc())).all()]
@app.post('/api/stocks',status_code=201)
def create_stock(item:StockInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    s=Stock(user_id=u.id,**item.model_dump()); db.add(s); db.commit(); db.refresh(s); return stock_dict(s)
@app.put('/api/stocks/{stock_id}')
def update_stock(stock_id:int,item:StockInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    s=db.scalar(select(Stock).where(Stock.id==stock_id,Stock.user_id==u.id))
    if not s: raise HTTPException(404,'Ürün bulunamadı')
    for k,v in item.model_dump().items(): setattr(s,k,v)
    db.commit(); return stock_dict(s)
@app.delete('/api/stocks/{stock_id}')
def remove_stock(stock_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Stock).where(Stock.id==stock_id,Stock.user_id==u.id)); db.commit(); return {'ok':True}
@app.delete('/api/stocks')
def clear_stocks(u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Stock).where(Stock.user_id==u.id)); db.commit(); return {'ok':True}
@app.get('/api/categories')
def list_categories(u:User=Depends(current_user),db:Session=Depends(get_db)):
    items=db.scalars(select(Category).where(Category.user_id==u.id).order_by(Category.id)).all()
    return [{'id':item.id,'name':item.name} for item in items]
@app.post('/api/categories',status_code=201)
def create_category(item:CategoryInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    name=item.name.strip()
    if not name: raise HTTPException(400,'Kategori adı boş olamaz')
    existing=db.scalar(select(Category).where(Category.user_id==u.id,Category.name==name))
    if existing: return {'id':existing.id,'name':existing.name}
    category=Category(user_id=u.id,name=name); db.add(category); db.commit(); db.refresh(category); return {'id':category.id,'name':category.name}
@app.delete('/api/categories/{category_id}')
def remove_category(category_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Category).where(Category.id==category_id,Category.user_id==u.id)); db.commit(); return {'ok':True}
@app.get('/api/settings')
def settings(u:User=Depends(current_user)): return user_dict(u)
@app.put('/api/settings')
def update_settings(item:MenuSettingsInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    u.company=item.company.strip() or u.company; u.menu_title=item.menuTitle.strip() or u.company; u.menu_logo=item.logo; u.menu_banner=item.banner
    db.commit(); return user_dict(u)
@app.get('/api/menu/{slug}')
def public_menu(slug:str,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.slug==slug))
    if not u: raise HTTPException(404,'Menü bulunamadı')
    items=db.scalars(select(Stock).where(Stock.user_id==u.id,Stock.status=='active')).all()
    categories=db.scalars(select(Category).where(Category.user_id==u.id).order_by(Category.id)).all()
    return {'slug':slug,'business':u.company,'menuTitle':u.menu_title or u.company,'logo':u.menu_logo,'banner':u.menu_banner,'categories':[c.name for c in categories],'stocks':[stock_dict(s) for s in items]}
