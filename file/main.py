import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

def save_image_with_size_limit(img, output_path, max_size_kb=200):
    """
    保存图像并调整质量以限制文件大小。
    """
    quality = 95  # 初始质量设为 95
    img.save(output_path, 'webp', optimize=True, quality=quality)

    # 如果文件大小超出限制，逐步降低质量
    while os.path.getsize(output_path) > max_size_kb * 1024 and quality > 10:
        quality -= 5  # 每次减少 5 的质量
        img.save(output_path, 'webp', optimize=True, quality=quality)

def convert_image(file_path, output_dir, max_size_kb):
    file_name = os.path.basename(file_path)
    try:
        with Image.open(file_path) as img:
            # 获取文件名（不带扩展名）
            file_name_without_ext = os.path.splitext(file_name)[0]
            # 保存为 WebP 格式到输出目录
            output_file_path = os.path.join(output_dir, f"{file_name_without_ext}.webp")
            save_image_with_size_limit(img, output_file_path, max_size_kb)
            return f"成功转换: {file_name} -> {file_name_without_ext}.webp"
    except Exception as e:
        return f"无法转换文件 {file_name}: {e}"

def convert_images_to_webp(input_dir, output_dir, max_size_kb=200):
    # 检查输出目录是否存在，如果不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取输入目录中的所有文件路径
    files = [os.path.join(input_dir, file_name) for file_name in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, file_name))]

    # 获取逻辑处理器的数量
    num_workers = multiprocessing.cpu_count()
    print(f"检测到 {num_workers} 个逻辑处理器，启动相应数量的线程进行并行处理...")

    # 使用 ThreadPoolExecutor 并行处理图像转换任务
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(convert_image, file, output_dir, max_size_kb) for file in files]
        
        for future in as_completed(futures):
            print(future.result())  # 打印每个任务的结果

def main():
    # 请求用户输入目录和输出目录
    input_dir = input("请输入输入目录的路径: ")
    output_dir = input("请输入输出目录的路径: ")

    # 设置最大文件大小
    max_size_kb = input("请输入单个文件的最大大小 (KB)，默认为 200KB: ")
    max_size_kb = int(max_size_kb) if max_size_kb.strip().isdigit() else 200

    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print("输入目录不存在！")
        return

    # 开始转换图片
    convert_images_to_webp(input_dir, output_dir, max_size_kb)
    print("所有图片已转换为 WebP 格式并输出到指定目录。")

if __name__ == "__main__":
    main()
