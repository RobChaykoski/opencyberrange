import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import modalDialog from './directives/modalDialog'

const app = createApp(App)
app.use(router)
app.directive('modal-dialog', modalDialog)
app.mount('#app')
