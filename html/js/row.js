export const ROW_STATE = {
    ban: 200,
    unknown: 300,
    unavailable: 400,
    available: 500,
    recent: 600,
};

export const ROW_STATE_MAP = {
    200: {
        text: "封号",
        style: "ban",
    },
    300: {
        text: "未知",
        style: "unknown",
    },
    400: {
        text: "冷却中",
        style: "unavailable",
    },
    500: {
        text: "可用",
        style: "available",
    },
    600: {
        text: "近期使用",
        style: "recent",
    },
};
