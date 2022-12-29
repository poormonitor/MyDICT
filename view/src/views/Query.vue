<script setup>
import { Search } from "@vicons/fa"
import { ref, watch, onMounted, computed, h } from "vue"
import axios from "../axios"
import { NAvatar, NEllipsis } from "naive-ui"
import { Buffer } from "buffer"

const searchKeyword = ref("")
const allDicts = ref([])
const availableDicts = ref([])
const content = ref("")
const hint = ref([])
const queryKey = reactive({ queryKeyword: "", currentDict: 0 })
const collapsed = ref(window.innerWidth <= 768)
const loadingContent = ref(false)
const loadingHint = ref(false)

const loadHint = () => {
    loadingHint.value = true
    axios.get("/hint", {
        params: { s: searchKeyword.value }
    }).then((response) => {
        if (response.data.lst) {
            loadingHint.value = false
            hint.value = response.data.lst
        }
    })
}

const goQuery = () => {
    loadHint()
    if (!hint.value.includes(searchKeyword.value)) {
        return
    }
    loadingContent.value = true
    queryKey.queryKeyword = searchKeyword.value
    axios.get("/available", {
        params: { s: queryKey.queryKeyword }
    }).then((response) => {
        if (response.data.lst) {
            availableDicts.value = allDicts.value.filter(item => response.data.lst.includes(item.order))
            if (!availableDicts.value.includes(queryKey.currentDict)) {
                queryKey.currentDict = Math.min.apply(Math, availableDicts.value.map(item => item.order))
            }
            fetchContent()
        }
    })
}

const fetchThumbail = async (d) => {
    return await axios.get("/thumbail", { params: { d: d }, responseType: 'arraybuffer' }).then((response) => {
        if (response.data) {
            let content_type = response.headers["content-type"]
            return `data:${content_type};base64,` + Buffer.from(response.data, "binary").toString("base64")
        }
    })
}

const fetchContent = () => {
    loadingContent.value = true
    axios.get("/query", {
        params: {
            d: queryKey.currentDict,
            s: queryKey.queryKeyword
        }
    }).then((response) => {
        if (response.data.result) {
            let result = response.data.result
            content.value = result.map(x => x.replaceAll("$MYDICT_API", import.meta.env.VITE_API_URL))
            loadingContent.value = false
        }
    })
}

const menuOptions = computed(() => {
    return availableDicts.value.map((item) => ({
        label: () => h(NEllipsis, null, { default: () => item.name }),
        key: item.order,
        icon: () => h(NAvatar, { size: "small", src: item.thumbail, objectFit: "scale-down", color: "#ffffff00" })
    }))
})

onMounted(() => {
    axios.get("/dicts").then(async (response) => {
        if (response.data.lst) {
            availableDicts.value = allDicts.value = response.data.lst
            for (let i = 0; i < allDicts.value.length; i++) {
                allDicts.value[i].thumbail = await fetchThumbail(i)
            }
        }
    })
})

window.onresize = () => {
    collapsed.value = window.innerWidth <= 768
}

watch(searchKeyword, loadHint)

watch(queryKey, () => {
    fetchContent()
})
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
            <n-auto-complete v-model:value="searchKeyword" :options="hint" @keyup.enter="goQuery" :clearable="true"
                class="w-64 lg:w-80" :input-props="{ autocomplete: 'disabled' }" size="large"
                placeholder="Press Enter to Go" :loading="loadingHint">
                <template #prefix>
                    <n-icon class="mr-1" :component="Search" />
                </template>
            </n-auto-complete>
            <n-button @click="goQuery">Go</n-button>
        </n-space>
    </div>
    <n-divider class="divider-line" />
    <n-layout has-sider class="main-container">
        <n-layout-sider bordered collapse-mode="width" :collapsed-width="64" :width="240" :collapsed="collapsed"
            show-trigger @collapse="collapsed = true" @expand="collapsed = false">
            <n-scrollbar>
                <n-menu :collapsed-width="64" :collapsed="collapsed" :collapsed-icon-size="22"
                    v-model:value="queryKey.currentDict" :options="menuOptions" />
            </n-scrollbar>
        </n-layout-sider>
        <n-layout>
            <div class="h-full">
                <div class="h-full" v-if="!loadingContent && content">
                    <iframe width="100%" height="100%" :srcdoc="t" v-for="t in content"></iframe>
                </div>
                <div class="main-content" v-else-if="loadingContent">
                    <n-skeleton height="2.5rem" width="20vw" class="mb-8" />
                    <n-skeleton class="mt-2" text :repeat="4" />
                </div>
                <div class="main-content" v-else>
                    <p class="text-center text-3xl text-zinc-500 p-10">Waiting for searching</p>
                </div>
            </div>
        </n-layout>
    </n-layout>
</template>

<style>
.main-container {
    height: calc(100vh - 4rem - 4rem - 1rem - 1px)
}

.divider-line {
    margin-top: 1rem !important;
    margin-bottom: 0 !important;
}
</style>