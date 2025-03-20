# Laptop Infers 程序开发提示词

## 项目背景

需要开发一个Python程序，用于处理多个包含`laptop_infers.json`文件的目录，提取笔记本电脑瑕疵检测信息，并将结果输出为CSV和JSON格式。

## 功能需求

### 1. 核心功能

- 遍历指定目录及其子目录，寻找以下文件：
  - `laptop_infers.json` - 主要数据文件
  - `qc_result_*` - QC结果文件
  - `inference_*` - 推理日志文件

- 从`laptop_infers.json`文件提取瑕疵检测信息：
  - 笔记本键值
  - 是否有瑕疵
  - 瑕疵评分
  - 瑕疵区域名称
  - 瑕疵边界框
  - 匹配分数
  - 时间戳

- 从`inference_*`文件分析mask缺失问题：
  - 提取包含"Transformation not possible"的行
  - 从这些行中提取区域名称（如"Front_04"）
  - 记录mask_miss信息到结果中

- 输出数据到两种格式：
  - CSV文件 - 方便电子表格查看，mask_miss以逗号分隔的字符串表示
  - JSON文件 - 保留完整数据结构，mask_miss保持列表格式

- 生成详细的日志记录：
  - 记录处理的文件数量
  - 记录成功和失败的处理
  - 提供错误的详细信息

### 2. 具体数据处理要求

#### JSON数据处理
- 解析`laptop_infers.json`文件中的数据
- 处理可能缺失的字段，提供默认值
- 使用pydantic模型进行数据验证

#### mask_miss提取
- 从`inference_*`文件中提取特定格式的信息
- 提取规则：在"Transformation not possible"前，从"]"到":"之间的文本
- 提取示例：
  ```
  [INFO][2025-02-23 09:47:39][inference_v2][LASA_02_BDCTO100DCS2M0AAAK_20250223094734_20250223-094736-488896] Front_04: Transformation not possible
  ```
  应提取"Front_04"并记录到mask_miss列表中

- mask_miss特殊值处理：
  - 找到匹配内容：记录区域名称列表（如["Front_04", "Top_01"]）
  - 未找到匹配内容：记录["none"]
  - 未找到inference文件：记录["no_log"]
  - 读取文件出错：记录["error"]

### 3. 输出格式

#### CSV文件
- 字段：laptop_key, defect, score, area_name, boxes, matched_score, timestamp, qc_result_file, mask_miss
- mask_miss字段以逗号分隔的字符串格式存储（如"Front_04, Top_01"）

#### JSON文件
- 保持与内存中相同的数据结构
- mask_miss字段保持列表格式

### 4. 日志记录

- 记录程序开始和结束时间
- 记录用户信息
- 记录处理的文件总数
- 记录成功和失败的文件数
- 失败时详细记录文件路径、所在文件夹、文件名等信息

## 技术要求

### 1. 项目结构

需要创建的文件：
- `process_laptop_infers.py` - 核心处理逻辑
- `main.py` - 程序入口
- `schema.py` - 数据模型定义（已提供）
- `requirements.txt` - 依赖包列表
- `pyproject.toml` - 项目配置
- `README.md` - 使用说明

### 2. 开发环境

- Python 3.12+
- 依赖包：
  - pydantic >= 2.0.0
  - typing-extensions >= 4.0.0
  - pathlib >= 1.0.1

### 3. 函数与类设计

#### LaptopInfersProcessor类

应包含以下方法：
- `__init__` - 初始化处理器，设置日志系统
- `find_json_files` - 遍历文件夹寻找文件
- `read_inference_file` - 读取并解析inference文件
- `read_json_file` - 读取JSON文件
- `parse_json_data` - 解析JSON数据
- `find_matching_box_info` - 查找匹配的瑕疵点信息
- `process_json_data` - 处理JSON数据
- `write_to_csv` - 写入CSV和JSON文件
- `process` - 执行完整处理流程

#### main模块

应包含以下内容：
- `main` 函数 - 程序入口
- 处理命令行参数（如果需要）
- 异常处理

## 详细实现指南

### 1. 初始化处理器

```python
def __init__(self, input_folder: str, output_csv: str):
    """初始化处理器"""
    # 设置输入输出路径
    # 创建日志目录
    # 设置日志记录器
    # 记录开始处理信息
```

### 2. 查找文件

```python
def find_json_files(self) -> List[Tuple[Path, str, str]]:
    """查找laptop_infers.json、qc_result_和inference_文件"""
    # 遍历输入目录及子目录
    # 找到laptop_infers.json文件
    # 查找同目录下的qc_result_和inference_文件
    # 返回文件路径元组列表
```

### 3. 读取inference文件

```python
def read_inference_file(self, folder_path: Path, filename: str) -> List[str]:
    """读取并解析inference文件"""
    # 检查文件是否存在
    # 读取文件内容
    # 使用正则表达式查找匹配内容
    # 返回提取的区域名称列表
```

### 4. 处理JSON数据

```python
def process_json_data(self, json_data: Dict, qc_result_file: str, mask_miss_areas: List[str]) -> List[Dict]:
    """处理JSON数据"""
    # 解析JSON数据
    # 提取laptop_key和瑕疵信息
    # 检查labels信息
    # 创建结果字典列表
    # 返回处理结果
```

### 5. 写入文件

```python
def write_to_csv(self, all_results: List[Dict]):
    """写入CSV和JSON文件"""
    # 检查结果是否为空
    # 将结果写入JSON文件
    # 准备CSV数据（将mask_miss转换为字符串）
    # 写入CSV文件
    # 记录写入信息
```

### 6. 处理流程

```python
def process(self):
    """执行完整处理流程"""
    # 查找所有文件
    # 记录处理开始信息
    # 处理每个文件
    # 记录成功和失败信息
    # 写入结果到文件
    # 记录处理完成信息
```

## 使用说明

最终程序应该可以通过以下方式运行：

```bash
python main.py
```

程序将处理当前目录及其子目录中的所有文件，生成结果文件和日志。

## 特别说明

程序需要记录以下特定信息：
- 程序开始时间：2025-03-20 02:44:05 UTC
- 用户登录名：hmjack2008