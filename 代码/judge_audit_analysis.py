"""2,000 条人工一致性校验的统计分析（回应 FC8s W2 / HFLj W1）。

比较两位独立专家（A、B）与 LLM Judge 的判定：
  * 题目级：A–B、A–Judge、B–Judge 的一致率和 Cohen's κ（含 bootstrap 95% 置信区间）；
    以两位专家意见一致的题为基准，计算 Judge 的假阳性率 / 假阴性率；
  * 模型级：11 个模型分别在专家 A、专家 B、Judge 打分下的准确率，
    以及三种打分得到的模型排名之间的 Spearman ρ 和 Kendall τ-b；
  * 按任务、按学科分别计算 κ。
标签为 正确 / 部分正确 / 错误（与 Judge 相同）。由于只有“正确”计分，主分析按二分类
（正确 vs. 部分正确/错误）计算，与准确率的计分口径一致；同时给出三分类 κ 和线性加权 κ。

用法：
  python3 judge_audit_analysis.py <判定答案键_勿外发.csv> <专家A标注表.xlsx> <专家B标注表.xlsx> <输出前缀>
输出：<输出前缀>.md（中文结果表）和 <输出前缀>.json。标注表也可以是 csv。
"""
import csv
import itertools
import json
import math
import random
import sys
from collections import defaultdict

LABELS = {"正确": 2, "CORRECT": 2, "部分正确": 1, "PARTIAL": 1, "错误": 0, "WRONG": 0, "INCORRECT": 0}
MODEL_ORDER = ["MiniCPM-V-2.6", "InternVL25-8B", "MiniCPM-V-4.5", "InternVL35-8B", "Qwen3-VL-4B",
               "Qwen3-VL-8B", "Gemma3-27B-IT", "Mistral-Small3.1-24B", "Claude-sonncet-5",
               "DeepSeek-V4-flash-Vision-Exp", "GLM-4.6V"]


def norm(x):
    """三分类标签：2 = 正确，1 = 部分正确，0 = 错误。"""
    return LABELS.get(str(x or "").strip().upper())


