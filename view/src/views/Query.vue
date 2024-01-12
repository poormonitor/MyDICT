<script setup lang="jsx">
import { Search } from "@vicons/fa";
import { ref, watch, onMounted, computed, inject } from "vue";
import { useRoute, useRouter, onBeforeRouteUpdate } from "vue-router";
import { useThemeVars } from "naive-ui";
import { useI18n } from "vue-i18n";

const { t } = useI18n({ useScope: "global" });

const axios = inject("axios");
const darkMode = inject("darkMode");

const route = useRoute();
const router = useRouter();
const themeVars = useThemeVars();
const hoverColor = computed(() => {
    let color = themeVars.value.primaryColor;
    return color.slice(0, color.length - 2) + "1a";
});

const allDicts = ref([]);
const availableDicts = ref([]);
const currentDict = ref();

const searchKeyword = ref("");
const queryKeyword = ref("");
const backKeyword = ref([]);

const inputRef = ref();
const iframeRef = ref([]);
const hint = ref([]);
const hints = computed(() => hint.value.map((item) => item[0]));
const showHint = ref([]);
const lastCheck = ref("");

const content = ref([]);

const collapsed = ref(window.innerWidth <= 768);

const loadingContent = ref(false);
const loadingHint = ref(false);

var hintTimeout;

const queryHint = async () => {
    if (!searchKeyword.value) return [];

    let currentKey = searchKeyword.value;

    return await axios
        .get("/hint", {
            params: { s: currentKey },
        })
        .then((response) => {
            if (currentKey === searchKeyword.value) {
                hint.value = response.data.lst;
                lastCheck.value = searchKeyword.value;
            }
        });
};

const goQuery = async () => {
    if (!hints.value.includes(searchKeyword.value)) {
        if (searchKeyword.value != lastCheck.value) {
            await queryHint();
        }
        if (!hints.value.includes(searchKeyword.value)) {
            return (showHint.value = hints.value);
        }
    }

    loadingContent.value = true;
    queryKeyword.value = searchKeyword.value;
    availableDicts.value = allDicts.value.filter((item) =>
        hint.value
            .find((e) => e[0] === queryKeyword.value)[1]
            .includes(item.order)
    );

    let availables = availableDicts.value.map((item) => item.order);
    if (!availables.includes(currentDict.value)) {
        currentDict.value = Math.min(...availables);
    }

    fetchContent();
};

