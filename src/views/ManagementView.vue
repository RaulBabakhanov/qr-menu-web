<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Activity, AlertTriangle, CalendarClock, Check, Clock3, Eye, Package, Power, QrCode, RefreshCw, Save, Search, ShieldCheck, Trash2, Users, X } from 'lucide-vue-next'
import { deleteAdminUser, fetchAdminOverview, fetchAdminUser, hasAdminKey, saveAdminUserSchedule, type AdminOverview, type AdminUser, type AuditItem, type UserOverview } from '../services/systemAdmin'

const router=useRouter()
const overview=ref<AdminOverview|null>(null),detail=ref<UserOverview|null>(null)
const selectedId=ref<number|null>(null),query=ref(''),pendingDelete=ref<AdminUser|null>(null)
const loading=ref(true),selecting=ref(false),saving=ref(false),deleting=ref(false),error=ref(''),saved=ref(false)
const start=ref(''),end=ref(''),frozenUntil=ref(''),status=ref<'active'|'frozen'>('active')
const maxView=computed(()=>Math.max(1,...(detail.value?.dailyViews.map(x=>x.count)||[1])))
const users=computed(()=>{
  const list=overview.value?.users||[]
  const q=query.value.trim().toLowerCase()
  if(!q) return list
  return list.filter(u=>[u.company,u.fullName,u.email,u.phone,u.slug].join(' ').toLowerCase().includes(q))
})
const selected=computed(()=>(overview.value?.users||[]).find(u=>u.id===selectedId.value)||null)
const actionNames:Record<string,string>={account_registered:'Yeni kayıt',account_deleted:'Hesap silindi',login_success:'Başarılı giriş',login_failed:'Başarısız giriş',product_created:'Ürün oluşturuldu',product_updated:'Ürün güncellendi',product_deleted:'Ürün silindi',products_cleared:'Ürünler temizlendi',category_created:'Kategori oluşturuldu',category_deleted:'Kategori silindi',settings_updated:'Menü ayarları değişti',schedule_updated:'Zamanlama güncellendi',system_admin_updated:'Admin zamanlamayı güncelledi'}
const toInput=(value?:string|null)=>value?new Date(value).toISOString().slice(0,16):''
const formatDate=(value?:string|null)=>value?new Intl.DateTimeFormat('tr-TR',{dateStyle:'medium',timeStyle:'short'}).format(new Date(value)):'—'
const formatDay=(value?:string|null)=>value?new Intl.DateTimeFormat('tr-TR',{day:'2-digit',month:'short'}).format(new Date(value)):'—'
const day=(value:string)=>new Intl.DateTimeFormat('tr-TR',{weekday:'short'}).format(new Date(`${value}T12:00:00`))
const initials=(item:AdminUser)=>`${item.firstName?.[0]||''}${item.lastName?.[0]||item.company?.[0]||'Q'}`.toUpperCase()
function applyAccount(account:UserOverview['account']){
  start.value=toInput(account.licenseStart); end.value=toInput(account.licenseEnd)
  frozenUntil.value=toInput(account.frozenUntil); status.value=account.status||'active'
}
async function load(silent=false){
  if(!hasAdminKey()){ router.push('/yonetici'); return }
  if(!silent) loading.value=true
  error.value=''
  try{
    overview.value=await fetchAdminOverview()
    if(selectedId.value && overview.value.users.some(u=>u.id===selectedId.value)) await selectUser(selectedId.value,false)
    else if(selectedId.value){ selectedId.value=null; detail.value=null }
  }catch(e){ error.value=e instanceof Error?e.message:'Veriler alınamadı' }
  finally{ loading.value=false }
}
async function selectUser(id:number,resetError=true){
  selectedId.value=id; selecting.value=true
  if(resetError) error.value=''
  try{
    detail.value=await fetchAdminUser(id)
    applyAccount(detail.value.account)
  }catch(e){ error.value=e instanceof Error?e.message:'İşletme bilgileri alınamadı' }
  finally{ selecting.value=false }
}
async function save(){
  if(!selectedId.value) return
  saving.value=true; error.value=''
  try{
    await saveAdminUserSchedule(selectedId.value,{licenseStart:new Date(start.value).toISOString(),licenseEnd:new Date(end.value).toISOString(),status:status.value,frozenUntil:status.value==='frozen'&&frozenUntil.value?new Date(frozenUntil.value).toISOString():null})
    saved.value=true; await load(true); setTimeout(()=>saved.value=false,1800)
  }catch(e){ error.value=e instanceof Error?e.message:'Kaydedilemedi' }
  finally{ saving.value=false }
}
function askDelete(item:AdminUser,event?:Event){
  event?.stopPropagation()
  if(item.protected) return
  pendingDelete.value=item
}
async function confirmDelete(){
  if(!pendingDelete.value) return
  deleting.value=true; error.value=''
  try{
    const id=pendingDelete.value.id
    await deleteAdminUser(id)
    if(selectedId.value===id){ selectedId.value=null; detail.value=null }
    pendingDelete.value=null
    await load(true)
  }catch(e){ error.value=e instanceof Error?e.message:'Silinemedi' }
  finally{ deleting.value=false }
}
const logIcon=(item:AuditItem)=>item.action.includes('login')?Users:item.action.includes('schedule')||item.action.includes('admin')?CalendarClock:item.action.includes('product')?Package:item.action.includes('deleted')?Trash2:item.action.includes('registered')?Users:Activity
onMounted(load)
</script>

