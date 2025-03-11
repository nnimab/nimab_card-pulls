import pandas as pd
import os
import requests
import json
import time
import argparse
import sys
import re
import random

# 解析命令行參數
parser = argparse.ArgumentParser(description='生成易經卦象的MD檔案')
parser.add_argument('--api-key', help='OpenAI API金鑰')
parser.add_argument('--start', type=int, help='起始卦象編號（1-64）')
parser.add_argument('--end', type=int, help='結束卦象編號（1-64）')
parser.add_argument('--force', action='store_true', help='強制重新生成已存在的檔案')
parser.add_argument('--dry-run', action='store_true', help='僅顯示將要生成的檔案，不實際生成')
parser.add_argument('--max-retries', type=int, default=5, help='API請求最大重試次數')
parser.add_argument('--initial-delay', type=float, default=2.0, help='初始重試延遲時間（秒）')
parser.add_argument('--model', type=str, default='gpt-4o', help='OpenAI 模型名稱')
args = parser.parse_args()

# 設定API金鑰（優先使用命令行參數，其次使用環境變數，最後使用預設值）
OPENAI_API_KEY = args.api_key or os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY and not args.dry_run:
    print("錯誤：未提供OpenAI API金鑰。請使用 --api-key 參數或設置 OPENAI_API_KEY 環境變數。")
    sys.exit(1)

API_URL = "https://api.openai.com/v1/chat/completions"

# 確保目標目錄存在
output_dir = "card-descriptions/yijing"
os.makedirs(output_dir, exist_ok=True)

# 讀取JSON檔案
json_file = "易經卡基本資料.json"
if not os.path.exists(json_file):
    print(f"錯誤：找不到JSON檔案 '{json_file}'")
    sys.exit(1)

try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"成功讀取JSON檔案，共有 {len(data)} 筆卦象資料")
except Exception as e:
    print(f"讀取JSON檔案時出錯: {e}")
    sys.exit(1)

# 五行對應表
wuxing_colors = {
    "木": {"color": "綠色/青色", "numbers": [3, 8], "direction": "東", "details": "綠、青、翠"},
    "火": {"color": "紅色", "numbers": [2, 7], "direction": "南", "details": "紅、紫、橙"},
    "土": {"color": "黃色", "numbers": [5, 10], "direction": "中央", "details": "黃、棕、咖啡"},
    "金": {"color": "白色", "numbers": [4, 9], "direction": "西", "details": "白、金、銀"},
    "水": {"color": "黑色", "numbers": [1, 6], "direction": "北", "details": "黑、藍、灰"}
}

# 解析屬性字符串為五行元素
def parse_attribute(attribute):
    if len(attribute) == 2:
        return [attribute[0], attribute[1]]
    else:
        print(f"警告：無法解析屬性 '{attribute}'")
        return ["未知", "未知"]

# 獲取五行解析
def get_wuxing_analysis(attribute):
    elements = parse_attribute(attribute)
    
    if elements[0] == "未知" or elements[1] == "未知":
        return "無法分析五行屬性。"
    
    analysis = []
    
    # 第一個元素
    if elements[0] in wuxing_colors:
        e1 = elements[0]
        info1 = wuxing_colors[e1]
        analysis.append(f"本卦第一元素為「{e1}」，對應{info1['color']}，方位在{info1['direction']}，數字為{info1['numbers'][0]}與{info1['numbers'][1]}，色系包含{info1['details']}。")
    
    # 第二個元素
    if elements[1] in wuxing_colors:
        e2 = elements[1]
        info2 = wuxing_colors[e2]
        analysis.append(f"本卦第二元素為「{e2}」，對應{info2['color']}，方位在{info2['direction']}，數字為{info2['numbers'][0]}與{info2['numbers'][1]}，色系包含{info2['details']}。")
    
    # 兩元素關係
    if elements[0] in wuxing_colors and elements[1] in wuxing_colors:
        relation = analyze_wuxing_relation(elements[0], elements[1])
        analysis.append(relation)
    
    return "\n\n".join(analysis)

