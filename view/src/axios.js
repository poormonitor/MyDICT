import axios from "axios";
import { configProviderProps } from "naive-ui";
import { ref } from "vue";
import { message } from "./discrete";

export default {
    install: (app, options) => {
        const networkAvailable = ref(true);
        app.provide("networkAvailable", networkAvailable);

        const instance = axios.create({
            baseURL: import.meta.env.VITE_API_URL,
            timeout: 5000,
        });

        instance.interceptors.request.use(
            (config) => {
                if (!networkAvailable.value && config.url != "/dicts") {
                    return Promise.reject("Network not available.");
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        instance.interceptors.response.use(
            (response) => {
                return response;
            },
            (error) => {
                if (!error.response) {
                    networkAvailable.value = false;
                } else if (error.response.data.detail) {
                    message.error(error.response.data.detail);
                } else {
                    message.error(error.message);
                }
                return Promise.reject(error);
            }
        );
        app.config.globalProperties.$axios = instance;
    },
};
