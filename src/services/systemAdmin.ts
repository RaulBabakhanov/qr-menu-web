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
