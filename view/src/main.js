import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import axios from "./axios"

import "./assets/index.css";
import "vfonts/Inter.css";

const app = createApp(App);

app.use(router);
app.use(axios)

app.mount("#app");
