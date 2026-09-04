export type AdminUser={
  id:number; company:string; firstName:string; lastName:string; fullName:string
  email:string; phone:string; slug:string; licenseStart:string; licenseEnd:string
  licenseDaysRemaining:number; status:'active'|'frozen'; frozenUntil?:string|null
  registeredAt?:string; products?:number; views?:number; lastLogin?:string|null; protected?:boolean
}
export type AuditItem={id:number;action:string;detail:string;ip:string;createdAt:string;userId?:number;company?:string}
export type AdminOverview={
  metrics:{businesses:number;active:number;frozen:number;views:number}
  users:AdminUser[]
  logs:AuditItem[]
}
export type UserOverview={
  account:AdminUser
  metrics:{totalViews:number;products:number;sessions:number}
  dailyViews:{date:string;count:number}[]
  logs:AuditItem[]
}

export async function loginSystemAdmin(password:string){
  const response=await fetch('/api/system-admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password})})
  const data=await response.json().catch(()=>({}))
  if(!response.ok)throw new Error(data.detail||'Yönetici girişi yapılamadı')
  localStorage.setItem('qr-menu-admin-key',data.key)
  localStorage.setItem('qr-menu-token',data.token)
  localStorage.setItem('qr-menu-user',JSON.stringify(data.user))
  localStorage.setItem('qr-menu-profile-name',data.user.fullName)
  return data.admin
}

function adminHeaders():Record<string,string>{
  const key=localStorage.getItem('qr-menu-admin-key')||''
  return {'Content-Type':'application/json','X-Admin-Key':key}
}

async function adminApi(path:string,options:RequestInit={}){
  const response=await fetch(`/api${path}`,{...options,headers:{...adminHeaders(),...(options.headers||{})}})
  const data=await response.json().catch(()=>({}))
  if(!response.ok)throw new Error(data.detail||'İşlem gerçekleştirilemedi')
  return data
}

export const hasAdminKey=()=>Boolean(localStorage.getItem('qr-menu-admin-key'))
export const fetchAdminOverview=()=>adminApi('/system-admin/overview') as Promise<AdminOverview>
export const fetchAdminUser=(id:number)=>adminApi(`/system-admin/users/${id}`) as Promise<UserOverview>
export const saveAdminUserSchedule=(id:number,payload:{licenseStart:string;licenseEnd:string;status:'active'|'frozen';frozenUntil:string|null})=>
  adminApi(`/system-admin/users/${id}/schedule`,{method:'PUT',body:JSON.stringify(payload)}) as Promise<AdminUser>
export const deleteAdminUser=(id:number)=>adminApi(`/system-admin/users/${id}`,{method:'DELETE'}) as Promise<{ok:boolean}>
