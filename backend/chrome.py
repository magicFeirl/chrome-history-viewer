import subprocess
import os
from glob import glob
import json
import sqlite3
from typing import List

from datetime import datetime, timedelta
import config


def chrome_time_to_datetime(chrome_time):
    # Chrome time is in microseconds since January 1, 1601
    epoch_start = datetime(1601, 1, 1)
    delta = timedelta(microseconds=chrome_time)
    return epoch_start + delta


cache = {}


def load_config_file(config_file):
    global cache

    if config_file not in cache:
        with open(config_file, "r", encoding="utf-8") as f:
            cache[config_file] = json.load(f)
    else:
        print(config_file, "命中缓存")

    return cache[config_file]


def create_link_description(id, url, title, visit_count=1, last_visit_time=None):
    now = datetime.now()
    last_visit_time = last_visit_time or now

    return {
        "id": id,
        "url": url,
        "title": title,
        "visit_count": visit_count,
        # typed_count: row[4]
        "last_visit_time": last_visit_time,
        "last_visit_day_since_now": round(
            (now - last_visit_time).total_seconds() / 60 / 60 / 24,
            2,
        ),
    }


def find_link_last_visit_time(link_parts: List[str]):
    chrome_data_dir = config.CHROME_DATA_DIR
    profiles = glob(os.path.join(chrome_data_dir, "Profile *"))

    results = []
    for dir in profiles:
        dirname = os.path.basename(dir)
        config_file = os.path.join(dir, "Preferences")

        if not os.path.exists(config_file):
            continue

        result = {}
        results.append(result)

        data = load_config_file(config_file)
        account_info = data.get("account_info")

        if not account_info:
            continue

        account_info = account_info[0]
        name, email, full_name = (
            data["profile"]["name"],
            account_info["email"],
            account_info["full_name"],
        )

        # print('quring:', dirname, name, full_name, email)

        result["browser"] = {
            "profile_dir": dirname,
            "username": name,
            "default_name": full_name,
            "email": email,
        }

        db_path = os.path.join(dir, "History")
        history_db = sqlite3.connect(db_path, timeout=0.5)

        cursor = history_db.cursor()

        links = result["links"] = []

        try:
            or_query = " or ".join([f'url like "%{s}%"' for s in link_parts])
            sql = f"""
                select * from urls
                where {or_query}
                order by last_visit_time desc
                limit 10
            """
            print(db_path)
            print("Execute:", sql)

            cursor.execute(sql)

            for row in cursor.fetchall():
                last_visit_time = chrome_time_to_datetime(row[5])
                id_url_title_vist_count = [row[i] for i in range(4)]
                links.append(
                    create_link_description(*id_url_title_vist_count, last_visit_time)
                )

        except sqlite3.OperationalError as e:
            last_visit_time = datetime.fromtimestamp(os.path.getmtime(db_path))
            links.append(create_link_description(-1, "", "占用中", 1, last_visit_time))
            print(e)
        finally:
            history_db.close()

    def sort_by_day(item):
        if "links" in item and item["links"]:
            return min(l["last_visit_day_since_now"] for l in item["links"])
        else:
            return 999

    results.sort(key=sort_by_day, reverse=True)
    return results


def open_chrome_with_profile(profile_name, url: str = ""):
    # Chrome 可执行文件的路径
    chrome_path = config.CHROME_EXE_PATH
    # 用户数据目录
    user_data_dir = config.CHROME_DATA_DIR
    username = os.environ["USERNAME"]

    for path in [user_data_dir, rf"C:\Users\{username}\AppData\Local\Google"]:
        # 启动 Chrome 并指定用户数据目录和配置文件夹
        result = subprocess.run(
            [
                chrome_path,
                f"--user-data-dir={path}",
                f"--profile-directory={profile_name}",
                url,
            ]
        )

        print(result)

        if result.returncode == 0:
            break
