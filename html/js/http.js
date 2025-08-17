export const BASE_URL = "http://127.0.0.1:8000/";

export const request = (path, ...args) => {
    if (typeof path === "string") {
        // 去掉路径开头的 /
        path = path.replace(/^\/+/, "");
        path = BASE_URL + path;
    }

    return fetch(path, ...args);
};
