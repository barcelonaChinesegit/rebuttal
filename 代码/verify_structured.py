"""核对 200 篇结构化论文是否齐全，并根据每篇的 meta.json 重新生成总表 manifest.csv。

用法：python3 -I verify_structured.py <06_200篇结构化论文 目录>
检查内容：各学科 / 各 arXiv 分类是否达到配额、是否有重复论文、每篇的文件是否齐全。
"""
import csv
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_arxiv_latex import PLAN  # noqa: E402

DISC_CN = {"CS": "计算机科学", "PHY": "物理", "MATH": "数学", "STAT": "统计", "QBIO": "定量生物",
           "EESS": "电子工程与系统科学", "ECON": "经济", "QFIN": "定量金融"}
# manifest.csv 的列：(meta.json 中的字段, 中文列名)
COLUMNS = [("discipline", "学科"), ("field", "领域（论文图3）"), ("arxiv_category", "arXiv分类"),
           ("arxiv_id", "arXiv编号"), ("title", "论文标题"), ("published", "首次提交时间"),
           ("main_tex", "主tex文件"), ("n_sections", "章节数"), ("n_figures", "图数"),
           ("n_tables", "表数"), ("n_equations", "公式数"), ("n_chars", "正文字符数"),
           ("n_source_files", "源码文件数"), ("pdf_bytes", "PDF字节数"), ("source_type", "来源类型")]

root = os.path.abspath(sys.argv[1])
metas, problems = [], []
for disc in sorted(os.listdir(root)):
    ddir = os.path.join(root, disc)
    if not os.path.isdir(ddir):
        continue
    for pid in sorted(os.listdir(ddir)):
        pdir = os.path.join(ddir, pid)
        if not os.path.isdir(pdir):
            continue
        need = ["meta.json", "structured.json", "main_flat.tex", "paper.pdf", "source"]
        miss = [f for f in need if not os.path.exists(os.path.join(pdir, f))]
        if miss:
            problems.append(f"{disc}/{pid}：缺少 {miss}")
            continue
        metas.append(json.load(open(os.path.join(pdir, "meta.json"), encoding="utf-8")))

want_disc, want_cat = Counter(), {}
for disc, field, cat, q in PLAN:
    want_disc[disc] += q
    want_cat[cat] = q
got_disc = Counter(m["discipline"] for m in metas)
got_cat = Counter(m["arxiv_category"] for m in metas)
ids = Counter(m["arxiv_id"].split("v")[0] for m in metas)

print(f"已完成论文：{len(metas)} 篇（目标 {sum(want_disc.values())} 篇）")
for d in want_disc:
    print(f"  {DISC_CN[d]:10s} {got_disc[d]:3d}/{want_disc[d]}")
short = {c: f"{got_cat[c]}/{q}" for c, q in want_cat.items() if got_cat[c] != q}
print("未达配额的 arXiv 分类：", short or "无")
print("重复论文：", [i for i, c in ids.items() if c > 1] or "无")
print("文件不全的文件夹：", problems or "无")
tot = Counter()
for m in metas:
    for k in ("n_figures", "n_tables", "n_equations"):
        tot[k] += m[k]
print(f"合计：图 {tot['n_figures']} 个，表 {tot['n_tables']} 个，公式 {tot['n_equations']} 个；"
      f"覆盖领域 {len({m['field'] for m in metas})} 个")

order = {d: i for i, d in enumerate(want_disc)}
metas.sort(key=lambda m: (order.get(m["discipline"], 99), m["arxiv_category"], m["arxiv_id"]))
with open(os.path.join(root, "manifest.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow([cn for _, cn in COLUMNS])
    for m in metas:
        w.writerow([DISC_CN.get(m[k], m[k]) if k == "discipline" else ("arXiv LaTeX 源码" if k == "source_type" else m.get(k, "")) for k, _ in COLUMNS])
print("总表已写入：", os.path.join(root, "manifest.csv"))
