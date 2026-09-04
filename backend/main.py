import base64, hashlib, hmac, os, secrets
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import DateTime, Float, ForeignKey, String, create_engine, delete, func, inspect, select, text
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
    menu_theme: Mapped[str]=mapped_column(String(30),default='classic')
    account_status: Mapped[str]=mapped_column(String(20),default='active')
    frozen_until: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
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
class AuditLog(Base):
    __tablename__='audit_logs'
    id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int|None]=mapped_column(ForeignKey('users.id'),nullable=True,index=True)
    action: Mapped[str]=mapped_column(String(80),index=True); detail: Mapped[str]=mapped_column(String(500),default=''); ip_address: Mapped[str]=mapped_column(String(80),default='')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),index=True)
class MenuView(Base):
    __tablename__='menu_views'
    id: Mapped[int]=mapped_column(primary_key=True); user_id: Mapped[int]=mapped_column(ForeignKey('users.id'),index=True)
    slug: Mapped[str]=mapped_column(String(100),index=True); ip_address: Mapped[str]=mapped_column(String(80),default=''); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),index=True)
Base.metadata.create_all(engine)
user_columns={column['name'] for column in inspect(engine).get_columns('users')}
with engine.begin() as connection:
    if 'menu_theme' not in user_columns: connection.execute(text("ALTER TABLE users ADD COLUMN menu_theme VARCHAR(30) DEFAULT 'classic'"))
    if 'account_status' not in user_columns: connection.execute(text("ALTER TABLE users ADD COLUMN account_status VARCHAR(20) DEFAULT 'active'"))
    if 'frozen_until' not in user_columns: connection.execute(text("ALTER TABLE users ADD COLUMN frozen_until TIMESTAMP"))
if DATABASE_URL.startswith('postgresql'):
    with engine.begin() as connection:
        for statement in [
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_start TIMESTAMPTZ',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS license_end TIMESTAMPTZ',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_logo TEXT',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_banner TEXT',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS menu_title VARCHAR(180)',
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active'",
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS frozen_until TIMESTAMPTZ']:
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
class MenuSettingsInput(BaseModel): company:str; menuTitle:str=''; logo:str|None=None; banner:str|None=None; theme:str='classic'
class ManagementScheduleInput(BaseModel):
    licenseStart:datetime; licenseEnd:datetime; status:str='active'; frozenUntil:datetime|None=None
class SystemAdminLoginInput(BaseModel): email:EmailStr; password:str
def get_db():
    with SessionLocal() as db: yield db
def system_admin(x_admin_key:str|None=Header(None)):
    expected=os.getenv('ADMIN_PANEL_KEY','raul2005')
    if not expected or not x_admin_key or not hmac.compare_digest(x_admin_key,expected): raise HTTPException(401,'Admin yetkisi gerekli')
    return True
def hash_password(password):
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,310000)
    return f'{base64.b64encode(salt).decode()}:{base64.b64encode(digest).decode()}'
def verify_password(password,encoded):
    salt,digest=encoded.split(':',1); actual=hashlib.pbkdf2_hmac('sha256',password.encode(),base64.b64decode(salt),310000)
    return hmac.compare_digest(actual,base64.b64decode(digest))
def aware(value): return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value
def log_event(db,user_id,action,detail='',ip=''):
    db.add(AuditLog(user_id=user_id,action=action,detail=detail[:500],ip_address=ip[:80]))
def account_frozen(u):
    if (u.account_status or 'active')!='frozen': return False
    return not u.frozen_until or aware(u.frozen_until)>datetime.now(timezone.utc)
def user_dict(u):
    start=u.license_start or datetime.now(timezone.utc); end=u.license_end or start+timedelta(days=365)
    remaining=max(0,(end.replace(tzinfo=timezone.utc)-datetime.now(timezone.utc)).days)
    return {'id':u.id,'company':u.company,'firstName':u.first_name,'lastName':u.last_name,'fullName':f'{u.first_name} {u.last_name}','email':u.email,'phone':u.phone,'slug':u.slug,
            'licenseStart':start.isoformat(),'licenseEnd':end.isoformat(),'licenseDaysRemaining':remaining,'menuTitle':u.menu_title or u.company,'logo':u.menu_logo,'banner':u.menu_banner,'theme':u.menu_theme or 'classic','status':u.account_status or 'active','frozenUntil':u.frozen_until.isoformat() if u.frozen_until else None}
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
def login(data:LoginInput,request:Request,db:Session=Depends(get_db)):
    email=data.email.lower().strip(); u=db.scalar(select(User).where(User.email==email))
    owner_email=os.getenv('OWNER_EMAIL','raul@gmail.com').lower().strip()
    owner_password=os.getenv('OWNER_PASSWORD','raul2005')
    if email==owner_email and hmac.compare_digest(data.password,owner_password):
        if not u:
            start=datetime.now(timezone.utc)
            u=User(company='Raul QR Menü',first_name='Raul',last_name='Babakhanov',email=owner_email,phone='',password_hash=hash_password(owner_password),slug='raul-qr-menu',license_start=start,license_end=start+timedelta(days=3650),menu_title='Raul QR Menü')
            db.add(u); db.commit(); db.refresh(u)
            for name in ['Ana Yemekler','Tatlılar','İçecekler']: db.add(Category(user_id=u.id,name=name))
            db.commit()
        elif not verify_password(owner_password,u.password_hash):
            u.password_hash=hash_password(owner_password); db.commit()
    ip=request.client.host if request.client else ''
    if not u or not verify_password(data.password,u.password_hash):
        log_event(db,u.id if u else None,'login_failed',f'Başarısız giriş: {data.email}',ip); db.commit(); raise HTTPException(401,'E-posta veya şifre hatalı')
    log_event(db,u.id,'login_success','Yönetim paneline giriş yapıldı',ip)
    return issue_token(db,u)
