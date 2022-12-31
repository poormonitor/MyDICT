<script setup>
import { inject } from "vue";
import { NetworkWired } from "@vicons/fa";

const networkAvailable = inject("networkAvailable");
</script>

<template>
    <n-modal
        :show="!networkAvailable"
        :mask-closable="false"
        title="Network not available"
        content="The network is not available currently. Please check your connection."
        size="huge"
        :bordered="false"
        preset="dialog"
        role="dialog"
        aria-modal="true"
        :closable="false"
    >
    <template #icon>
        <n-icon class="text-red-600 mr-1" size="1.5rem"><NetworkWired /></n-icon>
    </template>
    </n-modal>
</template>
