<script setup lang="jsx">
import { Search } from "@vicons/fa";
import {
    ref,
    watch,
    onMounted,
    computed,
    inject,
    getCurrentInstance,
} from "vue";
import { useRoute, useRouter, onBeforeRouteUpdate } from "vue-router";
import { useI18n } from "vue-i18n";

const { t } = useI18n({ useScope: "global" });

const instance = getCurrentInstance();
const axios = instance.appContext.config.globalProperties.$axios;
const networkAvailable = inject("networkAvailable");
const darkMode = inject("darkMode");

const route = useRoute();
const router = useRouter();

const allDicts = inject("allDicts");
const availableDicts = ref([]);

const currentDict = ref();
const searchKeyword = ref("");
const queryKeyword = ref("");
const backKeyword = ref([]);

const inputRef = ref();
const iframeRef = ref([]);
const hint = ref([]);
const lastCheck = ref("");

const content = ref([]);

const collapsed = ref(window.innerWidth <= 768);

const loadingContent = ref(false);
const loadingHint = ref(false);

const loadHint = async () => {
    hint.value = [];
    if (!searchKeyword.value) {
        return;
    }
    loadingHint.value = true;
    let currentKey = searchKeyword.value;
    await axios
        .get("/hint", {
            params: { s: currentKey },
        })
        .then((response) => {
            if (response.data.lst && currentKey == searchKeyword.value) {
                loadingHint.value = false;
                hint.value = response.data.lst;
                lastCheck.value = searchKeyword.value;
            }
        });
};

const goQuery = async () => {
    if (queryKeyword.value != lastCheck.value) {
        await loadHint();
    }
    if (!hint.value.includes(searchKeyword.value)) {
        return;
    }
    loadingContent.value = true;
    queryKeyword.value = searchKeyword.value;
    axios
        .get("/available", {
            params: { s: queryKeyword.value },
        })
        .then((response) => {
            if (response.data.lst) {
                availableDicts.value = allDicts.value.filter((item) =>
                    response.data.lst.includes(item.order)
                );
                let availables = availableDicts.value.map((item) => item.order);
                if (!availables.includes(currentDict.value)) {
                    currentDict.value = Math.min(...availables);
                }
                fetchContent();
            }
        });
};

const fetchContent = () => {
    loadingContent.value = true;
    if (!queryKeyword.value) {
        return;
    }
    let params = {
        d: currentDict.value,
        s: queryKeyword.value,
    };
    if (backKeyword.value.length) {
        params.back = backKeyword.value[backKeyword.value.length - 1];
    }
    router.push({ path: route.path, query: params });
    axios
        .get("/query", {
            params: params,
        })
        .then((response) => {
            if (response.data.result) {
                let result = response.data.result;
                content.value = result.map((x) =>
                    x.replaceAll("$MYDICT_API", import.meta.env.VITE_API_URL)
                );
                loadingContent.value = false;
                switchDarknessOnLoad(darkMode.value);
            }
        });
};

const switchDarkness = (val) => {
    if (val) {
        iframeRef.value.forEach((e, i) => {
            e.contentWindow.DarkReader.setFetchMethod(window.fetch);
            e.contentWindow.DarkReader.enable({
                brightness: 100,
                contrast: 90,
                sepia: 10,
            });
        });
    } else {
        iframeRef.value.forEach((e, i) => {
            e.contentWindow.DarkReader.disable();
        });
    }
};

const switchDarknessOnLoad = () => {
    if (darkMode.value) {
        iframeRef.value.forEach((e, i) => {
            e.contentWindow.DarkReader.setFetchMethod(window.fetch);
            e.contentWindow.DarkReader.enable({
                brightness: 100,
                contrast: 90,
                sepia: 10,
            });
        });
    }
};

onMounted(() => {
    if (networkAvailable.value) {
        availableDicts.value = allDicts.value;
    }
    if (route.query) {
        searchKeyword.value = queryKeyword.value = route.query.s;
        currentDict.value = route.query.d;
        backKeyword.value = [route.query.back];
        goQuery();
    }
    inputRef.value.focus();
});

onBeforeRouteUpdate((to, from) => {
    document.title = to.query.s ? to.query.s + " - MyDICT" : "MyDICT";
});

window.onresize = () => {
    collapsed.value = window.innerWidth <= 768;
};

window.addEventListener("message", (ev) => {
    if (ev.data.go) {
        if (!ev.data.back && ev.data.go != searchKeyword.value) {
            backKeyword.value.push(queryKeyword.value);
        }
        if (ev.data.back) {
            backKeyword.value.pop();
        }
        queryKeyword.value = ev.data.go;
        fetchContent();
    }
});

