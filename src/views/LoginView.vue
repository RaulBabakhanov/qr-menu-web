<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight, Check, Eye, EyeOff, Mail, QrCode, UserPlus, UtensilsCrossed } from 'lucide-vue-next'
import '../login.css'
import '../login-font.css'
import { loginAccount, registerAccount } from '../services/auth'

type Mode = 'login' | 'forgot' | 'register'
const router = useRouter()
const mode = ref<Mode>('login'), email = ref(''), password = ref(''), remember = ref(true), showPassword = ref(false), error = ref('')
const resetEmail = ref(''), resetSent = ref(false)
const company = ref(''), firstName = ref(''), lastName = ref(''), phone = ref(''), registerEmail = ref(''), registerPassword = ref('')

async function login() {
  if (!email.value.trim() || !password.value.trim()) { error.value = 'E-posta ve şifre alanlarını doldurun.'; return }
  try { await loginAccount(email.value.trim(),password.value); error.value=''; router.push('/admin') }
  catch(e) { error.value=e instanceof Error?e.message:'Giriş yapılamadı.' }
}
function changeMode(next: Mode) { mode.value = next; error.value = ''; resetSent.value = false; if (next === 'forgot') resetEmail.value = email.value }
function sendReset() { if (resetEmail.value.trim()) resetSent.value = true }
async function register() {
  if (!company.value || !firstName.value || !lastName.value || !registerEmail.value || !registerPassword.value) return
  try { await registerAccount({company:company.value.trim(),firstName:firstName.value.trim(),lastName:lastName.value.trim(),email:registerEmail.value.trim(),phone:phone.value.trim(),password:registerPassword.value}); router.push('/admin') }
  catch(e) { error.value=e instanceof Error?e.message:'Kayıt oluşturulamadı.' }
}
</script>

<template>
  <div class="login-page">
    <div class="login-overlay"></div>
    <header class="login-top"><div class="login-brand"><span><UtensilsCrossed :size="20" /></span><strong>QR Menü<i>.</i></strong></div></header>
    <section class="login-intro"><h1>Menünüz her zaman<br /><em>masada.</em></h1></section>

    <main class="login-card" :class="{ 'register-card': mode === 'register' }">
      <template v-if="mode === 'login'">
        <div class="card-mark"><QrCode :size="21" /></div>
        <div class="login-heading"><span>YÖNETİM PANELİ</span><h2>Hoş geldiniz</h2><p>Hesabınıza giriş yaparak menünüzü yönetin.</p></div>
        <form @submit.prevent="login">
          <label>E-posta<input v-model="email" type="email" placeholder="ornek@restoran.com" autocomplete="email" /></label>
          <label>Şifre<div class="password-field"><input v-model="password" :type="showPassword ? 'text' : 'password'" placeholder="Şifrenizi girin" autocomplete="current-password" /><button type="button" @click="showPassword=!showPassword"><EyeOff v-if="showPassword" :size="18"/><Eye v-else :size="18"/></button></div></label>
          <div class="login-options"><label><input v-model="remember" type="checkbox"/><span>Beni hatırla</span></label><button type="button" class="text-action" @click="changeMode('forgot')">Şifrenizi mi unuttunuz?</button></div>
          <p v-if="error" class="login-error">{{ error }}</p>
          <button class="login-submit" type="submit">Giriş yap <ArrowRight :size="18"/></button>
        </form>
        <p class="account-switch">Henüz hesabınız yok mu? <button @click="changeMode('register')">Kayıt ol</button></p>
      </template>

      <template v-else-if="mode === 'forgot'">
        <div class="card-mark"><Mail :size="21" /></div>
        <div class="login-heading reset-heading"><span>ŞİFRE YENİLEME</span><h2>Şifrenizi mi unuttunuz?</h2><p>E-posta adresinizi girin, sıfırlama bağlantısını gönderelim.</p></div>
        <div v-if="resetSent" class="reset-success"><span><Check :size="20"/></span><strong>Bağlantı gönderildi</strong><p>{{ resetEmail }} adresinin gelen kutusunu kontrol edin.</p></div>
        <form v-else @submit.prevent="sendReset"><label>E-posta<input v-model="resetEmail" type="email" placeholder="ornek@restoran.com" required /></label><button class="login-submit" type="submit">Şifre sıfırlama bağlantısı gönder <ArrowRight :size="18"/></button></form>
        <button class="back-login" @click="changeMode('login')"><ArrowLeft :size="15"/> Girişe dön</button>
      </template>

      <template v-else>
        <div class="card-mark"><UserPlus :size="21" /></div>
        <div class="login-heading register-heading"><span>YENİ HESAP</span><h2>QR Menü hesabınızı oluşturun</h2><p>Tüm menülerinizi tek panelden dijitale taşıyın.</p></div>
        <form class="register-form" @submit.prevent="register">
          <label>Firma ticari ünvanı<input v-model="company" placeholder="Restoran veya firma adı" required /></label>
          <div class="register-grid"><label>Ad<input v-model="firstName" placeholder="Adınız" required /></label><label>Soyad<input v-model="lastName" placeholder="Soyadınız" required /></label></div>
          <label>E-posta<input v-model="registerEmail" type="email" placeholder="ornek@restoran.com" required /></label>
          <label>Cep telefonu<input v-model="phone" type="tel" placeholder="05XX XXX XX XX" /></label>
          <label>Şifre<input v-model="registerPassword" type="password" placeholder="En az 6 karakter" minlength="6" required /></label>
          <button class="login-submit" type="submit">Hesabımı oluştur <ArrowRight :size="18"/></button>
        </form>
        <button class="back-login" @click="changeMode('login')"><ArrowLeft :size="15"/> Girişe dön</button>
      </template>
    </main>
  </div>
</template>
