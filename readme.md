# 项目简介

本项目是一个将指定目录下的 PDF 文件批量转换为 Markdown 文件的工具，基于开源项目 [marker](https://github.com/VikParuchuri/marker)。
该工具支持处理嵌套文件夹下的 PDF 文件，并保证目标文件夹下的子目录结构与源文件夹下的子目录结构一致。

## 环境要求

1. Python >= 3.10（最低 3.10，否则无法运行）
2. 安装 PyTorch（有 GPU 时请安装 GPU 版本）
3. 安装 marker 包（务必提前安装好 PyTorch，否则将默认安装 CPU 版本，影响生成速度）

## 功能说明

1. 支持处理嵌套文件夹下的 PDF 文件
2. 支持保证目标文件夹下的子目录结构与源文件夹下的子目录结构一致
3. 支持记录处理日志，方便故障时从故障点继续处理
4. 支持多次调用，内部加载模型，避免重复加载浪费时间
5. 支持跳过已经处理过的文件，避免重复处理

## 使用说明

### 参数设置

- `source_dir`: 源 PDF 文件路径
- `source_prefix`: 源 PDF 文件路径前缀
- `target_prefix`: 转换后的 Markdown 文件存放路径前缀
- `process_log_path`: 记录处理日志的路径

### 示例调用

```python
if __name__ == "__main__":
    source_dir = "/workspace/marker/source/a"
    source_prefix = "/workspace/marker/source/a"
    target_prefix = "/workspace/marker/target/bc"
    process_log_path = "/workspace/marker/process_log.log"

    pdf2md_main(source_dir, source_prefix, target_prefix, process_log_path)
```

## 许可证

本项目使用 [GPL-3.0 License](./LICENSE) 协议。您可以自由地使用、修改和分发本项目，但必须保留原作者信息，并且在分发时必须使用相同的许可证。
