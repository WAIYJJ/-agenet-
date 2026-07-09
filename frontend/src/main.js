import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import TravelPlan from './views/TravelPlan.vue'

const routes = [{ path: '/', component: TravelPlan }]
const router = createRouter({ history: createWebHistory(), routes })

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')