<script setup>
import { inject } from "vue";
import { NetworkWired } from "@vicons/fa";
import { useI18n } from "vue-i18n";

const { t } = useI18n({ useScope: "global" });

const networkAvailable = inject("networkAvailable");
</script>

<template>
    <n-modal
        :show="!networkAvailable"
        :mask-closable="false"
        :title="t('network-error')"
        :content="t('network-help')"
        size="huge"
        :bordered="false"
        preset="dialog"
        role="dialog"
        aria-modal="true"
        :closable="false"
    >
        <template #icon>
            <n-icon class="text-red-600 mr-1" size="1.5rem">
                <NetworkWired />
            </n-icon>
        </template>
    </n-modal>
</template>
