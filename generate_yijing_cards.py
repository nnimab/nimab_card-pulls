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
parser.add_argument('--api-key', help='Gemini API金鑰')
parser.add_argument('--start', type=int, help='起始卦象編號（1-64）')
parser.add_argument('--end', type=int, help='結束卦象編號（1-64）')
parser.add_argument('--force', action='store_true', help='強制重新生成已存在的檔案')
parser.add_argument('--dry-run', action='store_true', help='僅顯示將要生成的檔案，不實際生成')
parser.add_argument('--max-retries', type=int, default=5, help='API請求最大重試次數')
parser.add_argument('--initial-delay', type=float, default=2.0, help='初始重試延遲時間（秒）')
args = parser.parse_args()

# 設定API金鑰（優先使用命令行參數，其次使用環境變數，最後使用預設值）
GEMINI_API_KEY = args.api_key or os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY and not args.dry_run:
    print("錯誤：未提供Gemini API金鑰。請使用 --api-key 參數或設置 GEMINI_API_KEY 環境變數。")
    sys.exit(1)

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro-exp-02-05:generateContent?key={GEMINI_API_KEY}"

# 確保目標目錄存在
output_dir = "card-descriptions/yijing"
os.makedirs(output_dir, exist_ok=True)

# 讀取Excel檔案
excel_file = "掛卡排版database.xlsx"
if not os.path.exists(excel_file):
    print(f"錯誤：找不到Excel檔案 '{excel_file}'")
    sys.exit(1)

try:
    df = pd.read_excel(excel_file)
    print(f"成功讀取Excel檔案，共有 {len(df)} 行資料")
except Exception as e:
    print(f"讀取Excel檔案時出錯: {e}")
    sys.exit(1)

# 帶有指數退避重試的API請求函數
def api_request_with_retry(prompt, max_retries=args.max_retries, initial_delay=args.initial_delay):
    if args.dry_run:
        return {"success": True, "text": "這是一個測試運行，不實際生成內容。"}
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
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
                if "candidates" in response_json and len(response_json["candidates"]) > 0:
                    if "content" in response_json["candidates"][0]:
                        content = response_json["candidates"][0]["content"]
                        if "parts" in content and len(content["parts"]) > 0:
                            return {"success": True, "text": content["parts"][0]["text"].strip()}
                
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

# 使用Gemini API生成說明內容
def generate_description(gua_name, gua_attribute, yin_yang, gua_words):
    if args.dry_run:
        return "這是一個測試運行，不實際生成內容。"
        
    prompt = f"""
    請根據以下易經卦象資訊，生成一段說明文字，解釋如果抽到這個卦象代表的意義：
    
    卦名：{gua_name}
    屬性：{gua_attribute}
    陰陽：{yin_yang}
    卦詞：{gua_words}
    
    請提供一段簡潔但有深度的解釋，包括這個卦象在現代生活中的啟示和指導意義。
    """
    
    result = api_request_with_retry(prompt)
    
    if result["success"]:
        return result["text"]
    else:
        print(f"生成說明內容時出錯: {result['text']}")
        return "無法生成說明內容。"

# 使用Gemini API生成關鍵字
def generate_keywords(gua_name, gua_attribute, yin_yang, gua_words):
    if args.dry_run:
        return ["測試", "關鍵字", "不實際", "生成", "內容"]
        
    prompt = f"""
    請根據以下易經卦象資訊，生成5個關鍵字，這些關鍵字應該能概括這個卦象的核心含義：
    
    卦名：{gua_name}
    屬性：{gua_attribute}
    陰陽：{yin_yang}
    卦詞：{gua_words}
    
    請只回覆5個關鍵字，每個關鍵字應為單詞或短語，用逗號分隔。
    """
    
    result = api_request_with_retry(prompt)
    
    if result["success"]:
        keywords_text = result["text"]
        # 將關鍵字文字轉換為列表
        keywords = [kw.strip() for kw in keywords_text.split(",")]
        return keywords[:5]  # 確保只有5個關鍵字
    else:
        print(f"生成關鍵字時出錯: {result['text']}")
        return ["無法生成關鍵字"]

# 測試API連接
if not args.dry_run:
    print("測試API連接...")
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
filtered_rows = []
for index, row in df.iterrows():
    # 檢查是否有卦名
    if pd.isna(row["卦名"]) or not row["卦名"]:
        print(f"跳過第 {index+1} 行：卦名缺失")
        continue
        
    # 提取卦名中的數字部分
    gua_name = row["卦名"]
    
    # 使用正則表達式提取卦號
    match = re.search(r'(\d+)', gua_name)
    if not match:
        print(f"跳過第 {index+1} 行：卦名中找不到數字 '{gua_name}'")
        continue
        
    gua_number = match.group(1)  # 例如從 "01 乾為天" 或 "64火水未濟" 提取 "01" 或 "64"
    
    # 移除前導零並轉換為整數
    try:
        gua_num_int = int(gua_number.lstrip("0"))
    except ValueError:
        print(f"跳過第 {index+1} 行：卦號格式不正確 '{gua_number}'")
        continue
    
    # 檢查是否在指定範圍內
    if args.start and gua_num_int < args.start:
        continue
    if args.end and gua_num_int > args.end:
        continue
    
    filtered_rows.append((index, row, gua_num_int, gua_number))

# 按卦號排序
filtered_rows.sort(key=lambda x: x[2])

print(f"將處理 {len(filtered_rows)} 個卦象")

for index, row, gua_num_int, gua_number in filtered_rows:
    try:
        # 提取卦名
        gua_name = row["卦名"]
        
        # 移除前導零
        file_number = str(gua_num_int)
        
        # 檢查檔案是否已存在
        file_path = os.path.join(output_dir, f"{file_number}.md")
        if os.path.exists(file_path) and not args.force:
            print(f"檔案 {file_path} 已存在，跳過生成")
            skip_count += 1
            continue
        
        # 處理可能的缺失值
        gua_attribute = row["屬性"] if not pd.isna(row["屬性"]) else "未知"
        yin_yang = row["陰陽"] if not pd.isna(row["陰陽"]) else "未知"
        gua_words = row["卦詞"] if not pd.isna(row["卦詞"]) else "無卦詞"
        
        # 生成說明內容
        print(f"正在為 {gua_name} 生成說明內容...")
        description = generate_description(
            gua_name=gua_name,
            gua_attribute=gua_attribute,
            yin_yang=yin_yang,
            gua_words=gua_words
        )
        
        # 生成關鍵字
        print(f"正在為 {gua_name} 生成關鍵字...")
        keywords = generate_keywords(
            gua_name=gua_name,
            gua_attribute=gua_attribute,
            yin_yang=yin_yang,
            gua_words=gua_words
        )
        
        # 創建關鍵字部分
        keywords_section = "\n".join([f"- {keyword}" for keyword in keywords])
        
        # 創建MD檔案內容
        md_content = f"""# {gua_name}

## 基本資訊
- 卦號：{gua_number}
- 屬性：{gua_attribute}
- 陰陽：{yin_yang}

## 卦詞
{gua_words}

## 說明
{description}

## 關鍵字
{keywords_section}
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