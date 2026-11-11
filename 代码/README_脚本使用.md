# 脚本使用说明

所有命令在 `rebuttal/` 根目录执行。日常使用已有结果即可，不需要依次运行全部脚本。这里列出的文件均为当前可用脚本；一次性修改旧稿的脚本已清理。

## 脚本对应关系

| 脚本 | 输入/作用 | 输出与注意事项 |
|---|---|---|
| `verify_structured.py` | 检查200篇元数据、配额、重复项及文件存在情况 | 重写200篇总表 `manifest.csv`，不下载 |
| `fetch_arxiv_latex.py` | 按学科/领域配额联网下载arXiv论文并结构化 | 写入指定目录；200篇现已齐全，无需常规重跑 |
| `discipline_stats.py` | 从脚本内记录的Table 3数值和学科题数重算统计 | 写入指定输出目录，包含Wilson区间、原始检验及Holm校正；不自动读取新的模型实验 |
| `judge_audit_sample.py` | 从11模型有效判定中按比例分层抽样 | 生成答案键、两份空白盲标表、分布说明；同路径会覆盖文件，不要覆盖已有标注 |
| `judge_audit_analysis.py` | 读取答案键及两位专家真实标签，按编号连接 | 输出一致性MD/JSON；缺标或重复编号会停止；不生成专家标签 |
| `rebuttal_completion_audit.py` | 校验原抽样、读取真实标注进度、交叉核实领域元数据 | 更新真实Judge统计、61→52映射、2200题对照及200篇合并索引；不改原专家表 |
| `judge_simulation_preview.py` | 对现有Judge标签加模拟扰动并按预设ρ区间筛选 | 重写模拟CSV、MD和 `辅助文件/模拟统计.json`；只用于模拟预览 |
| `build_judge_preview.mjs` | 读取上述模拟JSON生成Excel及检查图 | 重写模拟Excel和辅助预览，不计算真实人工实验 |
| `test_judge_statistics.py` | 使用合成小样例验证统计函数 | 只报告测试通过/失败，不写入实验数据 |

## 运行环境

- 纯标准库脚本：下载、200篇检查、学科统计、统计函数测试。
- 读取XLSX及抽样：需要 `openpyxl`；当前本机的 `python3` 已可使用。
- 模拟生成：需要 `numpy`，本机已验证的解释器为 `/Users/chenzijian/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`。
- 模拟Excel生成：需要 `@oai/artifact-tool`，`代码/node_modules` 已链接到本机共享依赖。已验证的Node路径见下方命令。迁移到其他电脑时需要重新配置依赖链接；数据文件本身不依赖这个链接。

## 常用命令

首先进入工作目录：

```bash
cd /Users/chenzijian/Downloads/rebuttal
```

检查200篇、重算学科统计、刷新真实标注进度和分类映射：

```bash
python3 -B -I 代码/verify_structured.py 06_200篇结构化论文
python3 -B -I 代码/discipline_stats.py 02_学科统计
python3 -B 代码/rebuttal_completion_audit.py
```

真实标注收齐后计算一致性（当前空表会被拒绝）：

```bash
python3 -B 代码/judge_audit_analysis.py \
  03_Judge一致性标注/判定答案键_勿外发.csv \
  03_Judge一致性标注/专家A标注表.xlsx \
  03_Judge一致性标注/专家B标注表.xlsx \
  03_Judge一致性标注/一致性结果
```

检查统计函数：

```bash
python3 -B 代码/test_judge_statistics.py
```

只有需要重建模拟预览时才运行下面两条；会覆盖模拟结果：

```bash
/Users/chenzijian/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B 代码/judge_simulation_preview.py
/Users/chenzijian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node 代码/build_judge_preview.mjs
```

模拟生成脚本读取答案键，写入模拟JSON；Excel脚本再读取该JSON。单独重建Excel不会重新模拟标签。Excel中的主准确率、秩及二分类κ是公式，部分补充统计为固定快照；调整模拟数据后应重建，不能仅改几格就把所有补充结果视为已更新。

## 不要作为日常操作重跑的内容

- `judge_audit_sample.py` 会生成空白标注表。正式标注已开始后，不要向现有标注目录重跑；如需另做试验，应指定全新目录。
- `fetch_arxiv_latex.py` 是下载工具，不能代替文件完整性检查。
- `rebuttal_completion_audit.py` 会重写它生成的报告和映射表，且包含针对当前固定实验快照的校验。数据源或抽样方案改变后，应先检查脚本假设，而不是直接重跑覆盖手工修改。

当前脚本提供初步行级bootstrap区间；正式人工研究的聚类不确定性、专家资质和Judge运行配置仍需要补充。结果文件出现 `nan` / JSON `null` 表示指标无定义，不是完全一致。
