import os

# 確保目錄存在
cards_dir = 'card-descriptions'
if not os.path.exists(cards_dir):
    os.makedirs(cards_dir)

# 生成第11到64張卡片的描述文件
for i in range(11, 65):
    filename = f'{cards_dir}/{i}.md'
    
    # 如果文件已存在，跳過
    if os.path.exists(filename):
        print(f'文件 {filename} 已存在，跳過')
        continue
    
    # 創建 Markdown 內容
    content = f'''# 第{i}張卡片

## 基本資訊
- 卡片編號：{i}
- 卡片類型：測試卡片
- 元素屬性：待定

## 詳細描述
這是第{i}張卡片的描述。

## 牌義解析
正位：
- 這是第{i}張卡片的正位含義
- 待補充
- 待補充
- 待補充

逆位：
- 這是第{i}張卡片的逆位含義
- 待補充
- 待補充
- 待補充

## 關鍵字
- 關鍵字1
- 關鍵字2
- 關鍵字3
- 關鍵字4
- 關鍵字5
'''
    
    # 寫入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'已創建文件：{filename}')

print('所有卡片描述文件生成完成！') 