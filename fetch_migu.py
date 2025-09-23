import os
import sys
import time
import hashlib
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
from datetime import datetime, timedelta

# 常量定义
KEY_AES = "MQDUjI19MGe3BhaqTlpc9g=="
IV = "abcdefghijklmnop"
RSA_PRIVATE_KEY_PKCS8 = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAOhvWsrglBpQGpjB\r8okxLUCaaiKKOytn9EtvytB5tKDchmgkSaXpreWcDy/9imsuOiVCSdBr6hHjrTN7\rQKkA4/QYS8ptiFv1ap61PiAyRFDI1b8wp2haJ6HF1rDShG2XdfWIhLk4Hj6efVZA\rSfa3taM7C8NseWoWh05Cp26g4hXZAgMBAAECgYBzqZXghsisH1hc04ZBRrth/nT6\rIxc2jlA+ia6+9xEvSw2HHSeY7COgsnvMQbpzg1lj2QyqLkkYBdfWWmrerpa/mb7j\rm6w95YKs5Ndii8NhFWvC0eGK8Ygt02DeLohmkQu3B+Yq8JszjB7tQJRR2kdG6cPt\rKp99ZTyyPom/9uD+AQJBAPxCwajHAkCuH4+aKdZhH6n7oDAxZoMH/mihDRxHZJof\rnT+K662QCCIx0kVCl64s/wZ4YMYbP8/PWDvLMNNWC7ECQQDr4V23KRT9fAPAN8vB\rq2NqjLAmEx+tVnd4maJ16Xjy5Q4PSRiAXYLSr9uGtneSPP2fd/tja0IyawlP5UPL\rl76pAkAeXqMWAK+CvfPKxBKZXqQDQOnuI2RmDgZQ7mK3rtirvXae+ciZ4qc4Bqt7\r7yJ3s68YRlHQR+OMzzeeKz47kzZhAkAPteH1ChJw06q4Sb8TdiPX++jbkFiCxgiN\rCsaMTfGVU/Y8xGSSYCgPelEHxu1t2wwVa/tdYs505zYmkSGT1NaJAkBCS5hymXsA\rB92Fx8eGW5WpLfnpvxl8nOcP+eNXobi8Sc6q1FmoHi8snbcmBhidcDdcieKn+DbX\rGG3BQE/OCOkM\r"

# 频道信息
channelName = [
    {
        "cateName": "央视",
        "data": [
            {"name": "CCTV1综合", "pid": "608807420"},
            {"name": "CCTV2财经", "pid": "631780532"},
            {"name": "CCTV3综艺", "pid": "624878271"},
            {"name": "CCTV4中文国际", "pid": "631780421"},
            {"name": "CCTV5体育", "pid": "641886683"},
            {"name": "CCTV5+体育赛事", "pid": "641886773"},
            {"name": "CCTV6电影", "pid": "624878396"},
            {"name": "CCTV7国防军事", "pid": "673168121"},
            {"name": "CCTV8电视剧", "pid": "624878356"},
            {"name": "CCTV9纪录", "pid": "673168140"},
            {"name": "CCTV10科教", "pid": "624878405"},
            {"name": "CCTV11戏曲", "pid": "667987558"},
            {"name": "CCTV12社会与法", "pid": "673168185"},
            {"name": "CCTV13新闻", "pid": "608807423"},
            {"name": "CCTV14少儿", "pid": "624878440"},
            {"name": "CCTV15音乐", "pid": "673168223"},
            {"name": "CCTV17农业农村", "pid": "673168256"},
            {"name": "CCTV4欧洲", "pid": "608807419"},
            {"name": "CCTV4美洲", "pid": "608807416"},
            {"name": "CGTN外语记录", "pid": "609006487"},
            {"name": "CGTN阿拉伯语", "pid": "609154345"},
            {"name": "CGTN西班牙语", "pid": "609006450"},
            {"name": "CGTN法语", "pid": "609006476"},
            {"name": "CGTN俄语", "pid": "609006446"},
            {"name": "老故事", "pid": "884121956"},
            {"name": "发现之旅", "pid": "624878970"},
            {"name": "中学生", "pid": "708869532"},
            {"name": "CGTN", "pid": "609017205"},
        ]
    },
    # 其他分类频道...
    {
        "cateName": "卫视",
        "data": [
            {"name": "东方卫视", "pid": "651632648"},
            {"name": "江苏卫视", "pid": "623899368"},
            {"name": "广东卫视", "pid": "608831231"},
            {"name": "江西卫视", "pid": "783847495"},
            {"name": "河南卫视", "pid": "790187291"},
            {"name": "陕西卫视", "pid": "738910838"},
            {"name": "大湾区卫视", "pid": "608917627"},
            {"name": "湖北卫视", "pid": "947472496"},
            {"name": "吉林卫视", "pid": "947472500"},
            {"name": "青海卫视", "pid": "947472506"},
            {"name": "东南卫视", "pid": "849116810"},
            {"name": "海南卫视", "pid": "947472502"},
            {"name": "海峡卫视", "pid": "849119120"},
        ]
    }
    # 更多分类请参考原始JavaScript代码中的channelName
]

