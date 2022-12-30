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
        } else if (error.response.data.detail) {
            message.error(error.response.data.detail);
        } else {
            message.error(error.message);
        }
        return Promise.reject(error);
    }
);

export default instance;
