import os
import shutil
import argparse
from pathlib import Path

def move_images(source_dir, target_dir):
    """
    將 source_dir 中所有子資料夾的圖片移動到 target_dir，
    並在檔案名稱前加上原始資料夾的名稱
    """
    # 確保目標資料夾存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 獲取所有子資料夾
    subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    
    total_files = 0
    for subdir in subdirs:
        subdir_path = os.path.join(source_dir, subdir)
        
        # 獲取子資料夾中的所有檔案
        files = [f for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f))]
        
        for file in files:
            # 只處理圖片檔案
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # 原始檔案路徑
                source_file = os.path.join(subdir_path, file)
                
                # 新檔案名稱：只使用資料夾的名稱號碼，保留原始檔案格式
                file_extension = os.path.splitext(file)[1]
                new_filename = f"{subdir}{file_extension}"
                
                # 目標檔案路徑
                target_file = os.path.join(target_dir, new_filename)
                
                # 複製檔案
                shutil.copy2(source_file, target_file)
                print(f"已複製: {source_file} -> {target_file}")
                total_files += 1
    
    print(f"完成! 總共複製了 {total_files} 個檔案到 {target_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='將 yijing 資料夾中的圖片移動到目標資料夾')
    parser.add_argument('--source', default='images/yijing', help='源資料夾路徑')
    parser.add_argument('--target', default='images/yijing_output', help='目標資料夾路徑')
    
    args = parser.parse_args()
    
    # 將相對路徑轉換為絕對路徑
    source_dir = os.path.abspath(args.source)
    target_dir = os.path.abspath(args.target)
    
    print(f"源資料夾: {source_dir}")
    print(f"目標資料夾: {target_dir}")
    
    move_images(source_dir, target_dir) 