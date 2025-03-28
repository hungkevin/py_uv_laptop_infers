# Laptop Infers 程序开发指南

## 项目背景

本项目旨在开发一个工具，用于处理和分析笔记本电脑瑕疵检测系统生成的推理数据。此工具能够遍历指定目录及其子目录，寻找所有的 `laptop_infers.json` 文件，提取关键信息，并将这些信息整合到一个CSV文件中，方便后续分析。

## 功能需求

### 1. 核心功能

- 递归遍历指定目录，查找所有 `laptop_infers.json` 文件
- 从 JSON 文件中提取推理结果数据
- 从相同目录下的 `inference_*` 文件中提取 mask_miss 信息
- 从数据库中查询相关预测信息
- 将提取的数据整合到 CSV 和 JSON 输出文件中
- 生成详细的处理日志

### 2. 具体数据处理要求

#### JSON 数据处理
- 解析 `laptop_infers.json` 文件，从中提取 laptop_key、defect、score 等信息
- 处理 laptop_key，提取 laptop_name（第四个下划线之前的字符串）
- 处理 JSON 缺失字段，为 score_thr 和 box_size_thr 等字段添加默认值
- 在 labels 中查找与 results.score 匹配的瑕疵点，提取 area_name、boxes 和 matched_score

#### mask_miss提取
- 从 `inference_*` 文件中提取特定格式的信息
- 提取规则：在 "Transformation not possible" 前，匹配区域名称
- 示例：`[INFO][2025-02-23 09:47:39][inference_v2][LASA_02_BDCTO100DCS2M0AAAK_20250223094734_20250223-094736-488896] Front_04: Transformation not possible`
  应提取 "Front_04" 并记录到 mask_miss 列表中

- mask_miss 特殊值处理：
  - 找到匹配内容：记录区域名称列表（如 ["Front_04", "Top_01"]）
  - 未找到匹配内容：记录 ["none"]
  - 未找到 inference 文件：记录 ["no_log"]
  - 读取文件出错：记录 ["error"]

#### 数据库查询
- 从 SQLite 数据库中查询笔记本电脑的相关预测信息
- 使用 laptop_name 在 laptops 表中查找记录
- 通过 laptop_id 关联查询 laptop_defect_predictions 表中的预测结果
- 提取 pred、pred_score 和 gt 字段
- 处理查询失败情况：
  - 数据库不存在：返回 "no-db"
  - 没有找到记录：返回 "no-sn"
  - 查询出错：返回 "error"

### 3. 输出格式

#### CSV文件
- 字段：laptop_key, laptop_name, defect, score, area_name, boxes, matched_score, timestamp, qc_result_file, mask_miss, db_pred, db_pred_score, db_gt
- mask_miss 字段以逗号分隔的字符串格式存储（如 "Front_04, Top_01"）
- 使用 utf-8-sig 编码，确保 Excel 能正确显示中文

#### JSON文件
- 保持与内存中相同的数据结构
- mask_miss 字段保持列表格式，方便程序化处理
- 使用 ensure_ascii=False 确保正确输出中文字符

### 4. 日志记录

- 记录程序开始和结束时间
- 记录用户信息
- 记录处理的文件总数
- 记录成功和失败的文件数
- 失败时详细记录文件路径、所在文件夹、文件名等信息
- 日志文件保存在 logs 目录下，文件名包含当前时间戳

## 技术要求

### 1. 使用技术

- Python 3.12 或更高版本
- Pydantic 用于数据验证和解析
- SQLite 用于数据库查询
- 标准库组件：
  - pathlib 处理文件路径
  - logging 记录日志
  - csv 输出 CSV 文件
  - json 处理 JSON 数据

### 2. 架构设计

程序使用面向对象设计，主要包含：

- `LaptopInfersProcessor` 类：处理核心逻辑
- 辅助函数：`extract_laptop_name` 和 `get_db_info`
- 入口点：main.py

### 3. 错误处理机制

- 详细记录处理过程中的错误
- 捕获并处理所有可能的异常
- 错误信息包含文件路径、错误类型等关键信息
- 错误不会导致整个程序中断，而是跳过问题文件继续处理

## 详细实现指南

### 1. 文件结构

```
c:\work\py_uv_laptop_infers\
|-- main.py                    # 程序入口
|-- process_laptop_infers.py   # 核心处理逻辑
|-- schema.py                  # 数据结构定义
|-- README.md                  # 用户说明文档
|-- README_prompt.md           # 开发指南文档
|-- test_02.db                 # SQLite 数据库
|-- requirements.txt           # 依赖列表
|-- logs/                      # 日志目录
```

