import os
import re
import shutil
from pathlib import Path

def rename_folders_and_images(root_dir):
    """
    重命名圖片資料夾和圖片檔案
    1. 將資料夾名稱只保留前面的數字
    2. 將每個資料夾中的圖片重命名為 01.png
    3. 刪除其他檔案（如 desktop.ini 和 hexagram_*_urls.txt）
    """
    # 確保根目錄存在
    root_path = Path(root_dir)
    if not root_path.exists() or not root_path.is_dir():
        print(f"錯誤：目錄 {root_dir} 不存在")
        return

    # 獲取所有資料夾
    yijing_path = root_path / "yijing"
    if not yijing_path.exists() or not yijing_path.is_dir():
        print(f"錯誤：目錄 {yijing_path} 不存在")
        return

    folders = [f for f in yijing_path.iterdir() if f.is_dir()]
    print(f"找到 {len(folders)} 個資料夾")

    # 處理每個資料夾
    for folder in folders:
        # 從資料夾名稱中提取數字
        match = re.match(r"(\d+)", folder.name)
        if match:
            number = match.group(1)
            new_folder_name = number
            new_folder_path = folder.parent / new_folder_name
            
            # 如果新資料夾已存在，先刪除它
            if new_folder_path.exists() and new_folder_path != folder:
                print(f"警告：資料夾 {new_folder_name} 已存在，將被覆蓋")
                shutil.rmtree(new_folder_path)
            
            # 找到所有圖片檔案
            image_files = []
            for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                image_files.extend(list(folder.glob(f"*{ext}")))
            
            if image_files:
                # 如果資料夾名稱需要更改
                if folder.name != new_folder_name:
                    # 創建新資料夾
                    if not new_folder_path.exists():
                        new_folder_path.mkdir(parents=True)
                    
                    # 複製第一個圖片到新資料夾並重命名為 01.png
                    first_image = image_files[0]
                    new_image_path = new_folder_path / "01.png"
                    shutil.copy2(first_image, new_image_path)
                    print(f"處理：{folder.name} -> {new_folder_name}，圖片：{first_image.name} -> 01.png")
                    
                    # 刪除原始資料夾
                    shutil.rmtree(folder)
                else:
                    # 資料夾名稱已經是數字，只需重命名圖片和刪除其他檔案
                    
                    # 刪除所有非圖片檔案
                    for file_path in folder.iterdir():
                        if file_path.is_file() and not any(file_path.name.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']):
                            file_path.unlink()
                            print(f"刪除檔案：{file_path.name}")
                    
                    # 重命名第一個圖片為 01.png
                    first_image = image_files[0]
                    new_image_path = folder / "01.png"
                    
                    # 如果第一個圖片不是 01.png，則重命名它
                    if first_image.name != "01.png":
                        # 如果 01.png 已存在但不是第一個圖片，先刪除它
                        if new_image_path.exists() and new_image_path != first_image:
                            new_image_path.unlink()
                        
                        # 複製第一個圖片為 01.png
                        shutil.copy2(first_image, new_image_path)
                        print(f"處理：{folder.name}，圖片：{first_image.name} -> 01.png")
                    
                    # 刪除所有其他圖片
                    for img in image_files:
                        if img.name != "01.png":
                            img.unlink()
                            print(f"刪除圖片：{img.name}")
            else:
                print(f"警告：資料夾 {folder.name} 中沒有找到圖片檔案")
        else:
            print(f"警告：資料夾 {folder.name} 不符合命名規則，將被跳過")

    print("完成！所有資料夾和圖片已重命名。")

if __name__ == "__main__":
    # 設置圖片根目錄
    images_dir = "images"
    rename_folders_and_images(images_dir) 