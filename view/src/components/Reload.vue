<script setup lang="jsx">
import { useRegisterSW } from "virtual:pwa-register/vue";
import { ArrowAltCircleUpRegular } from "@vicons/fa";
import { useNotification } from "naive-ui";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n({ useScope: "global" });

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
            title: t("new-version"),
            content: () => (
                <div class="flex flex-col gap-y-2">
                    {t("new-help")}
                    <div class="flex justify-end">
                        <n-button
                            on-click={close}
                            strong
                            secondary
                            type="tertiary"
                        >
                            {t("yes")}
                        </n-button>
                        <n-button
                            on-click={doRefresh}
                            strong
                            secondary
                            type="success"
                        >
                            {t("no")}
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
