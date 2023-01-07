import axios from "axios";
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
                if (config.url === "/dicts") return config;

                if (!networkAvailable.value) {
                    return Promise.reject("Network not available.");
                }

                let version = sessionStorage.getItem("mydict_version");
                if (config.method === "get" && version) {
                    config.params.v = version;
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

        app.provide("axios", instance);
    },
};
