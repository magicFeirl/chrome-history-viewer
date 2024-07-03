import os
from glob import glob
import json
import sqlite3
import csv

from datetime import datetime, timedelta


def chrome_time_to_datetime(chrome_time):
    # Chrome time is in microseconds since January 1, 1601
    epoch_start = datetime(1601, 1, 1)
    delta = timedelta(microseconds=chrome_time)
    return epoch_start + delta


def find_link_last_visit_time(link_part: str):
    username = os.environ['USERNAME']
    chrome_data_dir = f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile *'
    profiles = glob(chrome_data_dir)

    results = []
    for dir in profiles:
        dirname = os.path.basename(dir)
        config_file = os.path.join(dir, 'Preferences')
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
        if item['links']:
            return min(l['last_visit_day_since_now'] for l in item['links'])
        else:
            return 999

    results.sort(key=sort_by_day, reverse=True)
    return results


if __name__ == '__main__':
    # sdxl colab
    colab_link = 'google.com'
    results = find_link_last_visit_time(colab_link)

    with open('data.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(['days', 'username', 'default_name', 'email'])

        for item in results:
            browser = item['browser']
            profile_dir, username, default_name, email = browser['profile_dir'], browser['username'], browser['default_name'], browser['email']
            # skip unavaible account
            if 'appeal' in username or 'cant restore' in username:
                continue

            colab_links = item['links']
            basic_row = [username, default_name, email]
            if not colab_links:
                basic_row.insert(0, 999)
            else:
                days = colab_links[0]['last_visit_day_since_now']
                if days < 2.5:
                    break
                basic_row.insert(0, days)

            writer.writerow(basic_row)
