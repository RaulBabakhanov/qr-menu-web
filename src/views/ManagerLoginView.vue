<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { ArrowLeft, ArrowRight, Eye, EyeOff, LockKeyhole, ShieldCheck, UtensilsCrossed } from 'lucide-vue-next'
import '../login.css'
import '../login-font.css'
import { loginSystemAdmin } from '../services/systemAdmin'

const router=useRouter(),password=ref(''),show=ref(false),loading=ref(false),error=ref('')
async function login(){loading.value=true;error.value='';try{await loginSystemAdmin(password.value);router.push('/yonetim')}catch(e){error.value=e instanceof Error?e.message:'Giriş yapılamadı'}finally{loading.value=false}}
</script>

<template>
  <div class="login-page admin-login-page">
    <div class="login-overlay"></div>
    <header class="login-top">
      <div class="login-brand"><span><UtensilsCrossed :size="20" /></span><strong>QR Menü<i>.</i></strong></div>
      <RouterLink to="/giris" class="secure-note"><ArrowLeft :size="14"/> İşletme girişine dön</RouterLink>
    </header>
    <section class="login-intro"><h1>Kontrol her zaman<br /><em>elinizde.</em></h1></section>
    <main class="login-card">
      <div class="card-mark"><ShieldCheck :size="21" /></div>
      <div class="login-heading"><span>YÖNETİCİ GİRİŞİ</span><h2>Tekrar hoş geldiniz</h2><p>Devam etmek için yönetici şifrenizle giriş yapın.</p></div>
      <form @submit.prevent="login">
        <label>Yönetici şifresi<div class="password-field"><LockKeyhole :size="16"/><input v-model="password" :type="show?'text':'password'" placeholder="Şifrenizi girin" autocomplete="current-password" required/><button type="button" @click="show=!show"><EyeOff v-if="show" :size="18"/><Eye v-else :size="18"/></button></div></label>
        <p v-if="error" class="login-error">{{error}}</p>
        <button class="login-submit" type="submit" :disabled="loading">{{loading?'Doğrulanıyor...':'Panele giriş yap'}} <ArrowRight :size="18"/></button>
      </form>
    </main>
    <footer class="login-credit"><strong>Created by Raul Babakhanov</strong></footer>
  </div>
</template>
