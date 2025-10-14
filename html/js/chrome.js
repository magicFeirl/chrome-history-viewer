import { request, BASE_URL } from './http.js'
import { ROW_STATE } from './row.js'

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

export const openChromeOneByOne = async (data, openLink, openCount) => {
    const autoOpen = async () => {
        let count = 0;
        const openRows = data.filter((item) =>
            [ROW_STATE.available, ROW_STATE.unknown].includes(
                item.lastLink.state_type
            )
        );
        console.log(openRows)
        for (const { browser } of openRows) {
            count++;
            await openChrome(browser, { url: openLink });

            if (count >= openCount) {
                break;
            }
        }
    };

    const selectOpen = async (rows) => {
        for (const { browser } of rows) {
            await openChrome(browser, { url: openLink });
        }
    };

    const selectRows = data.filter((item) => item.checked);
    // 有勾选打开则使用勾选的 Profile
    if (selectRows.length) {
        selectOpen(selectRows);
    } else {
        autoOpen();
    }
};