# fetchtest.py
# 由原 JS 工程自动转换，集成所有 fetch 相关功能
# 依赖 requests, hashlib, base64, datetime, pycryptodome（如需 AES/RSA）

import requests
import hashlib
import base64
import datetime
import os

# ========== 工具函数 ==========
def get_date_string(date):
    return date.strftime('%Y%m%d')

def get_time_string(date):
    return date.strftime('%H%M%S')

def get_datetime_string(date):
    return date.strftime('%Y%m%d%H%M%S')

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def append_file(path, content):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)

def delay(ms):
    import time
    time.sleep(ms / 1000)

# ========== 数据获取 ==========
def cate_list():
    url = "https://program-sc.miguvideo.com/live/v2/tv-data/a5f78af9d160418eb679a6dd0429c920"
    resp = requests.get(url)
    live_list = resp.json()['body']['liveList']
    live_list = [item for item in live_list if item['name'] != '热门']
    live_list.sort(key=lambda x: 0 if x['name'] == '央视' else 1)
    return live_list

def data_list():
    cates = cate_list()
    for cate in cates:
        url = f"https://program-sc.miguvideo.com/live/v2/tv-data/{cate['vomsID']}"
        resp = requests.get(url)
        cate['dataList'] = resp.json()['body']['dataList']
    # TODO: uniqueData 逻辑
    return cates

# ========== 加密相关 ==========
def get_string_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest().lower()

# ========== Android URL 720p ==========
def get_android_url_720p(pid):
    timestramp = int(datetime.datetime.now().timestamp() * 1000)
    app_version = "26000009"
    headers = {
        'AppVersion': 2600000900,
        'TerminalId': 'android',
        'X-UP-CLIENT-CHANNEL-ID': '2600000900-99000-201600010010027'
    }
    s = f"{timestramp}{pid}{app_version}"
    md5 = get_string_md5(s)
    salt = 66666601
    suffix = "770fafdf5ba04d279a59ef1600baae98migu6666"
    sign = get_string_md5(md5 + suffix)
    rate_type = 3
    if pid == "608831231":
        rate_type = 2
    base_url = "https://play.miguvideo.com/playurl/v1/play/playurl"
    params = f"?sign={sign}&rateType={rate_type}&contId={pid}&timestamp={timestramp}&salt={salt}"
    resp = requests.get(base_url + params, headers=headers).json()
    url = resp.get('body', {}).get('urlInfo', {}).get('url', '')
    if not url:
        return {'url': '', 'rateType': 0}
    # TODO: getddCalcuURL720p 逻辑
    res_url = url  # 占位
    return {'url': res_url, 'rateType': 3}

# ========== 回放数据写入 ==========
def update_playback_data(program, file_path):
    # TODO: getPlaybackData 逻辑
    # 这里只写入频道信息和节目单结构
    append_file(file_path, f'    <channel id="{program["name"]}">\n        <display-name lang="zh">{program["name"]}</display-name>\n    </channel>\n')
    # TODO: 写入节目单
    return True

# ========== 主流程 ==========
def fetch_url_by_android():
    start = datetime.datetime.now()
    path = os.path.join(os.getcwd(), 'interface.txt')
    write_file(path, "")
    datas = data_list()
    playback_file = os.path.join(os.getcwd(), 'playback.xml')
    write_file(playback_file, '<?xml version="1.0" encoding="UTF-8"?>\n' + '<tv generator-info-name="Tak" generator-info-url="https://github.com/develop202/migu_video/">\n')
    append_file(path, '#EXTM3U x-tvg-url="https://develop202.github.io/migu_video/playback.xml,https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/playback.xml,https://gh-proxy.com/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/playback.xml" catchup="append" catchup-source="&playbackbegin=${(b)yyyyMMddHHmmss}&playbackend=${(e)yyyyMMddHHmmss}"\n')
    for cate in datas:
        print(f"分类###{cate['name']}")
        for data in cate['dataList']:
            res = update_playback_data(data, playback_file)
            if not res:
                print("playback.xml更新失败")
            res_obj = get_android_url_720p(data['pID'])
            if res_obj['url'] == "":
                print(f"{data['name']}：节目调整，暂不提供服务")
                continue
            print(f"正在写入节目:{data['name']}")
            append_file(path, f'#EXTINF:-1 svg-id="{data["name"]}" svg-name="{data["name"]}" tvg-logo="{data["pics"]["highResolutionH"]}" group-title="{cate["name"]}",{data["name"]}\n{res_obj["url"]}\n')
    append_file(playback_file, '</tv>\n')
    end = datetime.datetime.now()
    print(f"本次耗时:{(end-start).total_seconds()}秒")

if __name__ == "__main__":
    fetch_url_by_android()
