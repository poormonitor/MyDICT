import axios from "axios";
import { message } from "./discrete";

const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 10000,
});

instance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (!error.response) {
            message.error("Network error.");
        } else {
            message.error(error.response.data.detail);
        }
        return Promise.reject(error);
    }
);

export default instance;
