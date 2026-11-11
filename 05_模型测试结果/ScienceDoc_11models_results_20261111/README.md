# ScienceDoc 11 模型评测结果（人类专家一致性标注用）

打包日期：2026-11-11。来源仓库：`/data/czj/SciDoc`。
评分口径：`sxz_v4`（与论文 Table 2/3 一致的历史缓存回放，无新 Judge 调用，
`data/results/identifier_migration_v4_replay/`，2026-09-21 生成）。

## 模型（11 个）

MiniCPM-V-2.6, InternVL25-8B, MiniCPM-V-4.5, InternVL35-8B, Gemma3-27B-IT,
Mistral-Small3.1-24B, Qwen3-VL-4B, Qwen3-VL-8B, Claude-sonncet-5（目录名保留原拼写）,
DeepSeek-V4-flash-Vision-Exp, GLM-4.6V。

## 目录

| 路径 | 内容 |
| --- | --- |
| `human_agreement_all_models.csv` | **标注主表**：11 模型 × 每题一行（共 24,148 行），精简字段 + 空白 `human_verdict` / `human_note` 两列供专家填写 |
| `per_model_details/<模型>/details.csv` | 每个模型的完整逐题评分明细（含 gold 元数据、解析状态、Judge 原始输出、证据页 P/R/F1 等全部字段） |
| `per_model_details/<模型>/summary.csv` | 该模型 7 行汇总 |
| `raw_model_outputs/<模型>/*.json` | 模型原始推理输出（5 个组件：ordinary1190、cross_old400、cross_hard400、reasoning_old100、reasoning_hard100） |
| `summary/summary.csv` | v4 回放 77 行汇总（11 模型 × 7 行） |
| `summary/summary_11models_77rows_calibrated_fixed_denominator.csv` | 参考 77 行汇总；与上面的回放结果数值一致 |
| `summary/report.json`, `paper_comparison.csv`, `run_binding.json` | 论文 Table 2/3 数值、与论文对照、输入文件哈希绑定 |
| `summary/detail_11models_5datasets.xlsx` | 按 5 个组件分 sheet 的明细工作簿 |
| `qa_id_mapping_final_2200.csv` | 实验旧编号（`legacy_document_id` + `legacy_qa_id`）↔ 当前正式编号（`gen_/md_/rea_/una_`）及 PDF 路径 |
| `SHA256SUMS` | 包内所有文件校验值 |

所有 CSV 均为 UTF-8 BOM 编码，可直接用 Excel 打开。

## 主表关键字段

- `in_current_release` / `current_qa_id` / `current_document_id` / `current_pdf_path`：
  对应当前正式 2,200 题的编号；PDF 为 `data/pdfs/<current_document_id>.pdf`（Google Drive 资源包中的文件名）。
- `item_uid`：实验时的原始身份（`组件::文档::QA`），跨模型对齐请用它。
- `answerable`：1 可回答 / 0 不可回答（不可回答题的正确答案是精确的 `Unanswerable`）。
- `question`, `gold_answer`, `gold_evidence_pages`：题目、标准答案、标准证据页（PDF 物理页，从 1 开始）。
- `pred_answer`, `pred_evidence_pages`：模型答案与模型给出的证据页。
- `answer_verdict`：LLM Judge 判定：`correct` / `partial` / `wrong` / `technical_failure`
  （`technical_failure` 指推理失败或输出无法解析，未调用 Judge，计分按错）。
  正确率只计 `correct`；`partial` 不得分。
- `judge_raw`：Judge 原始输出。
- `E_Precision`, `E_Recall`, `E_F1`：证据页指标。
- `human_verdict`, `human_note`：留空，供专家填写（建议使用与 `answer_verdict` 相同的四个取值）。

## 注意事项

1. **行数差异**：组件题量固定为 1,200 + 400 + 400 + 100 + 100 = 2,200，各模型为 2,190–2,200 行：
   - Claude-sonncet-5、InternVL35-8B、Qwen3-VL-4B、Qwen3-VL-8B 的普通组件只有 1,190 行（缺 10 道不可回答题）；
   - DeepSeek、GLM、Gemma3、InternVL25、MiniCPM-V-2.6、Mistral 的 cross_old400 只有 398 行；
   - MiniCPM-V-4.5 完整 2,200 行。
   缺失的题在计分时按固定分母记为错，但没有模型输出可供标注。
2. **不在当前正式集中的题**：30 行（Claude 普通组件 28 题 + 多个模型 cross_old400 中的
   `xb_0003::QA8`、`xb_0043::QA8`）是历史实验时的题目，后来被替换，当前正式 2,200 题中已无对应。
   这些行 `in_current_release=False`，当前编号为空，但模型答案与 Judge 判定仍然有效。
   如果只想标注当前正式集，请筛选 `in_current_release=True`。
3. 原始输出 JSON 内的 PDF 路径为当时服务器路径（如 `/data/czj/pku/data/pdfs/papers/1.pdf`），
   请以 `current_pdf_path` 为准定位 PDF。
