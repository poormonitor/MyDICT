<script setup>
import { useRegisterSW } from "virtual:pwa-register/vue";
import { ArrowAltCircleUpRegular } from "@vicons/fa";
import { useNotification, NIcon, NButton } from "naive-ui";
import { ref, h } from "vue";

const notification = useNotification();
const { offlineReady, needRefresh, updateServiceWorker } = useRegisterSW({
    immediate: true,
    onRegistered(r) {
        r &&
            setInterval(async () => {
                await r.update();
            }, 60 * 60 * 1000);
    },
});

const isRefreshing = ref(false);
const doRefresh = () => {
    isRefreshing.value = true;
    updateServiceWorker();
};
const close = () => {
    offlineReady.value = false;
    needRefresh.value = false;
};

onMounted(() => {
    if (offlineReady.value || needRefresh.value) {
        notification.create({
            title: "New version available",
            content: () =>
                h(
                    "div",
                    { class: "flex flex-col gap-y-2" },
                    {
                        default: () => [
                            "Click YES below to upgrade the APP now.",
                            h(
                                "div",
                                { class: "flex justify-end" },
                                {
                                    default: () => [
                                        h(
                                            NButton,
                                            {
                                                onClick: close,
                                                strong: true,
                                                secondary: true,
                                                type: "tertiary",
                                            },
                                            { default: () => "No" }
                                        ),
                                        h(
                                            NButton,
                                            {
                                                onClick: doRefresh,
                                                strong: true,
                                                secondary: true,
                                                type: "success",
                                            },
                                            { default: () => "Yes" }
                                        ),
                                    ],
                                }
                            ),
                        ],
                    }
                ),
            avatar: () =>
                h(
                    NIcon,
                    { size: "1.5rem", color: "#0ea5e9" },
                    { default: () => h(ArrowAltCircleUpRegular) }
                ),
        });
    }
});
</script>

<template></template>