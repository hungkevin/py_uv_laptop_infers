import os
import json
import csv
import re
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from schema import InferenceOutput, LaptopInfers, ModelParams, Labels

# 设置数据库路径
##DB_Path = "./test_02.db"  # 可以根据需要修改为实际的数据库路径

def extract_laptop_name(laptop_key: str) -> str:
    """
    从laptop_key中提取最后一个下划线之前的文本作为laptop_name

    Args:
        laptop_key (str): 完整的laptop_key字符串

    Returns:
        str: 提取出的laptop_name
    """
    last_underscore_pos = laptop_key.rfind('_')
    if last_underscore_pos != -1:
        return laptop_key[:last_underscore_pos]
    return laptop_key  # 如果没有下划线，返回原始字符串

def get_db_info(laptop_name: str, db_path: str) -> Tuple[str, str, str]:
    """
    从数据库中查询laptop_name相关信息

    Args:
        laptop_name (str): 要查询的laptop_name

    Returns:
        Tuple[str, str, str]: 返回 (db_pred, db_pred_score, db_gt)
                             如果数据库不存在，返回 ("no-db", "no-db", "no-db")
                             如果没有找到记录，返回 ("no-sn", "no-sn", "no-sn")
                             如果查询出错，返回 ("error", "error", "error")
    """
    DB_Path = db_path
    if not os.path.exists(DB_Path):
        return "no-db", "no-db", "no-db"

    try:
        conn = sqlite3.connect(DB_Path)
        cursor = conn.cursor()

        # 修正查询语句，确保字段名与analyze_gt.py中一致
        query = """
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
        """

        cursor.execute(query, (laptop_name,))
        record = cursor.fetchone()
        conn.close()

        if record:
            # 确保变量名与字段名一致
            pred, pred_score, gt = record
            return str(pred), str(pred_score), str(gt)
        else:
            return "no-sn", "no-sn", "no-sn"
    except Exception as e:
        logging.error(f"查询数据库时出错: {str(e)}")
        return "error", "error", "error"

