<script setup lang="ts">
import { LogOut, ShieldCheck } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="management-shell">
    <div class="glow glow-a"></div><div class="glow glow-b"></div>
    <header class="management-nav">
      <RouterLink to="/yonetim" class="management-brand">
        <span><ShieldCheck :size="20" /></span>
        <div><small>QR MENÜ</small><strong>Yönetim Merkezi</strong></div>
      </RouterLink>
      <nav>
        <RouterLink to="/giris" class="logout"><LogOut :size="17" /> Çıkış</RouterLink>
      </nav>
    </header>
    <main><slot /></main>
  </div>
</template>

<style scoped>
.management-shell{min-height:100vh;position:relative;overflow:hidden;background:#16110e;color:#f6eee7}
.glow{position:absolute;border-radius:50%;filter:blur(80px);pointer-events:none;z-index:0}
.glow-a{width:420px;height:420px;background:#e86e3530;top:-160px;right:-80px}
.glow-b{width:360px;height:360px;background:#5a2e1680;bottom:-120px;left:-90px}
.management-nav{position:relative;z-index:2;height:78px;padding:0 clamp(20px,4vw,64px);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ffffff12;background:#1c1612b8;backdrop-filter:blur(18px)}
.management-brand{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none}
.management-brand>span{width:42px;height:42px;border-radius:14px;background:linear-gradient(180deg,#f17e45,#c24b1c);display:grid;place-items:center;box-shadow:0 10px 24px #7a2f1466}
.management-brand small,.management-brand strong{display:block}
.management-brand small{font-size:8px;letter-spacing:1.8px;color:#d7b8a4}
.management-brand strong{font-size:15px;margin-top:3px}
.management-nav nav a{height:40px;padding:0 14px;border:1px solid #ffffff18;border-radius:12px;color:#f0e4da;text-decoration:none;font-size:11px;font-weight:700;display:flex;align-items:center;gap:7px;background:#ffffff08}
.management-nav nav a:hover{background:#ffffff12}
.management-nav nav .logout{color:#ffb4a2}
.management-shell main{position:relative;z-index:1;padding:28px clamp(20px,4vw,64px) 70px}
@media(max-width:600px){.management-nav{height:auto;padding-top:14px;padding-bottom:14px}}
</style>
