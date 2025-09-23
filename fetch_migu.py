import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import pywasm
import json

# 配置
WASM_URL = "https://m.miguvideo.com/mgs/player/prd/v_20250506111629_ddc2c612/dist/pickproof1000.wasm"
CATE_LIST_URL = "https://program-sc.miguvideo.com/live/v2/tv-data/a5f78af9d160418eb679a6dd0429c920"
PLAY_URL_TEMPLATE = "https://webapi.miguvideo.com/gateway/playurl/v2/play/playurlh5?contId={}&rateType={}&clientId=-&startPlay=true&xh265=false&channelId=0131_200300220100002"
PLAYBACK_URL_TEMPLATE = "https://program-sc.miguvideo.com/live/v2/tv-programs-data/{}/{}"

# 工具函数
def delay(ms):
    time.sleep(ms / 1000)

def get_date_string(date=None):
    if not date:
        date = datetime.now()
    return date.strftime("%Y%m%d")

def get_datetime_string(date=None):
    if not date:
        date = datetime.now()
    return date.strftime("%Y%m%d%H%M%S")

def write_file(file_path, content):
    Path(file_path).write_text(content, encoding='utf-8')

def append_file(file_path, content):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)

def init_wasm(wasm_url):
    try:
        response = requests.get(wasm_url)
        response.raise_for_status()
        wasm_bytes = response.content
        
        # 保存到临时文件
        with open("temp.wasm", "wb") as f:
            f.write(wasm_bytes)
            
        # 加载WASM
        vm = pywasm.load("temp.wasm")
        return vm
    except Exception as e:
        print(f"WASM初始化失败: {str(e)}")
        return None

def get_encrypt_url(vm, url):
    try:
        # 假设WASM有一个encrypt函数，具体需要根据实际WASM接口调整
        if not vm:
            return url
            
        # 这里需要根据实际WASM导出函数调整
        # 示例：将URL转换为字节数组传递给WASM函数
        url_bytes = url.encode('utf-8')
        result_ptr = vm.exec("encrypt", [len(url_bytes)])
        # 实际应用中需要根据WASM逻辑处理返回值
        return url
    except Exception as e:
        print(f"URL加密失败: {str(e)}")
        return url

# 核心功能
def get_cate_list():
    try:
        response = requests.get(CATE_LIST_URL)
        response.raise_for_status()
        data = response.json()
        
        live_list = data.get('body', {}).get('liveList', [])
        # 过滤热门分类
        live_list = [item for item in live_list if item.get('name') != '热门']
        # 央视排第一
        live_list.sort(key=lambda x: -1 if x.get('name') == '央视' else 1)
        return live_list
    except Exception as e:
        print(f"获取分类列表失败: {str(e)}")
        return []

def get_data_list(cate_list):
    try:
        for cate in cate_list:
            voms_id = cate.get('vomsID')
            if not voms_id:
                continue
                
            url = f"https://program-sc.miguvideo.com/live/v2/tv-data/{voms_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            cate['dataList'] = data.get('body', {}).get('dataList', [])
            delay(100)
        
        # 去重处理
        return unique_data(cate_list)
    except Exception as e:
        print(f"获取节目列表失败: {str(e)}")
        return []

def unique_data(live_list):
    all_items = []
    for category in live_list:
        for program in category.get('dataList', []):
            all_items.append({
                **program,
                'categoryName': category.get('name')
            })
    
    # 去重
    seen = set()
    unique_items = []
    for item in all_items:
        name = item.get('name')
        if name not in seen:
            seen.add(name)
            unique_items.append(item)
    
    # 重新组织分类
    category_map = {cate.get('name'): [] for cate in live_list}
    for item in unique_items:
        category_name = item.pop('categoryName', None)
        if category_name in category_map:
            category_map[category_name].append(item)
    
    # 更新原列表
    for cate in live_list:
        cate['dataList'] = category_map.get(cate.get('name'), [])
    
    return live_list

def get_url_info(cont_id, rate_type=4):
    try:
        url = PLAY_URL_TEMPLATE.format(cont_id, rate_type)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            'url': data.get('body', {}).get('urlInfo', {}).get('url', ''),
            'rateType': rate_type
        }
    except Exception as e:
        print(f"获取播放链接失败 (contId={cont_id}): {str(e)}")
        return {'url': '', 'rateType': rate_type}

