<script setup>
import { onMounted, ref, provide, inject, getCurrentInstance } from "vue";
import NetworkError from "./components/NetworkError.vue";
import Reload from "./components/Reload.vue";
import { Buffer } from "buffer";

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
});
</script>

<template>
    <n-notification-provider>
        <reload />
        <network-error />
        <router-view />
    </n-notification-provider>
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
