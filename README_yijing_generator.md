# 易經卦象說明生成器

這個腳本用於生成易經64卦的MD格式說明檔案，使用Gemini API生成說明內容和關鍵字。

## 功能

- 從Excel檔案中讀取卦象資料
- 使用Gemini API生成說明內容和關鍵字
- 生成MD格式的卦象說明檔案
- 支持指定處理的卦象範圍
- 支持強制重新生成已存在的檔案
- 支持測試運行模式
- 內建API請求重試機制，處理請求限制問題

## 安裝依賴

```bash
pip install pandas openpyxl requests
```

## 使用方法

### 基本用法

```bash
python generate_yijing_cards.py --api-key YOUR_GEMINI_API_KEY
```

### 使用環境變數設置API金鑰

```bash
# 設置環境變數
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY  # Windows
# 或
export GEMINI_API_KEY=YOUR_GEMINI_API_KEY  # Linux/Mac

# 執行腳本
python generate_yijing_cards.py
```

### 指定處理的卦象範圍

```bash
# 處理第1卦到第10卦
python generate_yijing_cards.py --start 1 --end 10
```

### 強制重新生成已存在的檔案

```bash
python generate_yijing_cards.py --force
```

### 測試運行模式

```bash
python generate_yijing_cards.py --dry-run
```

### 自定義重試參數

```bash
# 設置最大重試次數為10，初始延遲為3秒
python generate_yijing_cards.py --max-retries 10 --initial-delay 3
```

## 參數說明

- `--api-key`: Gemini API金鑰
- `--start`: 起始卦象編號（1-64）
- `--end`: 結束卦象編號（1-64）
- `--force`: 強制重新生成已存在的檔案
- `--dry-run`: 僅顯示將要生成的檔案，不實際生成
- `--max-retries`: API請求最大重試次數（預設為5）
- `--initial-delay`: 初始重試延遲時間，單位為秒（預設為2.0）

## 輸出格式

生成的MD檔案格式如下：

```markdown
# 01 乾為天

## 基本資訊
- 卦號：01
- 屬性：金金
- 陰陽：陽

## 卦詞
天道剛健運行不息，君子應效法天道，自強而不止。

## 說明
[由Gemini API生成的說明內容]

## 關鍵字
- 關鍵字1
- 關鍵字2
- 關鍵字3
- 關鍵字4
- 關鍵字5
```

## 處理API限制

腳本內建了指數退避重試機制，當遇到API請求限制（429 Too Many Requests）時，會自動等待並重試：

1. 初始等待時間為`--initial-delay`參數指定的秒數（預設為2秒）
2. 每次重試失敗後，等待時間會翻倍（指數退避）
3. 等待時間會添加隨機抖動，避免多個請求同時重試
4. 最多重試`--max-retries`參數指定的次數（預設為5次）
5. 每次成功生成一個檔案後，會等待5-10秒的隨機時間再處理下一個

如果仍然遇到API限制問題，可以嘗試：
- 增加`--initial-delay`參數的值
- 增加`--max-retries`參數的值
- 使用`--start`和`--end`參數分批處理卦象

## 注意事項

1. 請確保Excel檔案`掛卡排版database.xlsx`位於腳本同一目錄下
2. 請確保有足夠的Gemini API配額
3. 生成的檔案將保存在`card-descriptions/yijing`目錄下
4. 檔案名稱為卦號，例如`1.md`、`2.md`等 