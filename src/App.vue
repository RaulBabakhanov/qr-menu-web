<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from './layouts/AdminLayout.vue'

const route = useRoute()
const isPublicMenu = computed(() => route.path.startsWith('/menu/'))
const isLogin = computed(() => route.path === '/giris')
</script>

<template>
  <AdminLayout v-if="!isPublicMenu && !isLogin"><router-view /></AdminLayout>
  <router-view v-else />
</template>
