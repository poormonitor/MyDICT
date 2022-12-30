import { createRouter, createWebHashHistory } from "vue-router";

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: "/",
            name: "query",
            component: () => import("../views/Query.vue"),
            beforeEnter: (to, from) => {
                document.title = to.query.s
                    ? to.query.s + " - MyDICT"
                    : "MyDICT";
            },
        },
    ],
});

export default router;
