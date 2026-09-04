<script setup lang="ts">
import { ArrowLeft, LogOut, ShieldCheck } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="management-shell">
    <header class="management-nav">
      <RouterLink to="/yonetim" class="management-brand">
        <span><ShieldCheck :size="20" /></span>
        <div><small>QR MENÜ</small><strong>Yönetim Merkezi</strong></div>
      </RouterLink>
      <nav>
        <RouterLink to="/admin"><ArrowLeft :size="17" /> İşletme paneline dön</RouterLink>
        <RouterLink to="/giris" class="logout"><LogOut :size="17" /> Çıkış</RouterLink>
      </nav>
    </header>
    <main><slot /></main>
  </div>
</template>

<style scoped>
.management-shell{min-height:100vh;background:#f4f5f2;color:var(--ink)}
.management-nav{height:76px;padding:0 clamp(20px,4vw,64px);background:#18201c;color:#fff;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff12}
.management-brand{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none}
.management-brand>span{width:40px;height:40px;border-radius:12px;background:var(--orange);display:grid;place-items:center}
.management-brand small,.management-brand strong{display:block}.management-brand small{font-size:8px;letter-spacing:1.8px;color:#98a59e}.management-brand strong{font-size:14px;margin-top:3px}
.management-nav nav{display:flex;align-items:center;gap:9px}.management-nav nav a{height:39px;padding:0 13px;border:1px solid #ffffff1c;border-radius:10px;color:#d8deda;text-decoration:none;font-size:10px;font-weight:700;display:flex;align-items:center;gap:7px}.management-nav nav a:hover{background:#ffffff0d}.management-nav nav .logout{color:#f3a07b}
.management-shell main{padding:30px clamp(20px,4vw,64px) 60px}
@media(max-width:600px){.management-nav{height:auto;padding-top:14px;padding-bottom:14px;align-items:flex-start}.management-nav nav{flex-direction:column;align-items:stretch}.management-nav nav a{height:34px}.management-nav nav a:first-child{font-size:0}.management-nav nav a:first-child::after{content:'Panele dön';font-size:10px}}
</style>
