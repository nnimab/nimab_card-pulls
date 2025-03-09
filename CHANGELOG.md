# 變更日誌 (Changelog)

所有專案的顯著變更都將記錄在此檔案中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
並且本專案遵循 [語意化版本](https://semver.org/lang/zh-TW/)。

## [2.1.5] - 2024-03-09

### 新增
- 添加 GitHub Actions 工作流程，實現自動化部署
- 修改了以下檔案：
  - 新增 `.github/workflows/deploy.yml`: 設置自動部署工作流

### 優化
- 重新部署項目到 GitHub Pages
- 確保所有最新變更都已提交並推送

## [2.1.4] - 2023-03-09

### 優化
- 縮小放置區卡片右上角的屬性和陰陽顯示區域，提高整體布局平衡
- 修改了以下檔案：
  - `styles/main.css`: 修改 `.drawn-card-attribute` 樣式，將字體大小從 0.8em 減小到 0.65em
  - `styles/main.css`: 減小內邊距，從 2px 6px 縮小到 1px 3px
  - `styles/main.css`: 統一兩處 `.drawn-card-attribute` 樣式定義

## [2.1.3] - 2023-03-09

### 優化
- 改進放置區卡片的卦象名稱顯示方式，將卦號和卦名分成兩行顯示
- 修改了以下檔案：
  - `scripts/main.js`: 重構卡片名稱生成方式，分別生成卦號和卦名元素
  - `styles/main.css`: 添加 `.card-number` 和 `.card-name-only` 樣式，支持兩行顯示
  - `styles/main.css`: 修改 `.drawn-card-name` 樣式，使用 flex 布局實現垂直排列

## [2.1.2] - 2023-03-09

### 優化
- 縮小放置區卡片上的卦象名稱字體大小，提升視覺平衡
- 修改了以下檔案：
  - `styles/main.css`: 為 `.drawn-card-name` 添加 `font-size: 0.75em` 設定，使卡片名稱字體變小

## [2.1.1] - 2023-03-09

### 優化
- 放大所有卡片背面的圖案尺寸，使其更加明顯和精緻
- 修改了以下檔案：
  - `styles/main.css`: 將一般卡片背面的圖案從 70px x 70px 增加到 85px x 85px
  - `styles/main.css`: 將易經卦卡背面的圖案從 65px x 65px 增加到 80px x 80px
  - `styles/main.css`: 將人物卡背面的圖案從 60px x 60px 增加到 75px x 75px

## [2.1.0] - 2023-03-09

### 重大更新
- 全新卡片視覺設計系統
- 優化了卡片詳細資訊頁面的用戶體驗
- 為不同類型卡片增加獨特背面設計

### 新增
- 添加八卦太極圖案作為易經卦卡背面
- 添加星系圖案作為時空卡背面
- 添加藝術人形圖案作為人物卡背面

### 優化
- 改進卡片詳細資訊頁面的圖片顯示方式，提供更好的瀏覽體驗
- 調整卦詞文字區域，解決文字顯示問題
- 優化屬性和陰陽的顏色顯示

## [1.0.0] - 2023-03-09

### 新增
- 初始版本發布

## [1.0.1] - 2023-03-09

### 修改
- 卡片詳細資訊頁面的圖片比例調整為2:3
- 修改了以下檔案：
  - `styles/main.css`: 調整了 `.full-card-image` 和 `.card-detail-image` 的尺寸比例為2:3
  - `styles/main.css`: 將圖片顯示方式從 `object-fit: cover` 改為 `object-fit: contain`
  - `scripts/main.js`: 在 `createDetailView` 函數中添加圖片樣式以確保正確顯示

## [1.0.2] - 2023-03-09

### 修改
- 縮短卡片詳細資訊頁面圖片的上下長度
- 修復卡片詳細資訊中卦詞文字被遮擋的問題
- 修改了以下檔案：
  - `styles/main.css`: 將 `.full-card-image` 高度從600px調整為500px，調整較小螢幕下的相應高度
  - `styles/main.css`: 為 `.full-card-words` 添加z-index、position和margin-top，確保卦詞文字正確顯示

## [1.0.3] - 2023-03-09

### 修改
- 進一步縮減卡片圖片高度，為卦詞區域提供更多空間
- 全面優化卦詞顯示效果，解決文字被擠壓的問題
- 修改了以下檔案：
  - `styles/main.css`: 將 `.full-card-image` 高度從500px進一步降至420px
  - `styles/main.css`: 強化 `.full-card-words` 樣式，包括增加內邊距、背景不透明度、行高和字體大小
  - `styles/main.css`: 為 `.full-card-words` 添加圓角和陰影，提高視覺層次感

## [1.0.4] - 2023-03-09

### 修復
- 修復卦詞文字在右側被截斷的問題
- 修改了以下檔案：
  - `styles/main.css`: 調整 `.full-card-view` 容器的最大寬度和內邊距
  - `styles/main.css`: 為 `.full-card-words` 和 `.card-detail-content` 添加 `box-sizing: border-box`
  - `styles/main.css`: 為 `.full-card-words` 添加文字處理屬性，確保長文字能夠正確換行不溢出

## [1.0.5] - 2023-03-09

### 修改
- 調整卡片詳細資訊頁面中的圖片顯示方式，讓圖片填滿框框
- 修復卡片頂部屬性和陰陽的顏色顯示
- 修改了以下檔案：
  - `styles/main.css`: 將 `.full-card-image img` 的 `object-fit` 從 `contain` 改為 `cover`，讓圖片填滿容器
  - `styles/main.css`: 為 `.full-card-image` 調整樣式，添加背景色和移除圓角
  - `scripts/main.js`: 修改 `createDetailView` 函數，為五行屬性（金木水火土）設置對應的顏色

## [1.0.6] - 2023-03-09

### 修正
- 修正五行屬性的顏色設置
- 修改了以下檔案：
  - `scripts/main.js`: 將金的顏色從金黃色(#FFD700)改為白色(#FFFFFF)
  - `scripts/main.js`: 將水的顏色從水藍色(#00BCD4)改為灰色(#607D8B)

## [1.0.7] - 2023-03-09

### 修復
- 修復放置區卡片的屬性和陰陽顏色顯示
- 修改了以下檔案：
  - `scripts/main.js`: 更新 `handleCardDraw` 函數中的卡片顯示代碼，為陰陽和各個屬性字符分別設置正確的顏色

## [1.0.8] - 2023-03-09

### 修改
- 將卡片背面的星形符號更改為八卦陰陽圖案
- 修改了以下檔案：
  - `styles/main.css`: 更新 `.card::before` 樣式，使用SVG實現八卦陰陽圖案
  - `styles/main.css`: 為不同類型的卡片調整陰陽圖案的大小

## [1.0.9] - 2023-03-09

### 美化
- 升級卡片背面的圖案為完整八卦太極圖，參考用戶提供的圖片設計
- 修改了以下檔案：
  - `styles/main.css`: 重新設計 `.card::before` 的SVG圖案，添加八個卦象和黃色背景
  - `styles/main.css`: 加大所有卡片類型的背面圖案尺寸，提升視覺效果
  - `styles/main.css`: 增強陰影效果，使圖案在卡片背景上更加醒目

## [1.0.10] - 2023-03-09

### 細節調整
- 移除八卦太極圖案中的黃色背景，使其更加精緻和低調
- 調整八卦符號為白色，增強在卡片背景上的可見性
- 修改了以下檔案：
  - `styles/main.css`: 更新 `.card::before` 的SVG圖案，移除黃色背景圓圈
  - `styles/main.css`: 將外圍八卦符號的顏色從黑色改為白色，提高對比度

## [1.0.11] - 2023-03-09

### 特色增強
- 為不同類型的卡片設計專屬背面圖案，增強視覺差異
- 修改了以下檔案：
  - `styles/main.css`: 為易經卦卡保留太極八卦圖案
  - `styles/main.css`: 為時空卡設計宇宙星系主題圖案，包含旋轉星系和星星
  - `styles/main.css`: 為人物卡設計簡約人形圖案，具有頭部、身體、四肢和面部特徵
  - `styles/main.css`: 重構CSS結構，將不同卡片類型的樣式分開定義

## [1.0.12] - 2023-03-09

### 藝術優化
- 大幅提升人物卡背面圖案的精細度和藝術性
- 修改了以下檔案：
  - `styles/main.css`: 重新設計人物卡的SVG圖案，增加多項藝術細節
  - `styles/main.css`: 添加光環效果，呈現人物的神秘氣質
  - `styles/main.css`: 增加頭髮/頭飾、表情、手部細節
  - `styles/main.css`: 添加服飾/長袍效果，提高藝術表現力
  - `styles/main.css`: 增加裝飾線條和靈氣/能量流動效果 