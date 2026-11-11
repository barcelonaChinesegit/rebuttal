"""从 11 个模型的测试结果中抽取 2,000 条，生成两位专家的盲标 Excel 表
（回应 FC8s W2 / HFLj W1：LLM Judge 与人类专家的一致性）。

抽样池：结果包 human_agreement_all_models.csv 中满足以下条件的行
  * 属于当前正式 2,200 题（in_current_release == True）；
  * 实际调用过 Judge（answer_verdict 为 correct / partial / wrong；
    technical_failure 没有调用 Judge，也没有可标注的内容）。
抽样方式：按 模型 × 任务 × 学科 分层，按比例随机抽取，使样本与全部判定结果同分布。

用法：
  python3 judge_audit_sample.py <human_agreement_all_models.csv> <输出目录> [--n 2000] [--seed 2027]
输出（输出目录下）：
  判定答案键_勿外发.csv   编号 -> 模型名、题号、任务、学科、Judge 判定（只留给自己，不要发给标注同学）
  专家A标注表.xlsx        盲标表（无模型名、无 Judge 判定），题目顺序随机
  专家B标注表.xlsx        与 A 相同的 2,000 条，但顺序不同
  抽样分布核对.md         抽样与总体在模型 / 任务 / 学科 / Judge 判定上的分布对比
需要 openpyxl（pip3 install --user openpyxl）。
"""
import csv
import os
import random
import sys
from collections import Counter, defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

# Judge 原始取值 -> 中文标签（只有“正确”计分）
JUDGE_LABEL = {"correct": "正确", "partial": "部分正确", "wrong": "错误"}
DISCIPLINE = {
    "Computer Science": "计算机科学", "Physics": "物理", "Statistics": "统计",
    "Mathematics": "数学", "Electrical Engineering and Systems Science": "电子工程与系统科学",
    "Economics": "经济", "Quantitative Biology": "定量生物", "Quantitative Finance": "定量金融",
    "": "未标学科",
}

RULES = [
    ("怎么标", "对每一行，比较“模型答案”和“参考答案”在这道题要求的内容上是否语义一致，"
              "在“标注”列的下拉框里选一个值。只看题目、参考答案、模型答案三列即可，不需要打开 PDF。"),
    ("正确", "题目要求的事实、数值、单位、条件、比较方向全部正确。表述不同但含义相同也算正确"
            "（如 0.5 与 50%、\\alpha 与 α、同义改写）；答案简短但已经充分，也算正确。"),
    ("部分正确", "答对了题目要求的一部分，但缺少某个要求的组成部分（例如问两个数值只答对一个），且没有实质性错误。"),
    ("错误", "数值、符号、单位、方向错误；与参考答案实质矛盾；答非所问；答案为空。"),
    ("不可回答题", "任务为“不可回答题”时参考答案是 Unanswerable：模型明确表示无法根据文档回答才算正确，"
                 "给出任何具体答案都算错误。"),
    ("附带细节", "参考答案里有、但题目没有要求的附带细节，模型没写不扣分。"),
    ("拿不准时", "在“备注”列写原因，但“标注”列必须三选一，不能留空。"),
    ("独立标注", "两位同学各自独立完成，标注期间不要互相讨论，也不要查看任何模型或 Judge 的结果。"),
]


def task_of(r):
    d = r["dataset"]
    if d.startswith("cross"):
        return "多文档题"
    if d.startswith("reasoning"):
        return "推理题"
    return "不可回答题" if r["answerable"] == "0" else "普通题"


def allocate(strata, n):
    """按比例分配各层抽样数（最大余数法）。"""
    total = sum(len(v) for v in strata.values())
    quota = {k: n * len(v) / total for k, v in strata.items()}
    alloc = {k: int(q) for k, q in quota.items()}
    for k in sorted(quota, key=lambda k: quota[k] - alloc[k], reverse=True)[: n - sum(alloc.values())]:
        alloc[k] += 1
    return alloc


CTRL = {"\x07": "\\a", "\x08": "\\b", "\x0b": "\\v", "\x0c": "\\f"}


