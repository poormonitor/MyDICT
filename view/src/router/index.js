import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'query',
      component: () => import("../views/Query.vue")
    },
  ]
})

export default router