# 分析兩個五行元素的關係
def analyze_wuxing_relation(e1, e2):
    # 五行相生關係：木生火，火生土，土生金，金生水，水生木
    # 五行相剋關係：木剋土，土剋水，水剋火，火剋金，金剋木
    
    relations = {
        ("木", "火"): "第一元素「木」生第二元素「火」，為相生關係，象徵成長與發展。",
        ("火", "土"): "第一元素「火」生第二元素「土」，為相生關係，象徵轉化與堅實。",
        ("土", "金"): "第一元素「土」生第二元素「金」，為相生關係，象徵孕育與收穫。",
        ("金", "水"): "第一元素「金」生第二元素「水」，為相生關係，象徵釋放與流通。",
        ("水", "木"): "第一元素「水」生第二元素「木」，為相生關係，象徵滋養與成長。",
        
        ("木", "土"): "第一元素「木」剋第二元素「土」，為相剋關係，象徵突破與挑戰。",
        ("土", "水"): "第一元素「土」剋第二元素「水」，為相剋關係，象徵抑制與阻隔。",
        ("水", "火"): "第一元素「水」剋第二元素「火」，為相剋關係，象徵控制與熄滅。",
        ("火", "金"): "第一元素「火」剋第二元素「金」，為相剋關係，象徵改變與融化。",
        ("金", "木"): "第一元素「金」剋第二元素「木」，為相剋關係，象徵約束與限制。",
        
        # 同元素
        ("木", "木"): "本卦為雙「木」屬性，象徵旺盛的生命力與創造力，具有強大的成長潛能。",
        ("火", "火"): "本卦為雙「火」屬性，象徵熱情與光明，充滿活力與照耀的能量。",
        ("土", "土"): "本卦為雙「土」屬性，象徵穩固與包容，具有深厚的底蘊與承載力。",
        ("金", "金"): "本卦為雙「金」屬性，象徵堅決與剛毅，具有清晰的判斷力與執行力。",
        ("水", "水"): "本卦為雙「水」屬性，象徵智慧與適應，具有靈活的思維與深遠的洞察力。"
    }
    
    # 檢查是否存在預定義的關係
    key = (e1, e2)
    if key in relations:
        return relations[key]
    
    # 如果沒有預定義的關係，返回基於五行基本理論的關係
    cycles = {
        ("火", "木"): "第二元素「木」生第一元素「火」，顯示本卦中有潛在的支持力量。",
        ("土", "火"): "第二元素「火」生第一元素「土」，顯示本卦中有轉化的能量。",
        ("金", "土"): "第二元素「土」生第一元素「金」，顯示本卦中有成熟的基礎。",
        ("水", "金"): "第二元素「金」生第一元素「水」，顯示本卦中有釋放的潛能。",
        ("木", "水"): "第二元素「水」生第一元素「木」，顯示本卦中有滋養的來源。",
        
        ("土", "木"): "第二元素「木」剋第一元素「土」，顯示本卦中有挑戰與制約。",
        ("水", "土"): "第二元素「土」剋第一元素「水」，顯示本卦中有阻礙與限制。",
        ("火", "水"): "第二元素「水」剋第一元素「火」，顯示本卦中有控制的力量。",
        ("金", "火"): "第二元素「火」剋第一元素「金」，顯示本卦中有變革的因素。",
        ("木", "金"): "第二元素「金」剋第一元素「木」，顯示本卦中有約束的影響。"
    }
    
    key = (e1, e2)
    if key in cycles:
        return cycles[key]
    
    return f"元素「{e1}」與「{e2}」之間的關係較為複雜。"