watch(searchKeyword, loadHint);

watch(allDicts, () => {
    if (networkAvailable.value) {
        availableDicts.value = allDicts.value;
    }
});

watch(currentDict, () => {
    backKeyword.value = [];
    if (!searchKeyword.value) return;
    queryKeyword.value = searchKeyword.value;
    fetchContent();
});

const menuOptions = computed(() => {
    if (!availableDicts.value) return;
    return availableDicts.value.map((item) => ({
        label: () => <n-ellipsis>{item.name}</n-ellipsis>,
        key: item.order,
        icon: () => (
            <n-avatar
                size="small"
                object-fit="scale-down"
                color="#ffffff00"
                src={item.thumbail}
            ></n-avatar>
        ),
    }));
});

watch(darkMode, switchDarkness);
</script>

<template>
    <n-layout vertical>
        <n-layout-header>
            <div class="hidden md:block pt-4 pb-2 px-8 h-16">
                <div class="flex items-baseline gap-x-4">
                    <n-el tag="span" class="text-3xl font-bold gradient-title">
                        MyDICT
                    </n-el>
                    <n-el tag="span" class="hidden sm:inline">
                        {{ t("app-description") }}
                    </n-el>
                </div>
            </div>
            <div class="flex justify-center pb-0 pt-4 md:pb-3 md:pt-1 h-16">
                <div class="flex gap-x-2 md:gap-x-4 lg:gap-x-6 items-center">
                    <n-el class="text-xl font-bold md:hidden gradient-title">
                        MyDICT
                    </n-el>
                    <div class="text-lg hidden md:block whitespace-nowrap">
                        {{ t("query") }}
                    </div>
                    <n-auto-complete
                        v-model:value="searchKeyword"
                        :options="hint"
                        :clearable="true"
                        :input-props="{ autocomplete: 'disabled' }"
                        :loading="loadingHint"
                    >
                        <template
                            #default="{
                                handleInput,
                                handleBlur,
                                handleFocus,
                                value: slotValue,
                            }"
                        >
                            <n-input
                                :value="slotValue"
                                ref="inputRef"
                                :placeholder="t('press-enter-to-go')"
                                size="large"
                                autosize
                                class="w-48 md:w-60 lg:w-80"
                                @keyup.enter="goQuery"
                                @input="handleInput"
                                @focus="handleFocus"
                                @blur="handleBlur"
                            />
                        </template>
                        <template #prefix>
                            <n-icon class="mr-1" :component="Search" />
                        </template>
                    </n-auto-complete>
                    <n-button @click="goQuery">{{ t("go") }}</n-button>
                </div>
            </div>
            <n-divider class="divider-line" />
        </n-layout-header>
        <n-layout-content>
            <n-layout has-sider class="main-container">
                <n-layout-sider
                    bordered
                    collapse-mode="width"
                    :collapsed-width="64"
                    :width="240"
                    :collapsed="collapsed"
                    show-trigger
                    @collapse="collapsed = true"
                    @expand="collapsed = false"
                >
                    <n-scrollbar>
                        <n-menu
                            :collapsed-width="64"
                            :collapsed="collapsed"
                            :collapsed-icon-size="22"
                            v-model:value="currentDict"
                            :options="menuOptions"
                        />
                    </n-scrollbar>
                </n-layout-sider>
                <n-layout>
                    <div class="h-full">
                        <div
                            class="h-full"
                            v-if="!loadingContent && content.length"
                        >
                            <iframe
                                width="100%"
                                height="100%"
                                ref="iframeRef"
                                @load="switchDarknessOnLoad"
                                :srcdoc="t"
                                v-for="t in content"
                            ></iframe>
                        </div>
                        <div class="main-content" v-else-if="loadingContent">
                            <n-skeleton
                                height="2.5rem"
                                width="20vw"
                                class="mb-6"
                            />
                            <n-skeleton class="mt-2" text :repeat="4" />
                        </div>
                        <div class="main-content" v-else>
                            <n-el class="text-center text-3xl p-10">
                                {{ t("waiting-for-search") }}
                            </n-el>
                        </div>
                    </div>
                </n-layout>
            </n-layout>
        </n-layout-content>
    </n-layout>
</template>

<style>
.main-container {
    height: calc(100vh - 5rem - 1px);
}

@media (min-width: 768px) {
    .main-container {
        height: calc(100vh - 9rem - 1px);
    }
}

.divider-line {
    margin-top: 1rem !important;
    margin-bottom: 0 !important;
}
</style>
