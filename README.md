# Laptop Infers 处理工具

一个用于处理多个包含 `laptop_infers.json` 文件的目录的 Python 工具。

## 功能

- 遍历指定目录及其子目录，查找所有 `laptop_infers.json` 文件
- 提取每个笔记本电脑的推理结果，包括瑕疵检测、分数和区域信息
- 从 inference 日志文件中提取 mask_miss 信息
- 从数据库中查询笔记本电脑的相关预测信息
- 生成详细的处理报告，包括 CSV 和 JSON 格式的输出文件
- 记录详细的处理日志，包括成功和失败的文件信息

## 使用方法

1. 确保 Python 3.12 或更高版本已安装
2. 安装所需依赖
3. 确保 `schema.py` 文件位于项目目录中
4. 运行 `main.py` 脚本

```bash
python main.py
```

或使用 uv（更快的 Python 包管理器）：

```bash
uv run [py_uv_laptop_infers的路徑]/main.py
```

程序默认处理当前目录及其子目录中的所有文件。

## 输出文件

- **CSV 文件** - `laptop_infers_results.csv`：包含所有提取的信息，方便在电子表格软件中查看
- **JSON 文件** - `laptop_infers_results.json`：保留完整的数据结构，便于程序化处理
- **日志文件** - 在 `logs` 目录下生成日志文件，记录处理过程中的详细信息

## CSV 文件字段说明

- `laptop_key`: 笔记本电脑的唯一标识
- `laptop_name`: 从 laptop_key 中提取的名称（第四个下划线之前的部分）
- `defect`: 是否检测到瑕疵 (True/False)
- `score`: 瑕疵分数，表示检测到瑕疵的置信度
- `area_name`: 瑕疵所在区域名称
- `boxes`: 瑕疵的边界框坐标
- `matched_score`: 匹配的分数
- `timestamp`: 时间戳
- `qc_result_file`: QC结果文件名
- `mask_miss`: 从inference日志中提取的mask缺失区域信息（以逗号分隔的字符串）
- `db_pred`: 从数据库中获取的预测结果
- `db_pred_score`: 从数据库中获取的预测分数
- `db_gt`: 从数据库中获取的真实标签

## mask_miss 特殊说明

`mask_miss` 字段包含以下可能的值：
- 区域名称列表（如 "Front_04, Top_01"）- 表示这些区域出现了 "Transformation not possible" 错误
- "none" - 表示未在 inference 文件中找到错误
- "no_log" - 表示未找到 inference 文件
- "error" - 表示读取 inference 文件时出错

## 数据库查询

程序会从数据库中查询以下信息：
- 笔记本电脑的预测结果 (pred)
- 预测分数 (pred_score)
- 真实标签 (gt)

如果查询失败，将返回以下值之一：
- "no-db" - 表示数据库文件不存在
- "no-sn" - 表示在数据库中未找到该笔记本电脑
- "error" - 表示数据库查询出错

## 依赖

- Python >= 3.12
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0
- pathlib >= 1.0.1
- sqlite3 (Python 标准库)

## 安装依赖

```bash
pip install -r requirements.txt
```

或使用 uv（更快的 Python 包管理器）：

```bash
uv pip install -r requirements.txt
```

或使用 uv sync 自動按 pyproject.toml 建立環境：

```bash
uv sync
```

## 项目结构

- `main.py` - 主程序入口
- `process_laptop_infers.py` - 核心处理逻辑
- `schema.py` - 数据结构定义
- `test_02.db` - SQLite 数据库，存储笔记本电脑信息和预测结果
- `logs/` - 日志文件目录
- `requirements.txt` - 依赖列表

## 开发说明

### 添加新功能

要添加新功能，可以扩展 `LaptopInfersProcessor` 类或修改现有的处理流程。主要的处理逻辑位于以下方法中：

- `find_json_files()` - 查找 JSON 文件
- `read_inference_file()` - 读取 inference 文件并提取 mask_miss 信息
- `process_json_data()` - 处理 JSON 数据并提取所需信息
- `write_to_csv()` - 将结果写入 CSV 文件

### 数据库配置

默认情况下，程序会在当前目录中查找名为 `test_02.db` 的 SQLite 数据库文件。可以通过修改 `main.py` 中的 `db_path` 变量来更改数据库位置。