# 帶有指數退避重試的API請求函數
def api_request_with_retry(prompt, max_retries=args.max_retries, initial_delay=args.initial_delay):
    if args.dry_run:
        return {"success": True, "text": "這是一個測試運行，不實際生成內容。"}
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": args.model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with expertise in I Ching (Book of Changes). Always respond in Traditional Chinese."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    retry_count = 0
    delay = initial_delay
    
    while retry_count <= max_retries:
        try:
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))
            
            # 如果請求成功
            if response.status_code == 200:
                response_json = response.json()
                
                # 從回應中提取生成的文字
                if "choices" in response_json and len(response_json["choices"]) > 0:
                    if "message" in response_json["choices"][0]:
                        message = response_json["choices"][0]["message"]
                        if "content" in message:
                            return {"success": True, "text": message["content"].strip()}
                
                return {"success": False, "text": "無法從API回應中提取文字", "response": response_json}
            
            # 如果遇到429錯誤（請求過多）
            elif response.status_code == 429:
                retry_count += 1
                if retry_count > max_retries:
                    return {"success": False, "text": f"達到最大重試次數 ({max_retries})，API請求仍然失敗: 429 Too Many Requests"}
                
                # 計算等待時間（指數退避 + 隨機抖動）
                jitter = random.uniform(0, 0.1 * delay)
                wait_time = delay + jitter
                print(f"API請求受限 (429 Too Many Requests)，等待 {wait_time:.2f} 秒後重試 ({retry_count}/{max_retries})...")
                time.sleep(wait_time)
                
                # 增加下次重試的延遲時間（指數退避）
                delay *= 2
            
            # 其他HTTP錯誤
            else:
                return {"success": False, "text": f"API請求失敗: {response.status_code} {response.reason}", "response": response.text}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "text": f"API請求錯誤: {e}"}
    
    return {"success": False, "text": "達到最大重試次數，API請求仍然失敗"}

# 使用OpenAI API生成說明內容
def generate_description(gua_name, gua_attribute, yin_yang, gua_words, literal_translation="", symbolism=""):
    if args.dry_run:
        return "這是一個測試運行，不實際生成內容。"
        
    # 獲取五行解析
    wuxing_analysis = get_wuxing_analysis(gua_attribute)
        
    prompt = f"""
    請根據以下易經卦象資訊，生成一段說明文字，解釋如果抽到這個卦象代表的意義：
    
    卦名：{gua_name}
    屬性：{gua_attribute}
    陰陽：{yin_yang}
    卦詞：{gua_words}
    直譯：{literal_translation if literal_translation else "無"}
    象徵：{symbolism if symbolism else "無"}
    五行解析：{wuxing_analysis}
    
    請提供一段簡潔有半古文風格一點的解釋，例如:天行自強(前面這些個字要加粗，而且要四個字) 天道運行不息，君子當效法，自強奮進，永不懈怠 這樣就好 不用過多解釋 。
    """
    
    result = api_request_with_retry(prompt)
    
    if result["success"]:
        return result["text"]
    else:
        print(f"生成說明內容時出錯: {result['text']}")
        return "無法生成說明內容。"

# 使用OpenAI API生成關鍵字
def generate_keywords(gua_name, gua_attribute, yin_yang, gua_words, literal_translation="", symbolism=""):
    if args.dry_run:
        return ["測試", "關鍵字", "不實際", "生成", "內容"]
        
    # 獲取五行解析的簡短版本
    elements = parse_attribute(gua_attribute)
    wuxing_brief = ""
    if elements[0] != "未知" and elements[1] != "未知":
        wuxing_brief = f"本卦五行屬性為「{elements[0]}{elements[1]}」"
        
    prompt = f"""
    請根據以下易經卦象資訊，生成4個關鍵字，這些關鍵字應該能概括這個卦象的核心含義：
    
    卦名：{gua_name}
    屬性：{gua_attribute}
    陰陽：{yin_yang}
    卦詞：{gua_words}
    直譯：{literal_translation if literal_translation else "無"}
    象徵：{symbolism if symbolism else "無"}
    五行簡述：{wuxing_brief}
    
    請只回覆4個關鍵字，每個關鍵字應為單詞或短語，用逗號分隔。盡量結合卦象的五行屬性特點。
    """
    
    result = api_request_with_retry(prompt)
    
    if result["success"]:
        keywords_text = result["text"]
        # 將關鍵字文字轉換為列表
        keywords = [kw.strip() for kw in keywords_text.split(",")]
        return keywords[:4]  # 確保只有4個關鍵字
    else:
        print(f"生成關鍵字時出錯: {result['text']}")
        return ["無法生成關鍵字"]

# 測試API連接
if not args.dry_run:
    print("測試OpenAI API連接...")
    try:
        test_prompt = "Hello, World!"
        result = api_request_with_retry(test_prompt, max_retries=1)
        if result["success"]:
            print("API連接測試成功！")
        else:
            print(f"API連接測試失敗: {result['text']}")
            sys.exit(1)
    except Exception as e:
        print(f"API連接測試失敗: {e}")
        sys.exit(1)

