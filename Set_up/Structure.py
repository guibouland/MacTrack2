import os
import shutil

def copy_zip_files(input_folder, n):
    train_y_folder = os.path.join(input_folder, 'dataset/train/train_y')
    test_y_folder = os.path.join(input_folder, 'dataset/test/test_y')
    
    if not os.path.exists(test_y_folder):
        os.makedirs(test_y_folder, exist_ok=True)
    
    zip_files = sorted([f for f in os.listdir(train_y_folder) if f.endswith('.zip')])
    zip_count = len(zip_files)
    
    if zip_count == 0:
        print("No .zip files found in the train_y folder.")
        return
    
    for i in range(n):
        if i < zip_count:
            src_file = os.path.join(train_y_folder, zip_files[i])
        else:
            src_file = os.path.join(train_y_folder, zip_files[-1])
        dest_file = os.path.join(test_y_folder, f'{i:03d}_masks.zip')
        shutil.copy(src_file, dest_file)
        print(f"Copied {src_file} to {dest_file}")

input_folder = '/home/gbouland/Stage-LPHI-2024/input/norma/'
n = 266
copy_zip_files(input_folder, n)