### 2. 类与函数设计

#### LaptopInfersProcessor 类

```python
class LaptopInfersProcessor:
    def __init__(self, input_folder: str, output_csv: str, db_path: str):
        # 初始化处理器，设置输入输出路径和数据库路径
        # 配置日志记录器

    def find_json_files(self) -> List[Tuple[Path, str, str]]:
        # 遍历目录查找 laptop_infers.json 文件以及对应的 qc_result 和 inference 文件

    def read_inference_file(self, folder_path: Path, filename: str) -> List[str]:
        # 读取 inference 文件并提取 mask_miss 信息

    def read_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        # 读取并解析 JSON 文件

    def parse_json_data(self, json_data: Dict[str, Any]) -> Optional[InferenceOutput]:
        # 解析 JSON 数据，处理缺失字段

    def find_matching_box_info(self, labels: Dict[str, Labels], target_score: float) -> Optional[tuple]:
        # 在 labels 中查找与目标分数匹配的瑕疵点信息

    def process_json_data(self, json_data: Dict[str, Any], qc_result_file: str, mask_miss_areas: List[str]) -> List[Dict[str, Any]]:
        # 处理 JSON 数据，提取所需信息，并添加数据库查询结果

    def write_to_csv(self, all_results: List[Dict[str, Any]]):
        # 将结果写入 CSV 文件，同时生成 JSON 输出

    def process(self):
        # 执行完整的处理流程，遍历文件、提取数据、生成报告
```

#### 辅助函数

```python
def extract_laptop_name(laptop_key: str) -> str:
    # 从 laptop_key 中提取第四个下划线之前的文本

def get_db_info(laptop_name: str, db_path: str) -> Tuple[str, str, str]:
    # 从数据库中查询 laptop_name 相关信息
```

### 3. 数据库结构

数据库包含两个主要表：

- `laptops` 表：存储笔记本电脑基本信息
  - `id`: 主键
  - `laptop_name`: 笔记本电脑名称
  - `created_at`: 创建时间

- `laptop_defect_predictions` 表：存储预测结果
  - `laptop_id`: 外键，关联 laptops 表的 id
  - `pred`: 预测结果
  - `pred_score`: 预测分数
  - `gt`: 真实标签

查询示例：
```sql
SELECT
    p.pred,
    p.pred_score,
    p.gt
FROM
    laptops l
LEFT JOIN
    laptop_defect_predictions p ON l.id = p.laptop_id
WHERE
    l.laptop_name = ? AND
    l.created_at >= '2025-02-20'
ORDER BY
    l.created_at DESC
LIMIT 1
```

## 使用说明

### 1. 环境设置

确保已安装 Python 3.12 或更高版本，然后安装所需依赖：

```bash
pip install -r requirements.txt
# 或使用 uv
uv pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

程序将：
1. 在当前目录及其子目录中查找所有 laptop_infers.json 文件
2. 处理每个文件，提取所需信息
3. 生成 CSV 和 JSON 输出文件
4. 记录详细的处理日志

### 3. 输出文件

- **CSV 文件**: `laptop_infers_results.csv`
- **JSON 文件**: `laptop_infers_results.json`
- **日志文件**: `logs/laptop_infers_processor_YYYYMMDD_HHMMSS.log`

## 特别说明

### 1. 处理性能

- 程序设计为处理大量文件，优化了文件遍历和处理逻辑
- 对于大型目录结构，处理可能需要一定时间

### 2. 异常处理

- 程序不会因单个文件处理失败而中断
- 所有错误都会详细记录在日志中
- 处理结束时会显示成功和失败的文件数量统计

### 3. 数据库兼容性

- 确保数据库结构符合设计要求
- 数据库查询使用参数化查询，防止 SQL 注入
- 程序会处理数据库不存在、表结构不匹配等异常情况

### 4. 日期处理

- 数据库查询中使用 `2025-02-20` 格式的日期
- 日志记录使用本地时间和 UTC 时间
- 确保时间格式一致性

## 未来扩展

### 1. 潜在改进

- 添加命令行参数支持，允许指定输入目录和输出文件
- 实现并行处理，加速大量文件的处理
- 添加进度条显示处理进度
- 实现Web界面，方便用户操作

### 2. 集成建议

- 可与自动化测试系统集成
- 可扩展为 API 服务，提供远程调用能力
- 可添加数据可视化功能，生成报表和图表