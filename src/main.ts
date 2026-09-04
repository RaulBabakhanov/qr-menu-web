import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/giris' },
    { path: '/giris', component: () => import('./views/LoginView.vue') },
    { path: '/admin', component: () => import('./views/DashboardView.vue') },
    { path: '/admin/stoklar', component: () => import('./views/StocksView.vue') },
    { path: '/admin/excel', component: () => import('./views/ExcelView.vue') },
    { path: '/admin/qr-menu', component: () => import('./views/QrMenuView.vue') },
    { path: '/admin/profil', component: () => import('./views/ProfileView.vue') },
    { path: '/admin/ayarlar', component: () => import('./views/MenuSettingsView.vue') },
    { path: '/admin/yonetim', component: () => import('./views/ManagementView.vue') },
    { path: '/menu/:slug', component: () => import('./views/PublicMenuView.vue') },
  ],
})

createApp(App).use(router).mount('#app')
