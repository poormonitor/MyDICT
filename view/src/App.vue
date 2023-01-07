<script setup>
import { ref, provide, inject, watch } from "vue";
import NetworkError from "./components/NetworkError.vue";
import Reload from "./components/Reload.vue";
import Setting from "./components/Setting.vue";
import { darkTheme } from "naive-ui";
import { Buffer } from "buffer";
import { zhCN, dateZhCN, enUS, dateEnUS } from "naive-ui";
import { useI18n } from "vue-i18n";

const { locale } = useI18n({ useScope: "global" });

const axios = inject("axios");
const networkAvailable = inject("networkAvailable");

const darkMode = ref(false);
const allDicts = ref(null);

provide("darkMode", darkMode);
provide("allDicts", allDicts);

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
                sessionStorage.setItem("mydict_version", response.data.version);
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

fetchDicts();
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
