export type Account = { id:number; company:string; firstName:string; lastName:string; fullName:string; email:string; phone:string; slug:string }
const tokenKey='qr-menu-token', userKey='qr-menu-user'
async function request(path:string, options:RequestInit={}) {
  const response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})}})
  const data=await response.json().catch(()=>({}))
  if(!response.ok) throw new Error(data.detail||'İşlem gerçekleştirilemedi.')
  return data
}
function saveSession(data:{token:string;user:Account}) {
  localStorage.setItem(tokenKey,data.token); localStorage.setItem(userKey,JSON.stringify(data.user))
  localStorage.setItem('qr-menu-profile-name',data.user.fullName); window.dispatchEvent(new Event('qr-menu-profile-updated'))
}
export async function loginAccount(email:string,password:string){const data=await request('/api/auth/login',{method:'POST',body:JSON.stringify({email,password})});saveSession(data);return data.user as Account}
export async function registerAccount(payload:{company:string;firstName:string;lastName:string;email:string;phone:string;password:string}){const data=await request('/api/auth/register',{method:'POST',body:JSON.stringify(payload)});saveSession(data);return data.user as Account}
export function getToken(){return localStorage.getItem(tokenKey)||''}
export function getAccount():Account|null{try{return JSON.parse(localStorage.getItem(userKey)||'null')}catch{return null}}
export function authHeaders():Record<string,string>{const token=getToken();return token?{Authorization:`Bearer ${token}`}:{}}