const fetchContent = () => {
    if (!queryKeyword.value) return;

    loadingContent.value = true;

    let params = {
        d: currentDict.value,
        s: queryKeyword.value,
    };
    router.push({ path: route.path, query: params });

    if (backKeyword.value.length) params.back = backKeyword.value.slice(-1)[0];

    axios
        .get("/query", {
            params: params,
        })
        .then((response) => {
            if (response.data.result) {
                let result = response.data.result;
                content.value = result.map((x) =>
                    x.replaceAll("$MYDICT_API", "/api")
                );
                switchDarknessOnLoad(darkMode.value).then(() => {
                    loadingContent.value = false;
                });
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

const switchDarknessOnLoad = async () => {
    return new Promise((resolve, reject) => {
        if (darkMode.value) {
            iframeRef.value.forEach((e, i) => {
                e.contentWindow.DarkReader.setFetchMethod(window.fetch);
                e.contentWindow.DarkReader.enable({
                    brightness: 100,
                    contrast: 90,
                    sepia: 10,
                });
            });
            setTimeout(resolve, 300);
        } else {
            return resolve();
        }
    });
};

const fetchDicts = async () => {
    await axios.get("/dicts").then((response) => {
        if (response.data.lst) {
            sessionStorage.setItem("mydict_version", response.data.version);
            allDicts.value = response.data.lst;
            allDicts.value.map(async (item, index) => {
                item.thumbail = await fetchThumbail(index);
            });
        }
    });
};

const fetchThumbail = async (d) => {
    return await axios
        .get("/thumbail", { params: { d: d }, responseType: "arraybuffer" })
        .then((response) => {
            if (response.data) {
                const imageBuffer = response.data;
                const blob = new Blob([imageBuffer], {
                    type: response.headers["content-type"],
                });
                const imageUrl = URL.createObjectURL(blob);
                return imageUrl;
            }
        });
};

onMounted(async () => {
    await fetchDicts();
    availableDicts.value = allDicts.value;
    if (route.query.s) {
        searchKeyword.value = queryKeyword.value = route.query.s;
        currentDict.value = route.query.d;
        goQuery();
    } else {
        inputRef.value.focus();
    }
});

onBeforeRouteUpdate((to, from) => {
    document.title = to.query.s ? to.query.s + " - MyDICT" : "MyDICT";
});

window.addEventListener("resize", () => {
    collapsed.value = window.innerWidth <= 768;
});

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

watch(searchKeyword, () => {
    showHint.value = [];
    clearTimeout(hintTimeout);
    hintTimeout = setTimeout(async () => {
        if (lastCheck.value === searchKeyword.value) return;
        loadingHint.value = true;
        await queryHint();
        showHint.value = hints.value;
        loadingHint.value = false;
    }, 500);
});

watch(currentDict, () => {
    console.log(searchKeyword.value, queryKeyword.value, backKeyword.value);
    if (
        searchKeyword.value !== queryKeyword.value &&
        backKeyword.value.length
    ) {
        queryKeyword.value = backKeyword.value[0];
        backKeyword.value = [];
    }
    if (!searchKeyword.value) return;
    fetchContent();
});

const menuOptions = computed(() => {
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
                        :options="showHint"
                        :clearable="true"
                        :input-props="{ autocomplete: 'disabled' }"
                        :loading="loadingHint"
                        @select="goQuery"
                        blur-after-select
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
                                :input-props="{ spellcheck: 'false' }"
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
            <n-layout has-sider class="main-container hidden sm:block">
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
                            v-show="!loadingContent"
                            v-if="content.length"
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
                        <div class="main-content" v-if="loadingContent">
                            <n-skeleton
                                height="2.5rem"
                                width="20vw"
                                class="mb-6"
                            />
                            <n-skeleton class="mt-2" text :repeat="4" />
                        </div>
                        <div class="main-content" v-else-if="!content.length">
                            <n-el class="text-center text-3xl p-10">
                                {{ t("waiting-for-search") }}
                            </n-el>
                        </div>
                    </div>
                </n-layout>
            </n-layout>
            <n-layout class="main-container block sm:hidden">
                <n-layout-header bordered position="absolute" class="h-12">
                    <n-scrollbar x-scrollable class="overflow-y-hidden">
                        <n-breadcrumb class="m-1 mx-2" separator>
                            <n-breadcrumb-item
                                :clickable="true"
                                @click="() => (currentDict = item.key)"
                                :class="{
                                    'breadcrumb-now': item.key === currentDict,
                                    'last-dict':
                                        item.key ===
                                        menuOptions[menuOptions.length - 1].key,
                                }"
                                v-for="item in menuOptions"
                            >
                                <div class="flex items-center">
                                    <component class="" :is="item.icon()" />
                                </div>
                            </n-breadcrumb-item>
                            <n-breadcrumb-item class="w-0 last-dict" />
                        </n-breadcrumb>
                    </n-scrollbar>
                </n-layout-header>
                <n-layout position="absolute" class="!top-12">
                    <div class="h-full">
                        <div
                            class="h-full"
                            v-show="!loadingContent"
                            v-if="content.length"
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
                        <div class="main-content" v-if="loadingContent">
                            <n-skeleton
                                height="2.5rem"
                                width="20vw"
                                class="mb-6"
                            />
                            <n-skeleton class="mt-2" text :repeat="4" />
                        </div>
                        <div class="main-content" v-else-if="!content.length">
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
.last-dict > .n-breadcrumb-item__separator {
    margin: 0 !important;
}

.breadcrumb-now > .n-breadcrumb-item__link {
    background-color: v-bind("hoverColor") !important;
}

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
