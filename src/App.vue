<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from './layouts/AdminLayout.vue'
import ManagementLayout from './layouts/ManagementLayout.vue'

const route = useRoute()
const isPublicMenu = computed(() => route.path.startsWith('/menu/'))
const isLogin = computed(() => route.path === '/giris')
const isManagement = computed(() => route.path === '/yonetim')
</script>

<template>
  <ManagementLayout v-if="isManagement"><router-view /></ManagementLayout>
  <AdminLayout v-else-if="!isPublicMenu && !isLogin"><router-view /></AdminLayout>
  <router-view v-else />
</template>