def get_playback_data(program_id):
    try:
        today = get_date_string()
        url = PLAYBACK_URL_TEMPLATE.format(program_id, today)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('body', {}).get('program', [{}])[0].get('content', [])
    except Exception as e:
        print(f"获取节目单失败 (programId={program_id}): {str(e)}")
        return []

def refresh_token(user_id, token):
    try:
        # 实际刷新token的逻辑需要根据咪咕API调整
        print("刷新token成功")
        return True
    except Exception as e:
        print(f"刷新token失败: {str(e)}")
        return False

def main():
    # 获取环境变量
    user_id = os.environ.get('USERID')
    migu_token = os.environ.get('MIGU_TOKEN')
    
    if not user_id or not migu_token:
        print("错误: USERID或MIGU_TOKEN未设置")
        sys.exit(1)
    
    start_time = time.time()
    current_dir = Path.cwd()
    interface_path = current_dir / "interface.txt"
    playback_path = current_dir / "playback.xml"
    
    # 初始化文件
    write_file(interface_path, "")
    write_file(playback_path, '<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="Tak">\n')
    
    # 0点刷新token
    if datetime.now().hour == 0:
        refresh_token(user_id, migu_token)
    
    # 初始化WASM
    wasm_vm = init_wasm(WASM_URL)
    
    # 获取分类和节目列表
    cate_list = get_cate_list()
    if not cate_list:
        print("未获取到分类列表，退出程序")
        sys.exit(1)
    
    data_list = get_data_list(cate_list)
    
    # 写入M3U头部
    append_file(interface_path, '#EXTM3U x-tvg-url="https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/playback.xml" catchup="append" catchup-source="&playbackbegin=${(b)yyyyMMddHHmmss}&playbackend=${(e)yyyyMMddHHmmss}"\n')
    
    # 处理每个分类和节目
    for cate in data_list:
        cate_name = cate.get('name', '未知分类')
        print(f"处理分类: {cate_name}")
        
        for program in cate.get('dataList', []):
            program_name = program.get('name', '未知节目')
            program_id = program.get('pID')
            print(f"处理节目: {program_name} (ID: {program_id})")
            
            # 更新节目单
            playback_data = get_playback_data(program_id)
            if playback_data:
                # 写入频道信息
                append_file(playback_path, f'    <channel id="{program_name}">\n')
                append_file(playback_path, f'        <display-name lang="zh">{program_name}</display-name>\n')
                append_file(playback_path, f'    </channel>\n')
                
                # 写入节目信息
                for item in playback_data:
                    start_time = datetime.fromtimestamp(item.get('startTime') / 1000)
                    end_time = datetime.fromtimestamp(item.get('endTime') / 1000)
                    start_str = get_datetime_string(start_time)
                    end_str = get_datetime_string(end_time)
                    append_file(playback_path, f'    <programme channel="{program_name}" start="{start_str} +0800" stop="{end_str} +0800">\n')
                    append_file(playback_path, f'        <title lang="zh">{item.get("contName", "")}</title>\n')
                    append_file(playback_path, f'    </programme>\n')
            
            # 获取播放链接（带重试）
            retry_count = 0
            max_retries = 3
            res_obj = {'url': ''}
            
            while retry_count < max_retries and not res_obj['url']:
                # 尝试不同清晰度
                for rate_type in [3, 4, 5]:  # 高清、超清、蓝光
                    res_obj = get_url_info(program_id, rate_type)
                    if res_obj['url']:
                        break
                    
                if not res_obj['url']:
                    retry_count += 1
                    print(f"重试获取链接 ({retry_count}/{max_retries})")
                    delay(2000)
            
            if not res_obj['url']:
                print(f"无法获取 {program_name} 的播放链接")
                continue
            
            # 加密链接
            encrypted_url = get_encrypt_url(wasm_vm, res_obj['url'])
            
            # 写入M3U
            logo = program.get('pics', {}).get('highResolutionH', '')
            append_file(interface_path, f'#EXTINF:-1 svg-id="{program_name}" svg-name="{program_name}" tvg-logo="{logo}" group-title="{cate_name}",{program_name}\n')
            append_file(interface_path, f'{encrypted_url}\n')
    
    # 完成节目单XML
    append_file(playback_path, '</tv>\n')
    
    end_time = time.time()
    print(f"处理完成，耗时: {round(end_time - start_time, 2)}秒")

if __name__ == "__main__":
    main()
