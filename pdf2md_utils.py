'''
# pdf转markdown

环境说明：
1. python>=3.10（最低3.10，否则一定无法运行）
2. 安装pytorch（有gpu时请安装gpu版本）
3. 安装marker包（务必提前安装好pytorch，否则将默认安装cpu版本，影响生成速度）
```bash
pip install marker-pdf
```
程序说明：
1. 支持处理嵌套文件夹下的pdf文件
2. 支持保证目标文件夹下的子目录结构与源文件夹下的子目录结构一致
3. 支持记录处理日志，方便故障时从故障点继续处理
4. 支持多次调用，内部加载模型，避免重复加载浪费时间
5. 支持跳过已经处理过的文件，避免重复处理
'''
import os
from tqdm import tqdm
import time
import os
import json
from marker.convert import convert_single_pdf
from marker.models import load_all_models


# 基础工具函数
def get_subfolder_path(out_folder, fname):
    subfolder_name = fname.rsplit('.', 1)[0]
    subfolder_path = os.path.join(out_folder, subfolder_name)
    return subfolder_path

def get_markdown_filepath(out_folder, fname):
    subfolder_path = get_subfolder_path(out_folder, fname)
    out_filename = fname.rsplit(".", 1)[0] + ".md"
    out_filename = os.path.join(subfolder_path, out_filename)
    return out_filename

def markdown_exists(out_folder, fname):
    out_filename = get_markdown_filepath(out_folder, fname)
    return os.path.exists(out_filename)

def save_markdown(out_folder, fname, full_text, images, out_metadata):
    subfolder_path = get_subfolder_path(out_folder, fname)
    os.makedirs(subfolder_path, exist_ok=True)

    markdown_filepath = get_markdown_filepath(out_folder, fname)
    out_meta_filepath = markdown_filepath.rsplit(".", 1)[0] + "_meta.json"

    with open(markdown_filepath, "w+", encoding='utf-8') as f:
        f.write(full_text)
    with open(out_meta_filepath, "w+") as f:
        f.write(json.dumps(out_metadata, indent=4, ensure_ascii=False))

    for filename, image in images.items():
        image_filepath = os.path.join(subfolder_path, filename)
        image.save(image_filepath, "PNG")

    return subfolder_path


# 直接利用marker包的代码实现的转换单个pdf的方法
def my_convert_pdf(fpath, model_lst, out_folder):
    start = time.time()
    fname = os.path.basename(fpath)
    
    # 如果已经存在markdown文件则跳过
    if markdown_exists(out_folder, fname):
        print(f"Markdown file already exists for {fname}")
        return

    full_text, images, out_meta = convert_single_pdf(fpath, model_lst)
    subfolder_path = save_markdown(out_folder, fname, full_text, images, out_meta)
    print(f"Saved markdown to the {subfolder_path} folder")
    print(f"Total time: {time.time() - start}")


# 获取目录下所有子目录
def get_sub_dir(dir):
    sub_dirs = []
    for x in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, x)):
            # 拼接得到完整路径
            x = os.path.join(dir, x)
            sub_dirs.append(x)
    return sub_dirs


# 工具的主函数，遍历目录下的所有文件，并执行转md操作。输出路径是将文件路径中的指定前缀替换为另一个前缀
def process_files_in_directory(directory, source_prefix, target_prefix, model_lst=None):
    # 加载模型，防止反复加载浪费时间（便于多次调用）
    
    if model_lst is None:
        print("[Waring!] 在内部加载模型中！可能导致模型反复加载！")
        model_lst = load_all_models()

    if not os.path.exists(target_prefix):
        os.makedirs(target_prefix)
    
    # 获取所有文件路径
    all_files = []
    for root, dirs, files in os.walk(directory):
        # 打印当前所在的目录
        # for file in tqdm(files, desc=f"统计目录 {root}"): # 
        for file in files:
            all_files.append(os.path.join(root, file))

    # 使用 tqdm 打印进度条
    for file_path in tqdm(all_files, desc="Processing Files"):
        # print(file_path)
        try:
            target_dir = file_path.replace(source_prefix, target_prefix)
            # 去除最后的文件名
            target_dir = os.path.dirname(target_dir)
            # print("debug: ", target_dir)
            # 转md
            my_convert_pdf(file_path, model_lst, target_dir)
        except Exception as e:
            print("处理文件出错：", file_path, "跳过！")
            with open("/workspace/marker/error_3.log", "a+") as f:
                # 日期加错误日志
                f.write(f"time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
                f.write(f"{file_path} | Error processing : {str(e)}\n")
            with open("/workspace/marker/error_files_2.log", "a+") as f:
                f.write(file_path + "\n")

# 主函数，遍历目录下的所有子目录，并执行转md操作
def pdf2md_main(source_dir, source_prefix, target_prefix, process_log_path):

    # 获取源目录下的所有子目录
    sub_dirs = get_sub_dir(source_dir)
    print("Sub directories:")
    print(sub_dirs)

    # 加载模型
    print("Loading models...")
    model_lst = load_all_models()
    print("Models loaded.")

    # 在每个子目录下执行，方便故障时从子目录进行恢复. 日志记录当前处理的子目录
    with open(process_log_path, "w+") as f:
        for sub_dir in sub_dirs:
            # 时间+当前处理的子目录
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} {sub_dir}\n")
            print(f"Processing {sub_dir}")
            process_files_in_directory(sub_dir, source_prefix, target_prefix, model_lst)

if __name__ == "__main__":
    # main可以直接调用，也可以视为是一个示例调用的代码

    # 设置参数
    # 源pdf路径
    source_dir = "/workspace/marker/source/a" # 源pdf文件路径
    source_prefix = "/workspace/marker/source/a" # 源pdf文件路径前缀（与源文件路径不同的是，这里可以任选其中的部分作为前缀）
    target_prefix = "/workspace/marker/target/b" # 转换后的md文件存放路径前缀（原理是通过将源文件路径前缀替换为目标路径前缀，保证target目录下的各子目录与原始目录基本保持一致）
    process_log_path = "/workspace/marker/process_log.log" # 记录处理日志

    # 调用主函数
    pdf2md_main(source_dir, source_prefix, target_prefix, process_log_path)

