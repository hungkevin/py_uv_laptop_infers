import sqlite3
import csv
import os
import logging
import sys
from datetime import datetime
from database import DB_ROOT

# 设置控制台编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.7或更早版本
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 创建自定义StreamHandler使用UTF-8编码
class Utf8StreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__(sys.stdout)
        self.encoding = 'utf-8'

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("analyze_gt.log", encoding='utf-8'),
        Utf8StreamHandler()
    ]
)
logger = logging.getLogger("analyze_gt")

def analyze_gt():
    """
    从test.db提取数据，筛选2025/3/20及之后创建的笔记本电脑记录，
    并获取相应的预测结果，保存到analyze_gt.csv
    """
    logger.info("Start analyzing GT data")

    try:
        # 连接到数据库
        db_path = os.path.join(DB_ROOT, "test_02.db")
        logger.debug(f"Connecting to database: {db_path}")

        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return 0

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使用字典形式返回结果
        cursor = conn.cursor()
        logger.debug("Database connection successful")

        # 确定日期过滤条件（2025年3月20日）
        filter_date = "2025-03-20 00:00:00"
        logger.info(f"Using date filter: {filter_date}")

        # 查询符合条件的笔记本电脑及其预测数据
        query = """
        SELECT
            l.id AS laptop_id,
            l.laptop_name,
            p.pred,
            p.pred_score,
            p.gt,
            l.created_at
        FROM
            laptops l
        LEFT JOIN
            laptop_defect_predictions p ON l.id = p.laptop_id
        WHERE
            l.created_at >= ?
        ORDER BY
            l.created_at
        """

        logger.debug(f"Executing SQL query")
        cursor.execute(query, (filter_date,))
        results = cursor.fetchall()
        logger.info(f"Found {len(results)} matching records")

        # 将结果保存到CSV文件
        csv_path = "analyze_gt.csv"
        logger.debug(f"Preparing to write CSV file: {csv_path}")

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['laptop_id', 'laptop_name', 'pred', 'pred_score', 'gt', 'created_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            logger.debug(f"CSV headers written: {', '.join(fieldnames)}")

            for i, row in enumerate(results):
                # 将结果转换为字典并写入CSV
                row_dict = dict(row)

                # 转换布尔值为数值形式 (1/0)
                if row_dict['pred'] is not None:
                    # 保持原始布尔值的数值形式 (1/0)
                    row_dict['pred'] = 1 if row_dict['pred'] == 1 else 0
                if row_dict['gt'] is not None:
                    # 保持原始布尔值的数值形式 (1/0)
                    row_dict['gt'] = 1 if row_dict['gt'] == 1 else 0

                writer.writerow(row_dict)

                # 记录进度，每100条记录输出一次
                if i > 0 and i % 100 == 0:
                    logger.debug(f"Processed {i}/{len(results)} records")

        logger.info(f"Data successfully written to CSV file: {csv_path}")
        conn.close()
        logger.debug("Database connection closed")

        return len(results)

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        return 0
    except IOError as e:
        logger.error(f"File IO error: {str(e)}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 0

if __name__ == "__main__":
    logger.info("Starting analyze_gt script")
    try:
        count = analyze_gt()
        logger.info(f"Data extraction completed, {count} records processed.")
        print(f"Data extraction completed, {count} records processed.")
    except Exception as e:
        logger.critical(f"Program execution failed: {str(e)}")
        print(f"Program execution error, see log file for details.")