def clean(text):
    """Excel 不允许的控制字符改成可见的转义写法（例如 \\alpha 被存成响铃符 + lpha 时还原为 \\alpha）。"""
    out = []
    for ch in str(text or ""):
        if ord(ch) < 32 and ch not in "\t\n\r":
            out.append(CTRL.get(ch, "\\x%02x" % ord(ch)))
        else:
            out.append(ch)
    return "".join(out)


def write_sheet(path, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "标注"
    head = ["编号", "任务", "学科", "题目", "参考答案", "模型答案", "标注", "备注"]
    ws.append(head)
    for r in rows:
        ws.append([r["编号"], r["任务"], r["学科"], clean(r["question"]), clean(r["gold_answer"]),
                   clean(r["pred_answer"]), "", ""])
    widths = [9, 11, 14, 60, 40, 60, 12, 30]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DDEBF7")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws["G"][1:]:
        c.fill = PatternFill("solid", fgColor="FFF2CC")
    dv = DataValidation(type="list", formula1='"正确,部分正确,错误"', allow_blank=True,
                        showErrorMessage=True, errorTitle="取值错误", error="请从下拉框选择：正确 / 部分正确 / 错误")
    ws.add_data_validation(dv)
    dv.add(f"G2:G{len(rows) + 1}")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:H{len(rows) + 1}"
    info = wb.create_sheet("标注说明")
    info.column_dimensions["A"].width = 14
    info.column_dimensions["B"].width = 110
    info.append(["项目", "说明"])
    for c in info[1]:
        c.font = Font(bold=True)
    for k, v in RULES:
        info.append([k, v])
    for row in info.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)


def dist(rows, key):
    c = Counter(r[key] for r in rows)
    return {k: 100 * v / len(rows) for k, v in sorted(c.items())}


def main():
    args = sys.argv[1:]
    src, out_dir = args[0], args[1]
    n = int(args[args.index("--n") + 1]) if "--n" in args else 2000
    seed = int(args[args.index("--seed") + 1]) if "--seed" in args else 2027
    with open(src, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    pool = []
    for r in rows:
        if r["in_current_release"] != "True" or r["answer_verdict"] not in JUDGE_LABEL:
            continue
        pool.append({**r, "任务": task_of(r), "学科": DISCIPLINE[r["primary_category"]],
                     "Judge判定": JUDGE_LABEL[r["answer_verdict"]], "模型": r["model_name"]})
    strata = defaultdict(list)
    for r in pool:
        strata[(r["模型"], r["任务"], r["学科"])].append(r)
    alloc = allocate(strata, n)
    rng = random.Random(seed)
    sample = []
    for k in sorted(strata):
        sample += rng.sample(strata[k], alloc[k])
    rng.shuffle(sample)
    for i, r in enumerate(sample, 1):
        r["编号"] = f"A{i:04d}"

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "判定答案键_勿外发.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["编号", "模型", "实验题号", "正式题号", "数据组件", "任务", "学科", "Judge判定", "Judge原始输出"])
        for r in sample:
            w.writerow([r["编号"], r["模型"], r["item_uid"], r["current_qa_id"], r["dataset"],
                        r["任务"], r["学科"], r["Judge判定"], r["judge_raw"]])
    for name, s in (("专家A标注表.xlsx", seed + 1), ("专家B标注表.xlsx", seed + 2)):
        order = sample[:]
        random.Random(s).shuffle(order)
        write_sheet(os.path.join(out_dir, name), order)

    L = ["# 抽样分布核对", "",
         f"结果表总行数：{len(rows)}；当前正式集内、实际调用过 Judge 的判定（抽样池）：{len(pool)}；"
         f"抽样数：{len(sample)}；分层数：{len(strata)}；随机种子：{seed}。"]
    for key in ("模型", "任务", "学科", "Judge判定"):
        p, s = dist(pool, key), dist(sample, key)
        c = Counter(r[key] for r in sample)
        L += ["", f"## {key}", "", "| 取值 | 抽样池占比 (%) | 样本占比 (%) | 样本条数 |", "|---|---|---|---|"]
        L += [f"| {k} | {p[k]:.2f} | {s.get(k, 0):.2f} | {c.get(k, 0)} |" for k in p]
    with open(os.path.join(out_dir, "抽样分布核对.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