# 加密字符串替换规则
changedDdCalcu = {
    # 央视频道
    "631780532": {
        "all": {"index": [5, 8, 11, 14], "data": ["x", "a", "z", "a"]}
    },
    "624878271": {
        "all": {"index": [5, 8, 11, 14], "data": ["x", "a", "a", "a"]}
    },
    # 其他频道的规则...
}

# 工具函数
def delay(ms):
    time.sleep(ms / 1000)

def get_string_md5(s):
    md5_hash = hashlib.md5()
    md5_hash.update(s.encode('utf-8'))
    return md5_hash.hexdigest().lower()

def base64_encrypt(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')

def base64_decrypt(s):
    return base64.b64decode(s).decode('utf-8')

def get_date_string(date):
    return f"{date.year}{str(date.month).zfill(2)}{str(date.day).zfill(2)}"

def get_time_string(date):
    return f"{str(date.hour).zfill(2)}{str(date.minute).zfill(2)}{str(date.second).zfill(2)}"

def get_date_time_string(date):
    return get_date_string(date) + get_time_string(date)

def get_with_retry(url, headers=None, retries=3, timeout=10):
    """带重试的请求函数"""
    for i in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            return resp
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(2 ** i)  # 指数退避

# API调用函数
def cate_list():
    try:
        resp = get_with_retry("https://program-sc.miguvideo.com/live/v2/tv-data/a5f78af9d160418eb679a6dd0429c920")
        live_list = resp.json()["body"]["liveList"]
        # 过滤热门分类
        live_list = [item for item in live_list if item["name"] != "热门"]
        # 央视排第一
        live_list.sort(key=lambda x: -1 if x["name"] == "央视" else 1)
        return live_list
    except Exception as e:
        print(f"获取分类列表失败: {e}")
        raise

def data_list():
    try:
        cates = cate_list()
        for i, cate in enumerate(cates):
            print(f"获取分类 {cate['name']} 的数据...")
            resp = get_with_retry(f"https://program-sc.miguvideo.com/live/v2/tv-data/{cate['vomsID']}")
            cates[i]["dataList"] = resp.json()["body"]["dataList"]
        
        # 去重处理
        all_items = []
        for category in cates:
            for program in category["dataList"]:
                all_items.append({**program, "categoryName": category["name"]})
        
        seen = set()
        unique_items = []
        for item in all_items:
            if item["name"] not in seen:
                seen.add(item["name"])
                unique_items.append(item)
        
        # 重建分类映射
        category_map = {live["name"]: [] for live in cates}
        for item in unique_items:
            category_name = item.pop("categoryName")
            if category_name in category_map:
                category_map[category_name].append(item)
        
        # 更新分类数据
        for live in cates:
            live["dataList"] = category_map[live["name"]]
        
        return cates
    except Exception as e:
        print(f"获取频道数据失败: {e}")
        raise

def get_url_info(cont_id):
    try:
        url = f"https://webapi.miguvideo.com/gateway/playurl/v2/play/playurlh5?contId={cont_id}&rateType=999&clientId=-&startPlay=true&xh265=false&channelId=0131_200300220100002"
        resp = get_with_retry(url)
        data = resp.json()
        if "body" in data and "urlInfo" in data["body"] and "url" in data["body"]["urlInfo"]:
            return data["body"]["urlInfo"]["url"]
        return ""
    except Exception as e:
        print(f"获取播放链接失败: {e}")
        return ""

def get_android_url_720p(pid):
    """获取Android 720p播放链接，增强错误处理"""
    try:
        # 检查pid有效性
        if pid is None:
            print("错误: PID为None")
            return {"url": "", "rateType": 0}
        
        if not isinstance(pid, str) and not isinstance(pid, int):
            print(f"错误: PID类型无效 {type(pid)}")
            return {"url": "", "rateType": 0}
        
        pid_str = str(pid).strip()
        if not pid_str:
            print("错误: PID为空字符串")
            return {"url": "", "rateType": 0}
        
        print(f"正在处理PID: {pid_str}")
        
        timestamp = int(time.time() * 1000)
        app_version = "26000009"
        headers = {
            "AppVersion": "2600000900",
            "TerminalId": "android",
            "X-UP-CLIENT-CHANNEL-ID": "2600000900-99000-201600010010027"
        }
        
        str_to_hash = f"{timestamp}{pid_str}{app_version}"
        md5 = get_string_md5(str_to_hash)
        salt = 66666601
        suffix = "770fafdf5ba04d279a59ef1600baae98migu6666"
        sign = get_string_md5(md5 + suffix)
        
        # 广东卫视特殊处理
        rate_type = 2 if pid_str == "608831231" else 3
        
        base_url = "https://play.miguvideo.com/playurl/v1/play/playurl"
        params = f"?sign={sign}&rateType={rate_type}&contId={pid_str}&timestamp={timestamp}&salt={salt}"
        
        resp = get_with_retry(base_url + params, headers=headers)
        data = resp.json()
        
        if "body" in data and "urlInfo" in data["body"] and "url" in data["body"]["urlInfo"]:
            url = data["body"]["urlInfo"]["url"]
            print(f"成功获取链接: {url[:50]}...")
            return {"url": url, "rateType": rate_type}
        else:
            print(f"API响应中未找到有效URL: {data}")
            return {"url": "", "rateType": 0}
            
    except Exception as e:
        print(f"获取Android 720p链接失败: {e}")
        import traceback
        traceback.print_exc()
        return {"url": "", "rateType": 0}

# 回放数据处理
def get_playback_data(program_id):
    try:
        today = get_date_string(datetime.now())
        url = f"https://program-sc.miguvideo.com/live/v2/tv-programs-data/{program_id}/{today}"
        resp = get_with_retry(url)
        data = resp.json()
        return data.get("body", {}).get("program", [{}])[0].get("content", None)
    except Exception as e:
        print(f"获取回放数据失败: {e}")
        return None

def update_playback_data(program, file_path):
    try:
        # 这里简化了处理，实际应实现完整的updatePlaybackDataByMigu和updatePlaybackDataByCntv逻辑
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"    <channel id=\"{program['name']}\">\n")
            f.write(f"        <display-name lang=\"zh\">{program['name']}</display-name>\n")
            f.write(f"    </channel>\n")
        return True
    except Exception as e:
        print(f"更新回放数据失败: {e}")
        return False