<template><div class="hq">
  <header class="hero">
    <div>
      <span>SİSTEM KONTROLÜ</span>
      <h2>Kayıtlar, zamanlama, silme.</h2>
      <p>Tüm işletmeleri görün, birini seçin, süresini ayarlayın veya kaydı kaldırın.</p>
    </div>
    <button class="ghost" @click="load()"><RefreshCw :size="16"/> Yenile</button>
  </header>

  <p v-if="error" class="banner error">{{error}}</p>
  <div v-if="loading" class="loading">Yönetim verileri hazırlanıyor...</div>

  <template v-else-if="overview">
    <section class="stats">
      <article><small>Kayıtlı işletme</small><strong>{{overview.metrics.businesses}}</strong><Users :size="18"/></article>
      <article><small>Aktif yayın</small><strong>{{overview.metrics.active}}</strong><ShieldCheck :size="18"/></article>
      <article><small>Dondurulmuş</small><strong>{{overview.metrics.frozen}}</strong><Power :size="18"/></article>
      <article><small>Toplam görüntüleme</small><strong>{{overview.metrics.views.toLocaleString('tr-TR')}}</strong><Eye :size="18"/></article>
    </section>

    <div class="workspace">
      <section class="panel list-panel">
        <header>
          <div><span>KAYITLI İŞLETMELER</span><h3>Bir hesap seçin</h3></div>
          <b>{{users.length}}</b>
        </header>
        <div class="search"><Search :size="16"/><input v-model="query" placeholder="Ad, işletme, e-posta veya telefon"/></div>
        <div class="people">
          <button v-for="item in users" :key="item.id" type="button" class="person" :class="{on:item.id===selectedId}" @click="selectUser(item.id)">
            <span class="face">{{initials(item)}}</span>
            <span class="who">
              <strong>{{item.company}}</strong>
              <small>{{item.fullName}}</small>
              <em>{{item.email}}</em>
            </span>
            <span class="bits">
              <i :class="item.status">{{item.status==='frozen'?'Donduruldu':'Yayında'}}</i>
              <small>{{item.licenseDaysRemaining}} gün · {{formatDay(item.registeredAt)}}</small>
            </span>
            <span v-if="!item.protected" class="kill" title="Sil" @click="askDelete(item,$event)"><Trash2 :size="15"/></span>
          </button>
          <div v-if="!users.length" class="empty">Kayıt bulunamadı.</div>
        </div>
      </section>

      <section class="panel side-panel">
        <header>
          <div><span>ZAMANLANDIRMA</span><h3>{{selected?selected.company:'İşletme seçin'}}</h3></div>
          <CalendarClock :size="20"/>
        </header>
        <div v-if="!selected" class="empty tall">Soldan bir kayıt seçin. Süre ve silme yalnızca seçtiğiniz hesaba uygulanır.</div>
        <form v-else @submit.prevent="save">
          <div class="chip-row">
            <span>{{selected.fullName}}</span>
            <code>/menu/{{selected.slug}}</code>
          </div>
          <div class="dates"><label>Başlangıç<input v-model="start" type="datetime-local" required/></label><label>Bitiş<input v-model="end" type="datetime-local" required/></label></div>
          <div class="toggles">
            <button type="button" :class="{on:status==='active'}" @click="status='active'"><Check :size="16"/><b>Aktif</b></button>
            <button type="button" :class="{on:status==='frozen'}" @click="status='frozen'"><Power :size="16"/><b>Dondur</b></button>
          </div>
          <label v-if="status==='frozen'" class="later">Otomatik açılma<input v-model="frozenUntil" type="datetime-local"/><small>Boş bırakırsanız siz açana kadar kapalı kalır.</small></label>
          <button class="save" :disabled="saving||selecting"><Check v-if="saved" :size="16"/><Save v-else :size="16"/>{{saved?'Kaydedildi':saving?'Kaydediliyor...':'Bu hesaba kaydet'}}</button>
          <button v-if="!selected.protected" type="button" class="danger" @click="askDelete(selected)"><Trash2 :size="16"/> Bu kaydı sil</button>
        </form>
      </section>
    </div>

    <template v-if="detail && selected">
      <section class="selected-bar">
        <div><i :class="detail.account.status"></i><small>SEÇİLEN HESAP</small><strong>{{detail.account.status==='active'?'Yayında':'Donduruldu'}}</strong></div>
        <div><small>YETKİLİ</small><strong>{{detail.account.fullName}}</strong><em>{{detail.account.email}}</em></div>
        <div><small>QR ADRESİ</small><strong>/menu/{{detail.account.slug}}</strong><em>{{detail.account.phone||'Telefon yok'}}</em></div>
        <div><small>SON GİRİŞ</small><strong>{{formatDate(selected.lastLogin)}}</strong><em>{{formatDate(detail.account.registeredAt)}} kayıt</em></div>
      </section>
      <section class="mini-stats">
        <article><Eye :size="16"/><div><small>QR görüntüleme</small><strong>{{detail.metrics.totalViews.toLocaleString('tr-TR')}}</strong></div></article>
        <article><Package :size="16"/><div><small>Ürün</small><strong>{{detail.metrics.products}}</strong></div></article>
        <article><Users :size="16"/><div><small>Oturum</small><strong>{{detail.metrics.sessions}}</strong></div></article>
        <article><Clock3 :size="16"/><div><small>Kalan gün</small><strong>{{detail.account.licenseDaysRemaining}}</strong></div></article>
      </section>
      <div class="workspace">
        <section class="panel">
          <header><div><span>QR ANALİTİĞİ</span><h3>Son 7 gün</h3></div><QrCode :size="18"/></header>
          <div class="chart"><div v-for="item in detail.dailyViews" :key="item.date"><b>{{item.count}}</b><i :style="{height:`${Math.max(8,item.count/maxView*100)}%`}"></i><small>{{day(item.date)}}</small></div></div>
        </section>
        <section class="panel">
          <header><div><span>HAREKETLER</span><h3>Bu hesabın kayıtları</h3></div><b>{{detail.logs.length}}</b></header>
          <div class="logs">
            <div v-for="item in detail.logs" :key="item.id" class="log">
              <i><component :is="logIcon(item)" :size="14"/></i>
              <div><strong>{{actionNames[item.action]||item.action}}</strong><small>{{item.detail||'—'}}</small></div>
              <time>{{formatDate(item.createdAt)}}</time>
            </div>
            <div v-if="!detail.logs.length" class="empty">Bu işletme için henüz hareket yok.</div>
          </div>
        </section>
      </div>
    </template>
  </template>

  <div v-if="pendingDelete" class="overlay" @click.self="pendingDelete=null">
    <div class="modal">
      <button class="close" type="button" @click="pendingDelete=null"><X :size="16"/></button>
      <span class="warn"><AlertTriangle :size="22"/></span>
      <h3>{{pendingDelete.company}} silinsin mi?</h3>
      <p>{{pendingDelete.fullName}} hesabı, menüsü, ürünleri ve oturumları kalıcı olarak kalkacak.</p>
      <div class="modal-actions">
        <button type="button" @click="pendingDelete=null">Vazgeç</button>
        <button type="button" class="yes" :disabled="deleting" @click="confirmDelete">{{deleting?'Siliniyor...':'Evet, sil'}}</button>
      </div>
    </div>
  </div>
