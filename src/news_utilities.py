import json
from datetime import datetime, timedelta

cache_file = "/home/pi/AlarmClockProject/AlarmClock/cache/newslist.json"

days_keep = 4


def str_to_datetime(date_str):
    datetime_time = datetime(int(date_str[:4]),  # Year
                             int(date_str[5:7]),  # Month
                             int(date_str[8:10]))  # Day
    return(datetime_time)


def add_news(index, date, title, desc):
    news = get_news()
    if not isinstance(news, dict):
        news = {}
    news[str(index)] = {'title': title,
                        'date': date.strftime('%Y:%m:%d'),
                        'desc': desc}
    with open(cache_file, 'w') as jsonfile:
        json.dump(news, jsonfile, ensure_ascii=False, indent=4)


def rm_news(index):
    news = get_news()
    if not isinstance(news, dict):
        news = {}
    news.pop(str(index), None)
    with open(cache_file, 'w') as jsonfile:
        json.dump(news, jsonfile, ensure_ascii=False, indent=4)


def get_news():
    datetime_now = datetime.now()
    data = None
    data2 = None
    with open(cache_file, "r") as jsonFile:
        try:
            data = json.load(jsonFile)
        except json.decoder.JSONDecodeError:
            pass
    if data is None:
        return
    data2 = data.copy()
    for index in data.keys():
        if str_to_datetime(data[index]['date']) < datetime_now - timedelta(days=days_keep):
            data2.pop(index)
    if data != data2:
        with open(cache_file, 'w') as jsonfile:
            json.dump(data2, jsonfile)
    return data2


if __name__ == '__main__':
    print(get_news())
