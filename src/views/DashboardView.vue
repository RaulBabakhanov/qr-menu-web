<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { ArrowUpRight, Clock3, Eye, Package, QrCode, Sparkles, TrendingUp } from 'lucide-vue-next'
import { getStocks } from '../services/stocks'
import { getLastUpdated, getMenuViews } from '../services/dashboard'

const stocks = ref(getStocks())
const activeStocks = computed(() => stocks.value.filter(stock => stock.status === 'active'))
const menuViews = ref(getMenuViews())
const profileName = ref(localStorage.getItem('qr-menu-profile-name') || '')
const money = (value: number) => `${value.toLocaleString('tr-TR')} ₺`
const today = new Intl.DateTimeFormat('tr-TR', { day: 'numeric', month: 'long', weekday: 'long' }).format(new Date())
const lastUpdated = computed(() => {
  const value = getLastUpdated()
  if (!value) return 'Henüz yok'
  const minutes = Math.max(1, Math.round((Date.now() - new Date(value).getTime()) / 60000))
  return minutes < 60 ? `${minutes} dk.` : `${Math.round(minutes / 60)} sa.`
})
function syncProfileName() { profileName.value = localStorage.getItem('qr-menu-profile-name') || '' }
onMounted(() => { window.addEventListener('qr-menu-profile-updated', syncProfileName); stocks.value = getStocks(); menuViews.value = getMenuViews() })
onUnmounted(() => window.removeEventListener('qr-menu-profile-updated', syncProfileName))
</script>

<template>
  <div class="dashboard-page">
    <section class="dashboard-hero">
      <div><span class="day-label">{{ today }}</span><h2>Hoş geldiniz{{ profileName ? `, ${profileName}` : '' }} <Sparkles :size="20" /></h2><p>İşletmenizin bugünkü durumuna hızlıca göz atın.</p></div>
      <RouterLink to="/admin/qr-menu" class="open-menu"><QrCode :size="18" /> QR menüyü aç <ArrowUpRight :size="16" /></RouterLink>
    </section>

    <section class="stats-grid">
      <article class="stat-card"><span class="stat-icon orange"><Package :size="20" /></span><div><small>Toplam ürün</small><strong>{{ stocks.length }}</strong><p><b>{{ activeStocks.length }}</b> aktif ürün</p></div><span class="stat-trend"><TrendingUp :size="14"/> Güncel</span></article>
      <article class="stat-card"><span class="stat-icon green"><Eye :size="20" /></span><div><small>Menü görüntülenme</small><strong>{{ menuViews.toLocaleString('tr-TR') }}</strong><p>QR menü açılış sayısı</p></div><span class="stat-trend green-text">Canlı</span></article>
      <article class="stat-card"><span class="stat-icon blue"><Clock3 :size="20" /></span><div><small>Son güncelleme</small><strong>{{ lastUpdated }}</strong><p>Ürün ve menü işlemleri</p></div></article>
    </section>

    <section class="dashboard-grid" style="grid-template-columns:1fr">
      <article class="dash-panel recent-panel">
        <header><div><h3>Son eklenen ürünler</h3><p>Menünüzdeki son değişiklikler</p></div><RouterLink to="/admin/stoklar">Tümünü gör <ArrowUpRight :size="15" /></RouterLink></header>
        <div v-if="stocks.length" class="stock-list">
          <div v-for="stock in stocks.slice(0,4)" :key="stock.id" class="stock-row">
            <div class="stock-photo"><img v-if="stock.image" :src="stock.image" :alt="stock.name"/><Package v-else :size="20"/></div>
            <div class="stock-info"><strong>{{ stock.name }}</strong><small>{{ stock.category }}</small></div>
            <span :class="['stock-status',{ passive:stock.status!=='active' }]"><i></i>{{ stock.status==='active'?'Aktif':'Pasif' }}</span>
            <b class="stock-price">{{ money(stock.price) }}</b>
          </div>
        </div>
        <div v-else class="no-stock"><Package :size="26"/><span>Henüz ürün eklenmemiş</span></div>
      </article>

    </section>
  </div>
</template>

