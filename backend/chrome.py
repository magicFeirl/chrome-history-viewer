import subprocess
import os
from glob import glob
import json
import sqlite3

from datetime import datetime, timedelta
import config


def chrome_time_to_datetime(chrome_time):
    # Chrome time is in microseconds since January 1, 1601
    epoch_start = datetime(1601, 1, 1)
    delta = timedelta(microseconds=chrome_time)
    return epoch_start + delta


def find_link_last_visit_time(link_part: str):
    chrome_data_dir = config.CHROME_DATA_DIR
    profiles = glob(os.path.join(chrome_data_dir, 'Profile *'))

    results = []
    for dir in profiles:
        dirname = os.path.basename(dir)
        config_file = os.path.join(dir, 'Preferences')
        
        if not os.path.exists(config_file):
            continue
            
        result = {}
        results.append(result)

        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            account_info = data.get('account_info')

            if not account_info:
                continue

            account_info = account_info[0]
            name, email, full_name = data['profile']['name'], account_info['email'], account_info['full_name']

            # print('quring:', dirname, name, full_name, email)

            result['browser'] = {
                'profile_dir': dirname,
                'username': name,
                'default_name': full_name,
                'email': email
            }

            history_db = sqlite3.connect(
                os.path.join(dir, 'History'), timeout=0.5)

            cursor = history_db.cursor()

            links = result['links'] = []

            try:
                sql = f'''
                    select * from urls
                    where url like "%{link_part}%"
                    order by last_visit_time desc
                    limit 100
                '''
                cursor.execute(sql)
                now = datetime.now()

                for row in cursor.fetchall():
                    last_visit_time = chrome_time_to_datetime(row[5])

                    links.append({
                        'id': row[0],
                        'url': row[1],
                        'title': row[2],
                        'visit_count': row[3],
                        # typed_count: row[4]
                        'last_visit_time': last_visit_time,
                        'last_visit_day_since_now': round((now - last_visit_time).total_seconds() / 60 / 60 / 24, 2)
                    })

            except sqlite3.OperationalError as e:
                print(e)

            finally:
                history_db.close()

    def sort_by_day(item):
        if 'links' in item and item['links']:
            return min(l['last_visit_day_since_now'] for l in item['links'])
        else:
            return 999

    results.sort(key=sort_by_day, reverse=True)
    return results


def open_chrome_with_profile(profile_name, url: str = ""):
    # Chrome 可执行文件的路径
    chrome_path = config.CHROME_EXE_PATH
    # 用户数据目录
    user_data_dir = config.CHROME_DATA_DIR
    username = os.environ['USERNAME']
    
    for path in [user_data_dir, rf'C:\Users\{username}\AppData\Local\Google']:
        # 启动 Chrome 并指定用户数据目录和配置文件夹
        result = subprocess.run([
            chrome_path,
            f"--user-data-dir={path}",
            f"--profile-directory={profile_name}",
            url
        ])
        
        print(result)
        
        if result.returncode == 0:
            break
        