@app.get('/api/auth/me')
def me(u:User=Depends(current_user)): return user_dict(u)
@app.get('/api/stocks')
def list_stocks(u:User=Depends(current_user),db:Session=Depends(get_db)): return [stock_dict(s) for s in db.scalars(select(Stock).where(Stock.user_id==u.id).order_by(Stock.id.desc())).all()]
@app.post('/api/stocks',status_code=201)
def create_stock(item:StockInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    s=Stock(user_id=u.id,**item.model_dump()); db.add(s); log_event(db,u.id,'product_created',item.name); db.commit(); db.refresh(s); return stock_dict(s)
@app.put('/api/stocks/{stock_id}')
def update_stock(stock_id:int,item:StockInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    s=db.scalar(select(Stock).where(Stock.id==stock_id,Stock.user_id==u.id))
    if not s: raise HTTPException(404,'Ürün bulunamadı')
    for k,v in item.model_dump().items(): setattr(s,k,v)
    log_event(db,u.id,'product_updated',item.name); db.commit(); return stock_dict(s)
@app.delete('/api/stocks/{stock_id}')
def remove_stock(stock_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Stock).where(Stock.id==stock_id,Stock.user_id==u.id)); log_event(db,u.id,'product_deleted',f'Ürün #{stock_id}'); db.commit(); return {'ok':True}
@app.delete('/api/stocks')
def clear_stocks(u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Stock).where(Stock.user_id==u.id)); log_event(db,u.id,'products_cleared','Tüm ürünler silindi'); db.commit(); return {'ok':True}
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
    category=Category(user_id=u.id,name=name); db.add(category); log_event(db,u.id,'category_created',name); db.commit(); db.refresh(category); return {'id':category.id,'name':category.name}
@app.delete('/api/categories/{category_id}')
def remove_category(category_id:int,u:User=Depends(current_user),db:Session=Depends(get_db)):
    db.execute(delete(Category).where(Category.id==category_id,Category.user_id==u.id)); log_event(db,u.id,'category_deleted',f'Kategori #{category_id}'); db.commit(); return {'ok':True}
@app.get('/api/settings')
def settings(u:User=Depends(current_user)): return user_dict(u)
@app.put('/api/settings')
def update_settings(item:MenuSettingsInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    allowed_themes={'classic','modern','ocean','terracotta','midnight','pastel'}
    u.company=item.company.strip() or u.company; u.menu_title=item.menuTitle.strip() or u.company; u.menu_logo=item.logo; u.menu_banner=item.banner; u.menu_theme=item.theme if item.theme in allowed_themes else 'classic'
    log_event(db,u.id,'settings_updated',f'Tema: {u.menu_theme}'); db.commit(); return user_dict(u)
@app.get('/api/menu/{slug}')
def public_menu(slug:str,request:Request,db:Session=Depends(get_db)):
    u=db.scalar(select(User).where(User.slug==slug))
    if not u: raise HTTPException(404,'Menü bulunamadı')
    if account_frozen(u) or (u.license_end and aware(u.license_end)<datetime.now(timezone.utc)): raise HTTPException(403,'Menü geçici olarak kullanılamıyor')
    db.add(MenuView(user_id=u.id,slug=slug,ip_address=request.client.host if request.client else '')); db.commit()
    items=db.scalars(select(Stock).where(Stock.user_id==u.id,Stock.status=='active')).all()
    categories=db.scalars(select(Category).where(Category.user_id==u.id).order_by(Category.id)).all()
    return {'slug':slug,'business':u.company,'menuTitle':u.menu_title or u.company,'logo':u.menu_logo,'banner':u.menu_banner,'theme':u.menu_theme or 'classic','categories':[c.name for c in categories],'stocks':[stock_dict(s) for s in items]}

@app.get('/api/management/overview')
def management_overview(u:User=Depends(current_user),db:Session=Depends(get_db)):
    total_views=db.scalar(select(func.count(MenuView.id)).where(MenuView.user_id==u.id)) or 0
    today=datetime.now(timezone.utc).date(); daily=[]
    for offset in range(6,-1,-1):
        day=today-timedelta(days=offset); start=datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc); end=start+timedelta(days=1)
        count=db.scalar(select(func.count(MenuView.id)).where(MenuView.user_id==u.id,MenuView.created_at>=start,MenuView.created_at<end)) or 0
        daily.append({'date':day.isoformat(),'count':count})
    logs=db.scalars(select(AuditLog).where(AuditLog.user_id==u.id).order_by(AuditLog.id.desc()).limit(60)).all()
    return {'account':user_dict(u),'metrics':{'totalViews':total_views,'products':db.scalar(select(func.count(Stock.id)).where(Stock.user_id==u.id)) or 0,'sessions':db.scalar(select(func.count(AuthSession.token)).where(AuthSession.user_id==u.id)) or 0},'dailyViews':daily,'logs':[{'id':x.id,'action':x.action,'detail':x.detail,'ip':x.ip_address,'createdAt':x.created_at.isoformat()} for x in logs]}