<style scoped>
.dashboard-page{max-width:1400px;margin:auto}.dashboard-hero{display:flex;align-items:flex-end;justify-content:space-between;gap:25px;margin-bottom:28px}.day-label{display:block;color:var(--orange);font-size:10px;text-transform:uppercase;letter-spacing:1.4px;font-weight:800;margin-bottom:12px}.dashboard-hero h2{display:flex;align-items:center;gap:9px;font-size:30px;letter-spacing:-1px;margin:0 0 8px}.dashboard-hero h2 svg{color:var(--orange)}.dashboard-hero p{font-size:13px;color:var(--muted);margin:0}.open-menu{height:44px;display:flex;align-items:center;gap:9px;padding:0 16px;border-radius:11px;background:#202522;color:#fff;text-decoration:none;font-size:12px;font-weight:700;box-shadow:0 8px 18px #2025221f;transition:.2s}.open-menu:hover{background:var(--orange);transform:translateY(-2px)}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:18px}.stat-card{min-height:132px;background:#fff;border:1px solid var(--line);border-radius:15px;padding:22px;display:flex;align-items:flex-start;gap:15px;position:relative;box-shadow:0 5px 20px #2025220a}.stat-icon{width:43px;height:43px;border-radius:12px;display:grid;place-items:center;flex:none}.stat-icon.orange{color:#dc622d;background:#fff0e9}.stat-icon.green{color:#159465;background:#e9f8f1}.stat-icon.blue{color:#3979a9;background:#eaf4fb}.stat-card small{display:block;color:#8b948e;font-size:11px;margin-bottom:6px}.stat-card strong{display:block;font-size:25px;letter-spacing:-.7px}.stat-card p{font-size:10px;color:#9aa29c;margin:5px 0 0}.stat-card p b{color:#159465}.stat-trend{position:absolute;right:18px;top:18px;display:flex;align-items:center;gap:4px;background:#fff5ef;color:#d96532;padding:5px 7px;border-radius:7px;font-size:9px;font-weight:700}.stat-trend.green-text{background:#eaf8f1;color:#159465}
.dashboard-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(330px,.75fr);gap:18px}.dash-panel{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 6px 24px #2025220b;overflow:hidden}.dash-panel>header{display:flex;align-items:flex-start;justify-content:space-between;padding:22px 24px;border-bottom:1px solid var(--line)}.dash-panel h3{font-size:16px;margin:0 0 5px}.dash-panel header p{font-size:10px;color:var(--muted);margin:0}.dash-panel header>a{display:flex;align-items:center;gap:5px;color:var(--orange);font-size:10px;font-weight:700;text-decoration:none}.stock-row{min-height:78px;display:grid;grid-template-columns:50px 1fr 80px 85px;align-items:center;gap:13px;padding:11px 24px;border-bottom:1px solid #eef0ed}.stock-row:last-child{border-bottom:0}.stock-photo{width:48px;height:48px;border-radius:11px;background:#f2f4f1;color:#a3aba5;display:grid;place-items:center;overflow:hidden}.stock-photo img{width:100%;height:100%;object-fit:cover}.stock-info strong,.stock-info small{display:block}.stock-info strong{font-size:12px}.stock-info small{font-size:9px;color:#929a95;margin-top:4px}.stock-status{font-size:9px;font-weight:700;color:#159465;display:flex;align-items:center;gap:6px}.stock-status i,.live-badge i{width:6px;height:6px;border-radius:50%;background:currentColor}.stock-status.passive{color:#969e98}.stock-price{text-align:right;font-size:12px}.no-stock{height:280px;display:grid;place-items:center;align-content:center;gap:10px;color:#9aa29c;font-size:11px}
.live-badge{display:flex;align-items:center;gap:6px;padding:6px 9px;border-radius:8px;background:#eaf8f1;color:#159465;font-size:8px;font-weight:800;letter-spacing:.7px}.live-badge.offline{background:#f1f2f1;color:#8d958f}.chart-title{display:flex;justify-content:space-between;align-items:flex-end;padding:20px 24px 3px}.chart-title small,.chart-title strong{display:block}.chart-title small{font-size:9px;color:#939b95}.chart-title strong{font-size:27px;margin-top:3px}.chart-title>span{font-size:9px;color:#9aa29c}.mini-chart{height:115px;margin:8px 24px 0;border-bottom:1px solid var(--line);display:flex;align-items:flex-end;gap:7px;background:repeating-linear-gradient(to top,#f1f3f0 0,#f1f3f0 1px,transparent 1px,transparent 38px)}.mini-chart i{flex:1;min-height:8px;background:linear-gradient(#f39a6d,var(--orange));border-radius:5px 5px 0 0;opacity:.88}.chart-days{display:flex;justify-content:space-between;padding:7px 24px;color:#a0a7a2;font-size:8px}.manage-menu{margin:13px 20px 20px;border-radius:12px;padding:13px;background:#222824;color:#fff;text-decoration:none;display:flex;align-items:center;gap:11px}.manage-menu>span{flex:1}.manage-menu b,.manage-menu small{display:block}.manage-menu b{font-size:10px}.manage-menu small{font-size:8px;color:#9ca59e;margin-top:3px}
@media(max-width:1050px){.dashboard-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:700px){.dashboard-hero{align-items:stretch;flex-direction:column}.dashboard-hero h2{font-size:25px}.open-menu{justify-content:center}.stats-grid{grid-template-columns:1fr}.stock-row{grid-template-columns:48px 1fr auto}.stock-status{display:none}.stock-price{grid-column:3}}
</style>
