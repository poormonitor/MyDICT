import { useMessage } from "naive-ui";
import axios from "axios"

const message = useMessage()

const instance = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 1000
});

instance.interceptors.response.use((response) => {
    return response
}, (error) => {
    if (!error.response) {
        message.error("Network error.")
    } else {
        message.error(error.response.data.detail)
    }
    return Promise.reject(error);
})

export default instance