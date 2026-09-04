export async function loginSystemAdmin(password:string){
  const response=await fetch('/api/system-admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'raul@gmail.com',password})})
  const data=await response.json().catch(()=>({}))
  if(!response.ok)throw new Error(data.detail||'Yönetici girişi yapılamadı')
  localStorage.setItem('qr-menu-admin-key',data.key)
  return data.admin
}