</div></template>

<style scoped>
.hq{--mint:#f0a36a;--line:#ffffff14;max-width:1460px;margin:auto;color-scheme:dark}
.hero{display:flex;justify-content:space-between;align-items:end;gap:18px;margin-bottom:22px}
.hero span,.panel header span{font-size:9px;letter-spacing:1.8px;color:var(--mint);font-weight:800}
.hero h2{font-size:34px;margin:8px 0 6px;letter-spacing:-.8px}
.hero p{margin:0;color:#b8aaa0;font-size:13px}
.ghost,.save,.danger,.toggles button,.modal-actions button,.person,.kill,.close{cursor:pointer}
.ghost{height:42px;padding:0 14px;border:1px solid var(--line);border-radius:12px;background:#ffffff0d;color:#f6eee7;display:flex;align-items:center;gap:8px;font-size:11px;font-weight:700}
.banner{padding:12px 14px;border-radius:12px;margin-bottom:14px;font-size:12px}
.banner.error{background:#3a1714;color:#ffb4a8}
.loading{padding:90px;text-align:center;color:#b8aaa0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
.stats article{position:relative;overflow:hidden;padding:18px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(180deg,#2a221c,#1c1713);display:flex;flex-direction:column;gap:6px}
.stats small{font-size:10px;color:#b5a79c}
.stats strong{font-size:28px}
.stats svg{position:absolute;right:16px;top:16px;color:#f0a36aa6}
.workspace{display:grid;grid-template-columns:1.2fr .8fr;gap:14px;margin-bottom:14px}
.panel{border:1px solid var(--line);border-radius:20px;background:#241e19cc;backdrop-filter:blur(16px);overflow:hidden;box-shadow:0 18px 50px #120c0855}
.panel>header{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line)}
.panel h3{margin:4px 0 0;font-size:16px}
.panel header b{min-width:28px;height:28px;border-radius:9px;background:#f0a36a1a;color:var(--mint);display:grid;place-items:center;font-size:11px}
.panel header svg{color:var(--mint)}
.search{margin:14px 16px 0;height:44px;border:1px solid var(--line);border-radius:14px;background:#181410;display:flex;align-items:center;gap:8px;padding:0 13px;color:#b5a79c}
.search input,.dates input,.later input{width:100%;border:0;outline:0;background:transparent;color:#f6eee7;font:inherit}
.people{max-height:460px;overflow:auto;padding:10px}
.person{width:100%;border:1px solid transparent;background:transparent;color:inherit;border-radius:16px;padding:12px;display:grid;grid-template-columns:44px 1fr auto 34px;gap:10px;align-items:center;text-align:left}
.person:hover{background:#ffffff08}
.person.on{border-color:#f0a36a4d;background:#f0a36a12}
.face{width:44px;height:44px;border-radius:14px;background:linear-gradient(180deg,#f17e45,#9a4320);display:grid;place-items:center;font-size:12px;font-weight:800}
.who,.bits{min-width:0}
.who strong,.who small,.who em,.bits i,.bits small{display:block}
.who strong{font-size:13px}
.who small{margin-top:3px;font-size:11px;color:#efe4d8}
.who em{margin-top:2px;font-size:10px;color:#b5a79c;font-style:normal}
.bits{text-align:right}
.bits i{font-size:10px;font-style:normal;color:var(--mint);font-weight:800}
.bits i.frozen{color:#ffb089}
.bits small{margin-top:4px;font-size:9px;color:#b5a79c}
.kill{width:34px;height:34px;border:0;border-radius:10px;background:#ff8a7614;color:#ffb4a2;display:grid;place-items:center}
.kill:hover{background:#ff8a7630}
.side-panel form{padding:18px 20px 20px}
.chip-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.chip-row span,.chip-row code{font-size:11px;padding:7px 10px;border-radius:999px;background:#ffffff0d;color:#efe4d8}
.dates{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.dates label,.later{font-size:10px;font-weight:700;color:#b8aaa0}
.dates input,.later input{height:42px;margin-top:7px;border:1px solid var(--line)!important;border-radius:12px;padding:0 11px;background:#181410!important}
.toggles{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:14px 0}
.toggles button{height:46px;border:1px solid var(--line);border-radius:14px;background:#181410;color:#b8aaa0;display:flex;align-items:center;justify-content:center;gap:8px}
.toggles button.on{border-color:#f0a36a66;background:#f0a36a16;color:var(--mint)}
.later small{display:block;margin-top:6px;font-size:9px;color:#b5a79c}
.save,.danger{width:100%;height:44px;border:0;border-radius:14px;display:flex;align-items:center;justify-content:center;gap:8px;font-size:12px;font-weight:800;margin-top:12px}
.save{background:linear-gradient(135deg,#f17e45,#d95a20);color:#fff}
.danger{background:#3a1714;color:#ffb4a8}
.empty{padding:42px 20px;text-align:center;color:#b5a79c;font-size:12px}
.empty.tall{min-height:280px;display:grid;place-items:center}
.selected-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:4px 0 14px;padding:18px 20px;border-radius:20px;background:linear-gradient(120deg,#1c1612,#3a2418);border:1px solid var(--line)}
.selected-bar small,.selected-bar em{display:block;font-size:9px;color:#b5a79c;font-style:normal}
.selected-bar strong{display:block;margin:5px 0 3px;font-size:13px}
.selected-bar i{display:inline-block;width:8px;height:8px;border-radius:50%;background:#f0a36a;margin-right:7px;box-shadow:0 0 0 4px #f0a36a18}
.selected-bar i.frozen{background:#ffb089;box-shadow:0 0 0 4px #ffb08918}
.mini-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.mini-stats article{display:flex;gap:10px;align-items:center;padding:14px;border-radius:16px;border:1px solid var(--line);background:#241e19}
.mini-stats svg{color:var(--mint)}
.mini-stats small{display:block;font-size:9px;color:#b5a79c}
.mini-stats strong{font-size:20px}
.chart{height:230px;padding:30px 24px 18px;display:flex;align-items:end;gap:12px}
.chart>div{flex:1;height:100%;display:flex;flex-direction:column;justify-content:end;align-items:center;gap:6px}
.chart i{width:min(36px,70%);min-height:8px;border-radius:10px 10px 4px 4px;background:linear-gradient(#f4c49a,#e86e35)}
.chart b,.chart small{font-size:9px;color:#b5a79c}
.logs{max-height:280px;overflow:auto}
.log{display:grid;grid-template-columns:32px 1fr auto;gap:10px;align-items:center;padding:12px 18px;border-top:1px solid var(--line)}
.log i{width:32px;height:32px;border-radius:10px;background:#f0a36a14;color:var(--mint);display:grid;place-items:center}
.log strong,.log small{display:block}
.log small{margin-top:3px;font-size:10px;color:#b5a79c}
.log time{font-size:10px;color:#b5a79c;white-space:nowrap}
.overlay{position:fixed;inset:0;z-index:50;background:#120c08cc;display:grid;place-items:center;padding:20px}
.modal{position:relative;width:min(420px,100%);padding:28px 24px 22px;border-radius:22px;background:#2a211c;border:1px solid #ffffff1a;box-shadow:0 30px 80px #00000080;text-align:center}
.close{position:absolute;top:12px;right:12px;width:32px;height:32px;border:0;border-radius:10px;background:#ffffff10;color:#efe4d8;display:grid;place-items:center}
.warn{width:48px;height:48px;margin:0 auto 12px;border-radius:16px;background:#3a1714;color:#ffb4a8;display:grid;place-items:center}
.modal h3{margin:0 0 8px;font-size:20px}
.modal p{margin:0 0 18px;color:#b8aaa0;font-size:13px;line-height:1.5}
.modal-actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.modal-actions button{height:44px;border:0;border-radius:12px;background:#ffffff12;color:#f6eee7;font-weight:800}
.modal-actions .yes{background:#c2412d;color:#fff}
@media(max-width:1000px){.stats,.mini-stats,.selected-bar,.workspace{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.hero{flex-direction:column;align-items:stretch}.stats,.mini-stats,.selected-bar,.workspace,.dates,.toggles,.modal-actions{grid-template-columns:1fr}.person{grid-template-columns:44px 1fr 34px}.bits{display:none}.ghost{justify-content:center}}
</style>

