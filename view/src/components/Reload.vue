<script setup lang="jsx">
import { useRegisterSW } from "virtual:pwa-register/vue";
import { ArrowAltCircleUpRegular } from "@vicons/fa";
import { useNotification } from "naive-ui";
import { ref } from "vue";

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
            content: () => (
                <div class="flex flex-col gap-y-2">
                    Click YES below to upgrade the APP now.
                    <div class="flex justify-end">
                        <n-button
                            on-click={close}
                            strong
                            secondary
                            type="tertiary"
                        >
                            No
                        </n-button>
                        <n-button
                            on-click={doRefresh}
                            strong
                            secondary
                            type="success"
                        >
                            Yes
                        </n-button>
                    </div>
                </div>
            ),
            avatar: () => (
                <n-icon size="1.5rem" color="#0ea5e9">
                    <ArrowAltCircleUpRegular />
                </n-icon>
            ),
        });
    }
});
</script>

<template></template>