class LaptopInfersProcessor:
    def __init__(self, input_folder: str, output_csv: str, db_path: str):
        """
        初始化处理器

        Args:
            input_folder (str): 要搜索的主文件夹路径
            output_csv (str): 输出CSV文件的路径
        """
        self.input_folder = Path(input_folder)
        self.output_csv = Path(output_csv)
        self.db_path = Path(db_path)

        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 使用当前时间创建日志文件名
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"laptop_infers_processor_{current_time}.log"

        # 设置日志配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"开始处理，输入目录: {input_folder}")
        self.logger.info(f"输出文件: {output_csv}")

    def find_json_files(self) -> List[Tuple[Path, str, str]]:
        """
        遍历文件夹寻找 laptop_infers.json 文件和对应的 qc_result 文件以及 inference_ 文件

        Returns:
            List[Tuple[Path, str, str]]: 找到的文件对列表，每个元组包含一个 laptop_infers.json 文件、
                                        对应的 qc_result 文件名和 inference_ 文件名
        """
        file_tuples = []
        try:
            for root, _, files in os.walk(self.input_folder):
                root_path = Path(root)
                if "laptop_infers.json" in files:
                    laptop_infers_file = root_path / "laptop_infers.json"
                    # 寻找 qc_result_ 开头的文件
                    qc_files = [f for f in files if f.startswith("qc_result_")]
                    qc_result_file = qc_files[0] if qc_files else ""

                    # 寻找 inference_ 开头的文件
                    inference_files = [f for f in files if f.startswith("inference_")]
                    inference_file = inference_files[0] if inference_files else ""

                    file_tuples.append((laptop_infers_file, qc_result_file, inference_file))

            self.logger.info(f"找到 {len(file_tuples)} 个 laptop_infers.json 文件")
        except Exception as e:
            self.logger.error(f"遍历文件夹时发生错误: {str(e)}")
        return file_tuples

    def read_inference_file(self, folder_path: Path, filename: str) -> List[str]:
        """
        读取并解析 inference_ 文件，提取 mask_miss 信息

        Args:
            folder_path (Path): 文件夹路径
            filename (str): inference_文件名

        Returns:
            List[str]: 提取的mask_miss区域名称列表
        """
        if not filename:
            return ["no_log"]

        file_path = folder_path / filename
        try:
            mask_miss_areas = []
            pattern = r'\]\s([^:]+): Transformation not possible'

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            matches = re.findall(pattern, content)
            if matches:
                mask_miss_areas.extend(matches)

            return mask_miss_areas if mask_miss_areas else ["none"]

        except Exception as e:
            self.logger.error(f"读取inference文件 {file_path} 时发生错误: {str(e)}")
            return ["error"]

    def read_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        读取并解析 JSON 文件

        Args:
            file_path (Path): JSON 文件的路径

        Returns:
            Optional[Dict[str, Any]]: 解析后的 JSON 数据，如果发生错误返回 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"读取文件 {file_path} 时发生错误: {str(e)}")
            return None

    def parse_json_data(self, json_data: Dict[str, Any]) -> Optional[InferenceOutput]:
        """
        解析并验证 JSON 数据，处理可能的缺失字段

        Args:
            json_data (Dict[str, Any]): JSON 数据

        Returns:
            Optional[InferenceOutput]: 解析后的数据结构，如果发生错误返回 None
        """
        try:
            # 预处理 JSON 数据，补充缺失的必需字段
            for infer in json_data.get('laptop_infers', []):
                if 'params' in infer:
                    params = infer['params']
                    # 添加默认值
                    params.setdefault('score_thr', 0.0)
                    params.setdefault('box_size_thr', 1000)
                    params.setdefault('model_key', params.get('model_version', 'unknown'))
                    params.setdefault('mask_key', params.get('model_version', 'unknown'))
            return InferenceOutput(**json_data)
        except Exception as e:
            self.logger.error(f"解析JSON数据时发生错误: {str(e)}")
            return None

    def find_matching_box_info(self, labels: Dict[str, Labels], target_score: float) -> Optional[tuple]:
        """
        在 labels 中找出与目标分数匹配的瑕疵点信息

        Args:
            labels (Dict[str, Labels]): 标签数据
            target_score (float): 目标分数

        Returns:
            Optional[tuple]: 找到的瑕疵点信息 (area_name, boxes, score)，如果未找到返回 None
        """
        try:
            for area_name, label_data in labels.items():
                scores = label_data.scores
                boxes = label_data.boxes
                for i, score in enumerate(scores):
                    if abs(score - target_score) < 1e-6:
                        return (area_name, boxes[i], score)
        except Exception as e:
            self.logger.error(f"处理标签数据时发生错误: {str(e)}")
        return None

    def process_json_data(self, json_data: Dict[str, Any], qc_result_file: str, mask_miss_areas: List[str]) -> List[Dict[str, Any]]:
        """
        处理 JSON 数据，提取所需信息

        Args:
            json_data (Dict[str, Any]): JSON 数据
            qc_result_file (str): 对应的 QC 文件名
            mask_miss_areas (List[str]): 从inference文件中提取的mask_miss区域列表

        Returns:
            List[Dict[str, Any]]: 提取的信息列表
        """
        results = []
        try:
            inference_output = self.parse_json_data(json_data)
            if not inference_output:
                return results

            laptop_key = inference_output.laptop_key
            laptop_name = extract_laptop_name(laptop_key)

            # 获取数据库信息
            db_pred, db_pred_score, db_gt = get_db_info(laptop_name, self.db_path)

            for infer in inference_output.laptop_infers:
                if infer.results:
                    defect = infer.results.defect
                    score = infer.results.score

                    # 检查是否有 labels（是否检测到瑕疵）
                    if infer.results.labels and len(infer.results.labels) > 0:
                        box_info = self.find_matching_box_info(infer.results.labels, score)
                        if box_info:
                            area_name, boxes, matched_score = box_info
                        else:
                            area_name, boxes, matched_score = None, None, None
                    else:
                        # 如果没有检测到瑕疵，设置为 None
                        area_name, boxes, matched_score = None, None, None

                    # 添加数据库信息到结果中
                    results.append({
                        'laptop_key': laptop_key,
                        'defect': defect,
                        'score': score,
                        'area_name': area_name,
                        'boxes': str(boxes) if boxes is not None else None,
                        'matched_score': matched_score,
                        'timestamp': infer.timestamp,
                        'qc_result_file': qc_result_file,
                        'mask_miss': mask_miss_areas,  # 直接使用列表
                        'laptop_name': laptop_name,
                        'db_pred': db_pred,
                        'db_pred_score': db_pred_score,
                        'db_gt': db_gt
                    })

        except Exception as e:
            self.logger.error(f"处理JSON数据时发生错误: {str(e)}")

        return results

    def write_to_csv(self, all_results: List[Dict[str, Any]]):
        """
        将结果写入 CSV 文件，使用字符串格式存储mask_miss字段

        Args:
            all_results (List[Dict[str, Any]]): 提取的所有信息
        """
        if not all_results:
            self.logger.warning("没有数据要写入CSV")
            return

        try:
            # 将结果保存为JSON文件，这样可以保留列表格式
            json_file = self.output_csv.with_suffix('.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功将数据写入 {json_file}")

            # 准备CSV数据，将mask_miss转换为字符串
            csv_results = []
            for result in all_results:
                csv_result = result.copy()
                if isinstance(csv_result['mask_miss'], list):
                    csv_result['mask_miss'] = ', '.join(csv_result['mask_miss'])
                csv_results.append(csv_result)

            # 定义CSV字段，添加新字段
            fieldnames = [
                'laptop_key', 'defect', 'score',
                'area_name', 'boxes', 'matched_score',
                'timestamp', 'qc_result_file', 'mask_miss',
                'laptop_name', 'db_pred', 'db_pred_score', 'db_gt'
            ]

            # 使用标准CSV写入器
            with open(self.output_csv, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_results)

            self.logger.info(f"成功将数据写入 {self.output_csv}")
            self.logger.info(f"总共处理了 {len(all_results)} 条记录")
        except Exception as e:
            self.logger.error(f"写入文件时发生错误: {str(e)}")

    def process(self):
        """
        执行完整的处理流程
        """
        file_tuples = self.find_json_files()
        all_results = []
        processed_files = 0
        error_files = 0

        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"程序开始时间: 2025-03-20 02:44:05 UTC")
        self.logger.info(f"程序执行用户: hmjack2008")
        self.logger.info(f"{'='*50}\n")

        for json_file, qc_result_file, inference_file in file_tuples:
            self.logger.info(f"处理文件: {json_file}")

            # 读取 inference_ 文件提取 mask_miss 信息
            mask_miss_areas = self.read_inference_file(json_file.parent, inference_file)
            self.logger.info(f"从 {inference_file if inference_file else '(未找到inference文件)'} 中提取的mask_miss区域: {mask_miss_areas}")

            json_data = self.read_json_file(json_file)
            if json_data:
                results = self.process_json_data(json_data, qc_result_file, mask_miss_areas)
                if results:
                    all_results.extend(results)
                    processed_files += 1
                else:
                    error_files += 1
                    self.logger.error(f"""
==================== 处理失败 #{error_files} ====================
文件路径: {json_file}
所在文件夹: {json_file.parent}
文件夹名称: {json_file.parent.name}
QC文件: {qc_result_file if qc_result_file else '未找到'}
Inference文件: {inference_file if inference_file else '未找到'}
失败原因: 数据处理失败 - 无法从JSON数据中提取有效信息
=======================================================
""")
            else:
                error_files += 1
                self.logger.error(f"""
==================== 处理失败 #{error_files} ====================
文件路径: {json_file}
所在文件夹: {json_file.parent}
文件夹名称: {json_file.parent.name}
QC文件: {qc_result_file if qc_result_file else '未找到'}
Inference文件: {inference_file if inference_file else '未找到'}
失败原因: 文件读取失败 - 无法读取或解析JSON文件
=======================================================
""")

        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"处理完成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        self.logger.info(f"处理结果摘要:")
        self.logger.info(f"- 成功处理: {processed_files} 个文件")
        self.logger.info(f"- 处理失败: {error_files} 个文件")
        if error_files > 0:
            self.logger.info(f"- 详细的失败记录请查看上方日志")
        self.logger.info(f"{'='*50}\n")

        self.write_to_csv(all_results)
