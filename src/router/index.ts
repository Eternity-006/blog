import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/post/:slug',
      name: 'post',
      component: () => import('@/views/PostView.vue'),
    },
    {
      path: '/category/:category',
      name: 'category',
      component: () => import('@/views/CategoryView.vue'),
    },
    {
      path: '/tag/:tag',
      name: 'tag',
      component: () => import('@/views/TagView.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
    },
    {
      path: '/admin/:slug',
      name: 'admin-edit',
      component: () => import('@/views/AdminView.vue'),
    },
  ],
})

export default router
