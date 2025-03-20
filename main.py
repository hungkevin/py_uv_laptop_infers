from pathlib import Path
from process_laptop_infers import LaptopInfersProcessor

def main():
    current_dir = Path.cwd()
    input_folder = str(current_dir)
    output_csv = str(current_dir / "laptop_infers_results.csv")

    try:
        processor = LaptopInfersProcessor(input_folder, output_csv)
        processor.process()
    except Exception as e:
        print(f"程序执行时发生错误: {str(e)}")

if __name__ == "__main__":
    main()
