# 提示詞

請幫我生成一個 Python 程式來處理多個包含 `laptop_infers.json` 文件的目錄。具體要求如下：

1. **程式描述**：
   - 我需要一個 Python 程式來處理多個包含 `laptop_infers.json` 文件的目錄。
   - 每個目錄中可能還包含以 `qc_result_` 開頭的文件和以 `inference_` 開頭的文件。
   - 程式需要遍歷指定目錄中的所有子目錄，找到 `laptop_infers.json` 文件以及對應的 `qc_result_` 文件和 `inference_` 文件。
   - 將提取的信息寫入到 CSV 和 JSON 文件中。
   - 程式需要詳細記錄處理過程中的成功和失敗信息。

2. **功能要求**：
   - **遍歷文件夾**：遍歷主文件夾中的所有子目錄，找到 `laptop_infers.json` 文件和對應的 `qc_result_` 文件和 `inference_` 文件。
   - **讀取 JSON 文件**：讀取並解析 `laptop_infers.json` 文件，處理可能的缺失字段。
   - **檢查瑕疵信息**：檢查 JSON 文件中的 `labels` 信息。如果 `labels` 為空，則記錄 `None`。
   - **檢查 mask_miss 信息**：
     - 讀取對應的 `inference_` 文件，若找到 `Transformation not possible` 文字, 提取該文字之前, 從`] `到`: `的字串。
     - 若未找到 `Transformation not possible` 文字, 則記錄 `none`。
     - 若未找到 `inference_` 文件, 則記錄 `no_log`。
     - 若讀取文件出錯, 則記錄 `error`。
   - **記錄結果**：將提取的信息記錄到 CSV 和 JSON 文件中，包含以下字段：`laptop_key`、`defect`、`score`、`area_name`、`boxes`、`matched_score`、`timestamp`、`qc_result_file` 和 `mask_miss`。
   - **記錄錯誤**：在處理文件時，如果發生錯誤，需要記錄詳細的錯誤信息，包括文件路徑、文件夾名稱、QC 文件名稱、Inference 文件名稱和錯誤原因。

3. **日誌要求**：
   - 程式開始和結束時需要記錄時間和用戶信息。
   - 每次處理文件時需要記錄成功或失敗的詳細信息。
   - 如果發生錯誤，詳細記錄錯誤信息。

4. **使用以下時間和用戶信息**：
   - 當前時間 (UTC - YYYY-MM-DD HH:MM:SS 格式)：2025-03-20 02:44:05
   - 當前用戶登錄名：hmjack2008

5. **Mask Miss 示例**：
   - 例如以下字串：`[INFO][2025-02-23 09:47:39][inference_v2][LASA_02_BDCTO100DCS2M0AAAK_20250223094734_20250223-094736-488896] Front_04: Transformation not possible`
   - 應提取 `Front_04` 字串並記錄到 mask_miss 中

6. **輸出格式要求**：
   - CSV 文件：保存所有記錄，其中 mask_miss 以字符串形式存儲（用逗號分隔多個區域名稱）
   - JSON 文件：保存完整的數據結構，其中 mask_miss 保持為列表格式

7. **生成以下文件**：
   - `process_laptop_infers.py` - 核心處理邏輯
   - `main.py` - 程序入口
   - `requirements.txt` - 依賴包列表
   - `README.md` - 使用說明
```