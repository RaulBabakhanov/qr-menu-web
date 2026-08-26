<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { FileSpreadsheet, LayoutDashboard, LogOut, Menu, Package, QrCode, UtensilsCrossed, X } from 'lucide-vue-next'
import '../profile.css'
import '../upgrade.css'

const route = useRoute(), open = ref(false), profileName = ref(localStorage.getItem('qr-menu-profile-name') || '')
const links = [
  { label:'Genel Bakış',to:'/admin',icon:LayoutDashboard },
  { label:'Ürünler',to:'/admin/stoklar',icon:Package },
  { label:'Excel Aktarımı',to:'/admin/excel',icon:FileSpreadsheet },
  { label:'QR Menü',to:'/admin/qr-menu',icon:QrCode }
]
const pageTitle = computed(() => route.path==='/admin'?'Genel Bakış':route.path.includes('stoklar')?'Ürünler':route.path.includes('excel')?'Excel Aktarımı':route.path.includes('profil')?'Profil':'QR Menü')
function syncName(){profileName.value=localStorage.getItem('qr-menu-profile-name')||''}
onMounted(()=>window.addEventListener('qr-menu-profile-updated',syncName))
onUnmounted(()=>window.removeEventListener('qr-menu-profile-updated',syncName))
</script>

<template>
<div class="admin-shell">
  <aside class="sidebar" :class="{'sidebar-open':open}">
    <div class="brand"><span class="brand-mark"><UtensilsCrossed :size="18"/></span><span>QR Menü<span class="brand-dot">.</span></span></div>
    <div class="workspace-label">YÖNETİM PANELİ</div>
    <nav><RouterLink v-for="link in links" :key="link.to" :to="link.to" class="nav-item" active-class="nav-active" @click="open=false"><component :is="link.icon" :size="18"/><span>{{link.label}}</span></RouterLink></nav>
    <div class="sidebar-bottom">
      <RouterLink to="/admin/qr-menu" class="upgrade-box"><span class="upgrade-icon"><QrCode :size="17"/></span><div><strong>Menünü paylaş</strong><small>QR kodun kullanıma hazır</small></div><span class="upgrade-arrow">→</span></RouterLink>
      <RouterLink to="/giris" class="nav-item login-link"><LogOut :size="18"/><span>Çıkış yap</span></RouterLink>
      <RouterLink to="/admin/profil" class="user user-link"><div class="avatar">{{profileName.slice(0,2).toUpperCase()||'QM'}}</div><div class="profile-copy"><small>İşletme hesabı</small><strong>{{profileName||'Profilinizi düzenleyin'}}</strong></div><span class="more">•••</span></RouterLink>
    </div>
  </aside>
  <div v-if="open" class="mobile-overlay" @click="open=false"></div>
  <main class="main-content">
    <header class="topbar"><button class="icon-button menu-button" @click="open=!open"><X v-if="open" :size="20"/><Menu v-else :size="20"/></button><div class="topbar-title"><span>QR MENÜ /</span><h1>{{pageTitle}}</h1></div><RouterLink to="/admin/profil" class="top-profile"><div><small>Hesabım</small><strong>{{profileName||'QR Menü'}}</strong></div><span>{{profileName.slice(0,2).toUpperCase()||'QM'}}</span></RouterLink></header>
    <section class="page-body"><slot/></section>
  </main>
</div>
</template>
