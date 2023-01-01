<script setup lang="jsx">
import { useDialog } from "naive-ui";
import { inject, watch } from "vue";
import { Cog } from "@vicons/fa";
import { useI18n } from "vue-i18n";

const dialog = useDialog();
const { t, locale } = useI18n({ useScope: "global" });
const darkMode = inject("darkMode");

const showSetting = () => {
    dialog.create({
        title: t("setting"),
        content: () => (
            <n-form
                class="mt-8 mx-4"
                label-placement="left"
                label-width="6rem"
                label-align="left"
            >
                <n-form-item label={t("language")}>
                    <n-select
                        v-model:value={locale.value}
                        options={[
                            { label: "中文", value: "zh" },
                            { label: "English", value: "en" },
                        ]}
                    />
                </n-form-item>
                <n-form-item label={t("darkmode")}>
                    <n-switch v-model:value={darkMode.value} />
                </n-form-item>
            </n-form>
        ),
        icon: () => (
            <n-icon size="1.2rem">
                <Cog />
            </n-icon>
        ),
    });
};

watch(darkMode, (val) => {
    sessionStorage.setItem("darkmode_mydict", val);
});

watch(locale, (val) => {
    sessionStorage.setItem("lang_mydict", val);
});
</script>

<template>
    <div class="absolute right-4 bottom-4 lg:right-6 lg:top-6 z-10">
        <n-button @click="showSetting" circle>
            <template #icon>
                <n-icon size="large"><cog /></n-icon>
            </template>
        </n-button>
    </div>
</template>
