<script setup>
import { ref, provide, inject, watch } from "vue";
import { darkTheme } from "naive-ui";
import { Buffer } from "buffer";
import { zhCN, dateZhCN, enUS, dateEnUS } from "naive-ui";
import { useI18n } from "vue-i18n";
import Setting from "./components/Setting.vue";

const { locale } = useI18n({ useScope: "global" });

const darkMode = ref(false);
provide("darkMode", darkMode);

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
    locale.value = sessionStorage.getItem("locale_mydict");
}
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