def debug_data_source():
    """调试函数，检查数据源问题"""
    try:
        datas = data_list()
        for i, cate in enumerate(datas):
            print(f"分类: {cate['name']}")
            if 'dataList' in cate:
                for j, program in enumerate(cate['dataList']):
                    pid = program.get('pID')
                    print(f"  节目 {j}: {program.get('name', '未知')} - PID: {pid} (类型: {type(pid)})")
                    if pid is None:
                        print(f"     警告: {program.get('name')} 的PID为None!")
    except Exception as e:
        print(f"调试数据源时出错: {e}")

# 主函数
def fetch_url_by_android():
    start = time.time()
    path = os.path.join(os.getcwd(), "interface.txt")
    
    # 清空文件
    with open(path, "w", encoding="utf-8") as f:
        f.write("")
    
    # 获取数据
    try:
        datas = data_list()
    except Exception as e:
        print(f"获取数据失败: {e}")
        return
    
    # 初始化回放文件
    playback_file = os.path.join(os.getcwd(), "playback.xml")
    with open(playback_file, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<tv generator-info-name="Tak" generator-info-url="https://github.com/develop202/migu_video/">\n')
    
    # 写入M3U开头
    with open(path, "a", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://develop202.github.io/migu_video/playback.xml,https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/playback.xml,https://gh-proxy.com/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/playback.xml" catchup="append" catchup-source="&playbackbegin=${(b)yyyyMMddHHmmss}&playbackend=${(e)yyyyMMddHHmmss}"\n')
    
    # 处理每个分类
    success_count = 0
    fail_count = 0
    
    for i, cate in enumerate(datas):
        print(f"处理分类: {cate['name']}")
        data = cate.get("dataList", [])
        
        for program in data:
            # 检查program数据完整性
            if not program or 'pID' not in program or program['pID'] is None:
                print(f"跳过无效节目数据: {program.get('name', '未知')}")
                fail_count += 1
                continue
            
            # 检查节目名称
            if 'name' not in program or not program['name']:
                print(f"跳过无名节目，PID: {program['pID']}")
                fail_count += 1
                continue
            
            # 更新回放数据
            res = update_playback_data(program, playback_file)
            if not res:
                print("playback.xml更新失败")
            
            # 获取播放链接
            res_obj = get_android_url_720p(program["pID"])
            if res_obj["url"] == "":
                print(f"{program['name']}：节目调整，暂不提供服务")
                fail_count += 1
                continue
            
            print(f"成功写入节目: {program['name']}")
            
            # 写入节目信息
            with open(path, "a", encoding="utf-8") as f:
                line = f"#EXTINF:-1 svg-id=\"{program['name']}\" svg-name=\"{program['name']}\" tvg-logo=\"{program.get('pics', {}).get('highResolutionH', '')}\" group-title=\"{cate['name']}\",{program['name']}\n"
                f.write(line)
                f.write(f"{res_obj['url']}\n")
            success_count += 1
    
    # 完成回放文件
    with open(playback_file, "a", encoding="utf-8") as f:
        f.write("</tv>\n")
    
    end = time.time()
    print(f"处理完成: 成功 {success_count} 个, 失败 {fail_count} 个")
    print(f"本次耗时:{(end - start):.2f}秒")

if __name__ == "__main__":
    # 先调试数据源
    print("开始调试数据源...")
    debug_data_source()
    print("\n开始获取播放链接...")
    fetch_url_by_android()
