import { authHeaders } from './auth'
export type Category={id:number;name:string}
export type MenuTheme='classic'|'modern'|'ocean'|'terracotta'|'midnight'|'pastel'
export type MenuSettings={company:string;menuTitle:string;logo?:string;banner?:string;theme:MenuTheme;licenseStart:string;licenseEnd:string;licenseDaysRemaining:number;slug:string}
async function api(path:string,options:RequestInit={}){const response=await fetch(`/api${path}`,{...options,headers:{'Content-Type':'application/json',...authHeaders(),...(options.headers||{})}});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.detail||'İşlem yapılamadı');return data}
export const fetchSettings=()=>api('/settings') as Promise<MenuSettings>
export const saveSettings=(data:{company:string;menuTitle:string;logo?:string;banner?:string;theme:MenuTheme})=>api('/settings',{method:'PUT',body:JSON.stringify(data)}) as Promise<MenuSettings>
export const fetchCategories=()=>api('/categories') as Promise<Category[]>
export const addCategory=(name:string)=>api('/categories',{method:'POST',body:JSON.stringify({name})}) as Promise<Category>
export const deleteCategory=(id:number)=>api(`/categories/${id}`,{method:'DELETE'})
