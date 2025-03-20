# Laptop Infers 处理工具

一个用于处理多个包含 `laptop_infers.json` 文件的目录的 Python 工具。

## 功能

- 遍历指定目录中的所有子目录，找到 `laptop_infers.json` 文件以及对应的 `qc_result_` 文件和 `inference_` 文件
- 读取并解析 JSON 文件，提取笔记本电脑瑕疵检测信息
- 检查 JSON 文件中的 `labels` 信息，识别瑕疵位置和分数
- 从 `inference_` 文件中提取 `mask_miss` 信息，识别 "Transformation not possible" 错误
- 将提取的信息写入 CSV 和 JSON 文件，便于后续分析
- 详细记录处理过程中的成功和失败信息，提供完整的日志

## 使用方法

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
- `defect`: 是否检测到瑕疵 (True/False)
- `score`: 瑕疵分数，表示检测到瑕疵的置信度
- `area_name`: 瑕疵所在区域名称
- `boxes`: 瑕疵的边界框坐标
- `matched_score`: 匹配的分数
- `timestamp`: 时间戳
- `qc_result_file`: QC结果文件名
- `mask_miss`: 从inference日志中提取的mask缺失区域信息（以逗号分隔的字符串）

## mask_miss 特殊说明

`mask_miss` 字段包含以下可能的值：
- 区域名称列表（如 "Front_04, Top_01"）- 表示这些区域出现了 "Transformation not possible" 错误
- "none" - 表示未在 inference 文件中找到错误
- "no_log" - 表示未找到 inference 文件
- "error" - 表示读取 inference 文件时出错

## 依赖

- Python >= 3.12
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0
- pathlib >= 1.0.1

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

```
py_uv_laprop_infers/
├── main.py                # 程序入口
├── process_laptop_infers.py # 核心处理逻辑
├── schema.py              # 数据模型定义
├── requirements.txt       # 依赖包清单
├── pyproject.toml         # 项目配置
├── README.md              # 项目说明文档
└── logs/                  # 日志目录（程序运行时创建）
```