@app.put('/api/management/schedule')
def update_management_schedule(item:ManagementScheduleInput,u:User=Depends(current_user),db:Session=Depends(get_db)):
    if item.licenseEnd<=item.licenseStart: raise HTTPException(400,'Bitiş tarihi başlangıçtan sonra olmalı')
    if item.status not in {'active','frozen'}: raise HTTPException(400,'Geçersiz hesap durumu')
    u.license_start=item.licenseStart; u.license_end=item.licenseEnd; u.account_status=item.status; u.frozen_until=item.frozenUntil if item.status=='frozen' else None
    log_event(db,u.id,'schedule_updated',f'Durum: {item.status}, bitiş: {item.licenseEnd.isoformat()}'); db.commit(); return user_dict(u)

@app.post('/api/system-admin/login')
def system_admin_login(item:SystemAdminLoginInput):
    expected_email=os.getenv('ADMIN_PANEL_EMAIL','raul@gmail.com')
    expected_key=os.getenv('ADMIN_PANEL_KEY','raul2005')
    if item.email.lower().strip()!=expected_email.lower() or not expected_key or not hmac.compare_digest(item.password,expected_key): raise HTTPException(401,'Admin bilgileri hatalı')
    return {'key':expected_key,'admin':{'email':expected_email,'name':'Raul Babakhanov'}}

@app.get('/api/system-admin/overview',dependencies=[Depends(system_admin)])
def system_admin_overview(db:Session=Depends(get_db)):
    users=db.scalars(select(User).order_by(User.id.desc())).all(); result=[]
    for item in users:
        info=user_dict(item)
        info.update({'products':db.scalar(select(func.count(Stock.id)).where(Stock.user_id==item.id)) or 0,'views':db.scalar(select(func.count(MenuView.id)).where(MenuView.user_id==item.id)) or 0,'lastLogin':db.scalar(select(func.max(AuditLog.created_at)).where(AuditLog.user_id==item.id,AuditLog.action=='login_success'))})
        if info['lastLogin']: info['lastLogin']=info['lastLogin'].isoformat()
        result.append(info)
    logs=db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(100)).all(); user_map={x.id:x for x in users}
    return {'metrics':{'businesses':len(users),'active':sum(1 for x in users if not account_frozen(x)),'frozen':sum(1 for x in users if account_frozen(x)),'views':db.scalar(select(func.count(MenuView.id))) or 0},'users':result,'logs':[{'id':x.id,'userId':x.user_id,'company':user_map[x.user_id].company if x.user_id in user_map else 'Bilinmeyen','action':x.action,'detail':x.detail,'ip':x.ip_address,'createdAt':x.created_at.isoformat()} for x in logs]}

@app.put('/api/system-admin/users/{user_id}/schedule',dependencies=[Depends(system_admin)])
def system_admin_schedule(user_id:int,item:ManagementScheduleInput,db:Session=Depends(get_db)):
    user=db.get(User,user_id)
    if not user: raise HTTPException(404,'İşletme bulunamadı')
    if item.licenseEnd<=item.licenseStart: raise HTTPException(400,'Bitiş tarihi başlangıçtan sonra olmalı')
    user.license_start=item.licenseStart; user.license_end=item.licenseEnd; user.account_status=item.status; user.frozen_until=item.frozenUntil if item.status=='frozen' else None
    log_event(db,user.id,'system_admin_updated',f'Admin planı güncelledi: {item.status}'); db.commit(); return user_dict(user)
