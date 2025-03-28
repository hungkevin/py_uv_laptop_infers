from pathlib import Path
from process_laptop_infers import LaptopInfersProcessor

def main():
    """
    主函数 - 程序的入口点

    功能:
    1. 获取当前工作目录作为输入文件夹
    2. 配置输出CSV文件路径
    3. 配置数据库路径
    4. 初始化并运行笔记本电脑推理数据处理器
    """
    # 获取当前工作目录作为输入文件夹
    current_dir = Path.cwd()

    # 定义输出CSV文件路径，将在当前目录下生成
    output_csv = str(current_dir / "laptop_infers_results.csv")

    # 定义数据库文件路径
    ##db_path = str(current_dir / "test_02.db")
    db_path = str(current_dir / "test_03.db")

    try:
        # 初始化处理器，传入输入文件夹路径、输出CSV文件路径和数据库路径
        processor = LaptopInfersProcessor(
            input_folder=str(current_dir),
            output_csv=output_csv,
            db_path=db_path
        )

        # 执行处理流程
        # 这将遍历所有子目录，查找并处理laptop_infers.json文件
        # 提取相关信息并生成CSV和JSON输出文件
        processor.process()
    except Exception as e:
        # 捕获并打印任何异常，确保程序不会崩溃而没有提示
        print(f"程序执行时发生错误: {str(e)}")

# 当直接运行此脚本时执行main()函数
if __name__ == "__main__":
    main()
