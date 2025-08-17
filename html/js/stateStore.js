import { ref, watch } from './vue.esm-browser.js'


const DEFAULT_VALUE = () => ({
    showUnavailable: false,
    showAvailable: true,
    showBan: false,
    showUnknown: true,
    accountRowCount: 1,
    openCount: 1,
    openLink: "",
    querys: Array.from({ length: 3 }).map((a) => ""),
    disabledAccounts: []
})

export const STORE_KEY = 'STATE'

export default function useStateStore() {
    const data = localStorage.getItem(STORE_KEY)
    const state = ref()

    try {
        state.value = data ? JSON.parse(data) : DEFAULT_VALUE()
    } catch (e) {
        state.value = DEFAULT_VALUE()
        localStorage.removeItem(STORE_KEY)
        console.error('Load store failed:', e)
    }

    const watcher = watch(() => state.value, () => {
        localStorage.setItem(STORE_KEY, JSON.stringify(state.value))
    }, { deep: true })

    return { state, watcher }
}