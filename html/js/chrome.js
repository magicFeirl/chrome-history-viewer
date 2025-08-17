import { request, BASE_URL } from './http.js'

export const openChrome = async (browser, link) => {
    // if (link.state_type === ROW_STATE.unknown) {
    //   return
    // }
    const { profile_dir } = browser;
    const url = link?.url || "chrome://history/";
    const resp = await request(
        `/open/${browser.profile_dir}?url=${url}`
    );
    const result = await resp.json();
};

export const openChromeOneByOne = async () => {
    const autoOpen = async () => {
        let openCount = 0;
        const openRows = data.value.filter((item) =>
            [ROW_STATE.available, ROW_STATE.unknown].includes(
                item.lastLink.state_type
            )
        );

        for (const { browser } of openRows) {
            openCount++;
            await openChrome(browser, { url: state.value.openLink });

            if (openCount >= state.value.openCount) {
                break;
            }
        }
    };

    const selectOpen = async (rows) => {
        for (const { browser } of rows) {
            await openChrome(browser, { url: state.value.openLink });
        }
    };

    const selectRows = data.value.filter((item) => item.checked);
    // 有勾选打开则使用勾选的 Profile
    if (selectRows.length) {
        selectOpen(selectRows);
    } else {
        autoOpen();
    }
};