# 為每個卦象生成MD檔案
success_count = 0
error_count = 0
skip_count = 0

# 過濾要處理的卦象
filtered_data = []
for index, item in enumerate(data):
    # 檢查是否有卦名
    if "卦名" not in item or not item["卦名"]:
        print(f"跳過第 {index+1} 筆資料：卦名缺失")
        continue
        
    # 提取卦名中的數字部分
    gua_name = item["卦名"]
    
    # 使用正則表達式提取卦號
    match = re.search(r'(\d+)', gua_name)
    if not match:
        print(f"跳過第 {index+1} 筆資料：卦名中找不到數字 '{gua_name}'")
        continue
        
    gua_number = match.group(1)  # 例如從 "01 乾為天" 或 "64火水未濟" 提取 "01" 或 "64"
    
    # 移除前導零並轉換為整數
    try:
        gua_num_int = int(gua_number.lstrip("0"))
    except ValueError:
        print(f"跳過第 {index+1} 筆資料：卦號格式不正確 '{gua_number}'")
        continue
    
    # 檢查是否在指定範圍內
    if args.start and gua_num_int < args.start:
        continue
    if args.end and gua_num_int > args.end:
        continue
    
    filtered_data.append((index, item, gua_num_int, gua_number))

# 按卦號排序
filtered_data.sort(key=lambda x: x[2])

print(f"將處理 {len(filtered_data)} 個卦象")

for index, item, gua_num_int, gua_number in filtered_data:
    try:
        # 提取卦名
        gua_name = item["卦名"]
        
        # 移除前導零
        file_number = str(gua_num_int)
        
        # 檢查檔案是否已存在
        file_path = os.path.join(output_dir, f"{file_number}.md")
        if os.path.exists(file_path) and not args.force:
            print(f"檔案 {file_path} 已存在，跳過生成")
            skip_count += 1
            continue
        
        # 處理可能的缺失值
        gua_attribute = item.get("屬性", "未知")
        yin_yang = item.get("陰陽", "未知")
        gua_words = item.get("卦詞", "無卦詞")
        literal_translation = item.get("直譯", "")
        symbolism = item.get("象徵", "")
        
        # 生成說明內容
        print(f"正在為 {gua_name} 生成說明內容...")
        description = generate_description(
            gua_name=gua_name,
            gua_attribute=gua_attribute,
            yin_yang=yin_yang,
            gua_words=gua_words,
            literal_translation=literal_translation,
            symbolism=symbolism
        )
        
        # 生成關鍵字
        print(f"正在為 {gua_name} 生成關鍵字...")
        keywords = generate_keywords(
            gua_name=gua_name,
            gua_attribute=gua_attribute,
            yin_yang=yin_yang,
            gua_words=gua_words,
            literal_translation=literal_translation,
            symbolism=symbolism
        )
        
        # 創建關鍵字部分
        keywords_section = "\n".join([f"- {keyword}" for keyword in keywords])
        
        # 創建MD檔案內容
        md_content = f"""# {gua_name}

## 基本資訊
- 屬性：{gua_attribute}
- 陰陽：{yin_yang}
## 卦詞
{gua_words}
### 直譯 : {literal_translation}
### 象徵 : {symbolism}
## 說明
{description}
### 關鍵字：{keywords_section}
## 五行解析
{get_wuxing_analysis(gua_attribute)}

"""
        
        # 寫入MD檔案
        if not args.dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"已生成 {file_path}")
        else:
            print(f"將生成 {file_path}")
        
        success_count += 1
        
        # 避免API請求過於頻繁
        if not args.dry_run:
            # 在每次成功生成後添加隨機延遲（5-10秒）
            delay = random.uniform(5, 10)
            print(f"等待 {delay:.2f} 秒後繼續...")
            time.sleep(delay)
    
    except Exception as e:
        print(f"處理卦象時出錯: {e}")
        import traceback
        traceback.print_exc()
        error_count += 1

print(f"\n處理完成！成功生成 {success_count} 個檔案，跳過 {skip_count} 個，失敗 {error_count} 個。")
if args.dry_run:
    print("注意：這是一個測試運行，沒有實際生成任何檔案。") 