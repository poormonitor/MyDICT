<script setup>
import { Search } from "@vicons/fa";
import { ref, watch, onMounted, computed, h } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "../axios";
import { NAvatar, NEllipsis } from "naive-ui";
import { Buffer } from "buffer";

const route = useRoute();
const router = useRouter();

const allDicts = ref([]);
const availableDicts = ref([]);

const searchKeyword = ref("");
const queryKeyword = ref("");
const backKeyword = ref([]);

const hint = ref([]);
const lastCheck = ref("");

const currentDict = ref(0);
const content = ref("");

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
                if (!availableDicts.value.includes(currentDict.value)) {
                    currentDict.value = Math.min.apply(
                        Math,
                        availableDicts.value.map((item) => item.order)
                    );
                }
                fetchContent();
            }
        });
};

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
            }
        });
};

const menuOptions = computed(() => {
    return availableDicts.value.map((item) => ({
        label: () => h(NEllipsis, null, { default: () => item.name }),
        key: item.order,
        icon: () =>
            h(NAvatar, {
                size: "small",
                src: item.thumbail,
                objectFit: "scale-down",
                color: "#ffffff00",
            }),
    }));
});

onMounted(() => {
    axios.get("/dicts").then((response) => {
        if (response.data.lst) {
            availableDicts.value = allDicts.value = response.data.lst;
            allDicts.value.map(async (item, index) => {
                item.thumbail = await fetchThumbail(index);
            });
        }
    });
    if (route.query) {
        searchKeyword.value = queryKeyword.value = route.query.s;
        currentDict.value = route.query.d;
        backKeyword.value = [route.query.back];
        goQuery();
    }
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
    }
});

watch(searchKeyword, loadHint);

watch(queryKeyword, fetchContent);
watch(currentDict, () => {
    backKeyword.value = [];
    queryKeyword.value = searchKeyword.value;
    fetchContent();
});
</script>

<template>
    <div class="pt-6 px-8 h-16">
        <n-space align="baseline">
            <n-gradient-text type="info" class="text-3xl font-bold">
                MyDICT
            </n-gradient-text>
            <span class="hidden sm:inline">A universal dictionary tool</span>
        </n-space>
    </div>
    <div class="flex justify-center mb-6 mt-2 sm:mb-4 sm:mt-4 h-12">
        <n-space class="items-center">
            <span class="text-lg hidden md:inline">Query</span>
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
                        size="large"
                        placeholder="Press Enter to Go"
                        class="w-64 lg:w-80"
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
            <n-button @click="goQuery">Go</n-button>
        </n-space>
    </div>
    <n-divider class="divider-line" />
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
                <div class="h-full" v-if="!loadingContent && content">
                    <iframe
                        width="100%"
                        height="100%"
                        :srcdoc="t"
                        v-for="t in content"
                    ></iframe>
                </div>
                <div class="main-content" v-else-if="loadingContent">
                    <n-skeleton height="2.5rem" width="20vw" class="mb-6" />
                    <n-skeleton class="mt-2" text :repeat="4" />
                </div>
                <div class="main-content" v-else>
                    <p class="text-center text-3xl text-zinc-500 p-10">
                        Waiting for searching
                    </p>
                </div>
            </div>
        </n-layout>
    </n-layout>
</template>

<style>
.main-container {
    height: calc(100vh - 4rem - 4rem - 1rem - 1px);
}

.divider-line {
    margin-top: 1rem !important;
    margin-bottom: 0 !important;
}
</style>
