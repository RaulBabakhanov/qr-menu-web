import { authHeaders } from './auth'

export type ManagementAccount={company:string;email:string;slug:string;licenseStart:string;licenseEnd:string;licenseDaysRemaining:number;status:'active'|'frozen';frozenUntil?:string|null}
export type AuditItem={id:number;action:string;detail:string;ip:string;createdAt:string}
export type ManagementOverview={account:ManagementAccount;metrics:{totalViews:number;products:number;sessions:number};dailyViews:{date:string;count:number}[];logs:AuditItem[]}

async function api(path:string,options:RequestInit={}){
  const response=await fetch(`/api${path}`,{...options,headers:{'Content-Type':'application/json',...authHeaders(),...(options.headers||{})}})
  const data=await response.json().catch(()=>({}))
  if(!response.ok)throw new Error(data.detail||'İşlem gerçekleştirilemedi')
  return data
}
export const fetchManagement=()=>api('/management/overview') as Promise<ManagementOverview>
export const saveSchedule=(payload:{licenseStart:string;licenseEnd:string;status:'active'|'frozen';frozenUntil:string|null})=>api('/management/schedule',{method:'PUT',body:JSON.stringify(payload)}) as Promise<ManagementAccount>