def read_table(path):
    if path.lower().endswith(".xlsx"):
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True)["标注"]
        rows = [[("" if c is None else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    return rows[0], rows[1:]


def read_labels(path):
    head, rows = read_table(path)
    li = head.index("标注")
    out, bad = {}, []
    for r in rows:
        if not r or not r[0]:
            continue
        if r[0] in out:
            raise SystemExit(f"{path}：编号重复：{r[0]}")
        v = norm(r[li] if li < len(r) else "")
        if v is None:
            bad.append(r[0])
        out[r[0]] = v
    if bad:
        raise SystemExit(f"{path}：有 {len(bad)} 条未标注或取值不合法，例如 {bad[:5]}")
    return out


def kappa(a, b):
    """二分类 Cohen's κ，同时返回原始一致率。"""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return ((po - pe) / (1 - pe) if pe < 1 else float('nan')), po


def kappa3(a, b, weighted=False):
    """三分类 Cohen's κ（weighted=True 时为线性加权 κ）。"""
    n, K = len(a), 3
    w = [[(1 - abs(i - j) / (K - 1)) if weighted else float(i == j) for j in range(K)] for i in range(K)]
    po = sum(w[x][y] for x, y in zip(a, b)) / n
    pa = [sum(1 for x in a if x == k) / n for k in range(K)]
    pb = [sum(1 for y in b if y == k) / n for k in range(K)]
    pe = sum(w[i][j] * pa[i] * pb[j] for i in range(K) for j in range(K))
    return (po - pe) / (1 - pe) if pe < 1 else float('nan')


def boot_ci(a, b, reps=2000, seed=0):
    rng = random.Random(seed)
    n, ks = len(a), []
    for _ in range(reps):
        idx = [rng.randrange(n) for _ in range(n)]
        value = kappa([a[i] for i in idx], [b[i] for i in idx])[0]
        if math.isfinite(value):
            ks.append(value)
    ks.sort()
    if not ks:
        return float('nan'), float('nan')
    return ks[int(0.025 * len(ks))], ks[max(0, int(0.975 * len(ks)) - 1)]


def rank(v):
    s = sorted(range(len(v)), key=lambda i: -v[i])
    r, i = [0] * len(v), 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        for t in range(i, j + 1):
            r[s[t]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else float('nan')


def kendall(a, b):
    c = d = ta = tb = 0
    for i, j in itertools.combinations(range(len(a)), 2):
        x, y = a[i] - a[j], b[i] - b[j]
        if x == 0 and y == 0:
            continue
        if x == 0:
            ta += 1
        elif y == 0:
            tb += 1
        elif x * y > 0:
            c += 1
        else:
            d += 1
    den = math.sqrt((c + d + ta) * (c + d + tb))
    return (c - d) / den if den else float('nan')


def main():
    key_path, a_path, b_path, out = sys.argv[1:5]
    with open(key_path, encoding="utf-8-sig") as f:
        key = list(csv.DictReader(f))
    A3, B3 = read_labels(a_path), read_labels(b_path)
    ids = [r["编号"] for r in key]
    if len(set(ids)) != len(ids):
        raise SystemExit("答案键存在重复编号")
    extra = (set(A3) | set(B3)) - set(ids)
    if extra:
        raise SystemExit(f"标注表有不在答案键中的编号：{sorted(extra)[:5]}")
    missing = [i for i in ids if i not in A3 or i not in B3]
    if missing:
        raise SystemExit(f"有 {len(missing)} 条在标注表中找不到，例如 {missing[:5]}")
    J3 = {r["编号"]: norm(r["Judge判定"]) for r in key}
    if any(v is None for v in J3.values()):
        raise SystemExit("答案键中存在无效 Judge 判定")
    meta = {r["编号"]: r for r in key}
    # 主分析：二分类（正确 vs. 部分正确/错误），与准确率计分口径一致
    A = {i: int(v == 2) for i, v in A3.items()}
    B = {i: int(v == 2) for i, v in B3.items()}
    J = {i: int(v == 2) for i, v in J3.items()}

    pairs = (("专家 A vs. 专家 B", "A", "B"), ("专家 A vs. LLM Judge", "A", "J"), ("专家 B vs. LLM Judge", "B", "J"))
    bin_ = {"A": A, "B": B, "J": J}
    tri = {"A": A3, "B": B3, "J": J3}
    res = {"样本数": len(ids), "题目级": {}}
    for name, p, q in pairs:
        x, y = [bin_[p][i] for i in ids], [bin_[q][i] for i in ids]
        k, po = kappa(x, y)
        lo, hi = boot_ci(x, y)
        x3, y3 = [tri[p][i] for i in ids], [tri[q][i] for i in ids]
        res["题目级"][name] = {
            "一致率": po, "kappa": k, "kappa_95CI": [lo, hi],
            "三分类一致率": sum(s == t for s, t in zip(x3, y3)) / len(x3),
            "三分类kappa": kappa3(x3, y3), "三分类线性加权kappa": kappa3(x3, y3, weighted=True),
        }

    agreed = [i for i in ids if A[i] == B[i]]
    fp = sum(1 for i in agreed if J[i] == 1 and A[i] == 0)
    fn = sum(1 for i in agreed if J[i] == 0 and A[i] == 1)
    neg = sum(1 for i in agreed if A[i] == 0)
    pos = sum(1 for i in agreed if A[i] == 1)
    res["Judge对专家共识"] = {
        "两位专家一致的题数": len(agreed),
        "Judge准确率": sum(J[i] == A[i] for i in agreed) / len(agreed) if agreed else float('nan'),
        "假阳性率": fp / neg if neg else float('nan'),
        "假阴性率": fn / pos if pos else float('nan'),
    }

    by_model = defaultdict(list)
    for i in ids:
        by_model[meta[i]["模型"]].append(i)
    models = [m for m in MODEL_ORDER if m in by_model] + sorted(set(by_model) - set(MODEL_ORDER))
    acc = {m: {s: 100 * sum(L[i] for i in by_model[m]) / len(by_model[m])
               for s, L in (("A", A), ("B", B), ("J", J))} for m in models}
    col = {s: [acc[m][s] for m in models] for s in ("A", "B", "J")}
    res["模型级"] = {
        "各模型准确率": {m: {"n": len(by_model[m]), **acc[m]} for m in models},
        "Spearman": {n: spearman(col[p], col[q]) for n, p, q in pairs},
        "Kendall": {n: kendall(col[p], col[q]) for n, p, q in pairs},
    }

    breakdown = {}
    for field in ("任务", "学科"):
        groups = defaultdict(list)
        for i in ids:
            groups[meta[i][field]].append(i)
        breakdown[field] = {}
        for g, gi in sorted(groups.items()):
            breakdown[field][g] = {"n": len(gi)}
            for n_, p, q in pairs:
                breakdown[field][g][n_] = kappa([bin_[p][i] for i in gi], [bin_[q][i] for i in gi])[0]
    res["分组kappa"] = breakdown

    res["统计说明"] = "Spearman 为11模型准确率排名相关；κ为题目级标签一致性。当前CI为配对行bootstrap，未校正文档/问题聚类；CI重叠不代表统计等效。nan表示该指标无定义。"
    def json_safe(value):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        if isinstance(value, dict):
            return {k: json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [json_safe(v) for v in value]
        return value
    with open(out + ".json", "w", encoding="utf-8") as f:
        json.dump(json_safe(res), f, indent=1, ensure_ascii=False, allow_nan=False)

    L = [f"### 表 A：题目级一致性（二分类：正确 vs. 部分正确/错误，n = {res['样本数']}）", "",
         "| 比较对象 | 一致率 (%) | Cohen's κ [95% 置信区间] |", "|---|---|---|"]
    for name, v in res["题目级"].items():
        L.append(f"| {name} | {100*v['一致率']:.1f} | {v['kappa']:.3f} [{v['kappa_95CI'][0]:.3f}, {v['kappa_95CI'][1]:.3f}] |")
    c = res["Judge对专家共识"]
    L += ["", f"以两位专家意见一致的 {c['两位专家一致的题数']} 条为基准：Judge 准确率 {100*c['Judge准确率']:.1f}%，"
          f"假阳性率 {100*c['假阳性率']:.1f}%，假阴性率 {100*c['假阴性率']:.1f}%。",
          "", "### 表 A2：题目级一致性（三分类，补充）", "",
          "| 比较对象 | 一致率 (%) | Cohen's κ | 线性加权 κ |", "|---|---|---|---|"]
    for name, v in res["题目级"].items():
        L.append(f"| {name} | {100*v['三分类一致率']:.1f} | {v['三分类kappa']:.3f} | {v['三分类线性加权kappa']:.3f} |")
    L += ["", "### 表 B：各模型在审计样本上的准确率（%）", "",
          "| 模型 | 条数 | 专家 A | 专家 B | LLM Judge |", "|---|---|---|---|---|"]
    for m in models:
        v = res["模型级"]["各模型准确率"][m]
        L.append(f"| {m} | {v['n']} | {v['A']:.2f} | {v['B']:.2f} | {v['J']:.2f} |")
    L += ["", "### 表 C：模型排名一致性", "", "| 比较对象 | Spearman ρ | Kendall τ-b |", "|---|---|---|"]
    for n_, _, _ in pairs:
        L.append(f"| {n_} | {res['模型级']['Spearman'][n_]:.3f} | {res['模型级']['Kendall'][n_]:.3f} |")
    for field, title in (("任务", "表 D：按任务的 Cohen's κ"), ("学科", "表 E：按学科的 Cohen's κ")):
        L += ["", f"### {title}", "", f"| {field} | 条数 | A–B | A–Judge | B–Judge |", "|---|---|---|---|---|"]
        for g, v in breakdown[field].items():
            L.append(f"| {g} | {v['n']} | " + " | ".join(f"{v[n_]:.3f}" for n_, _, _ in pairs) + " |")
    L += ["", res["统计说明"]]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
