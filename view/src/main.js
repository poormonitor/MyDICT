import { createApp } from "vue";
import { createI18n } from "vue-i18n";
import App from "./App.vue";
import router from "./router";
import axios from "./axios";
import messages from "./i18n";
import "default-passive-events";

import "./assets/index.css";
import "vfonts/Inter.css";

const app = createApp(App);
const i18n = createI18n({
    legacy: false,
    locale: "zh",
    fallbackLocale: "en",
    messages,
});

app.use(router);
app.use(axios);
app.use(i18n);

app.mount("#app");
