<script setup>
import {
    onMounted,
    ref,
    provide,
    inject,
    getCurrentInstance,
    watch,
} from "vue";
import NetworkError from "./components/NetworkError.vue";
import Reload from "./components/Reload.vue";
import Setting from "./components/Setting.vue";
import { darkTheme } from "naive-ui";
import { Buffer } from "buffer";
import { zhCN, dateZhCN, enUS, dateEnUS } from "naive-ui";
import { useI18n } from "vue-i18n";

const { locale } = useI18n({ useScope: "global" });

const darkMode = ref(false);
provide("darkMode", darkMode);

const instance = getCurrentInstance();
const axios = instance.appContext.config.globalProperties.$axios;

const allDicts = ref(null);
provide("allDicts", allDicts);

const networkAvailable = inject("networkAvailable");

const fetchThumbail = async (d) => {
    return await axios
        .get("/thumbail", { params: { d: d }, responseType: "arraybuffer" })
        .then((response) => {
            if (response.data) {
                let content_type = response.headers["content-type"];
                return (
                    `data:${content_type};base64,` +
                    Buffer.from(response.data, "binary").toString("base64")
                );
            }
        });
};

const fetchDicts = () => {
    axios
        .get("/dicts", { withNetwork: true })
        .then((response) => {
            if (response.data.lst) {
                networkAvailable.value = true;
                allDicts.value = response.data.lst;
                allDicts.value.map(async (item, index) => {
                    item.thumbail = await fetchThumbail(index);
                });
            }
        })
        .catch((error) => {
            if (!networkAvailable.value) {
                setTimeout(() => {
                    fetchDicts();
                }, 1000);
            }
        });
};

onMounted(() => {
    fetchDicts();
    if (
        sessionStorage.getItem("darkmode_mydict") === "true" ||
        (window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
        darkMode.value = true;
    }
    if (sessionStorage.getItem("locale_mydict")) {
        locale = sessionStorage.getItem("locale_mydict");
    }
});

const langConfig = computed(() => {
    return {
        en: {
            locale: enUS,
            dateLocale: dateEnUS,
        },
        zh: {
            locale: zhCN,
            dateLocale: dateZhCN,
        },
    };
});

watch(locale, (val) => {
    document.documentElement.setAttribute("lang", val);
});
</script>

<template>
    <n-config-provider
        :theme="darkMode ? darkTheme : null"
        :locale="langConfig[locale].locale"
        :date-locale="langConfig[locale].dateLocale"
    >
        <n-notification-provider>
            <n-dialog-provider>
                <setting />
                <reload />
                <network-error />
                <router-view />
            </n-dialog-provider>
        </n-notification-provider>
    </n-config-provider>
</template>

<style>
html,
body,
div#app {
    height: 100%;
    width: 100%;
    margin: 0;
}
</style>
