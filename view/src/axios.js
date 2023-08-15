import axios from "axios";
import { message } from "./discrete";

export default {
    install: (app, options) => {
        const instance = axios.create({
            baseURL: "/api",
            timeout: 30000,
        });

        instance.interceptors.request.use(
            (config) => {
                if (config.url === "/dicts") return config;

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
            (response) => response,
            (error) => {
                if (error.response.data.detail) {
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
