"""FC8s W1 的学科统计：只用论文 Table 3 的数字（纯标准库）。

内容：
  1. 每个学科准确率的 Wilson 95% 置信区间；
  2. 数学是否稳定偏弱（符号检验、逐模型两比例检验、合并检验）；
  3. 各学科的模型排名与总体排名的一致性（Spearman ρ、Kendall τ-b、Kendall's W）；
  4. 合并为两大组后的准确率与置信区间；
  5. 图 5b 热力图每一格的显著性（该学科 vs. 其余学科，两比例 z 检验）。
各学科题数取自结果包 summary/report.json 的 membership 字段（与 Table 3 一致）。

用法：python3 -I discipline_stats.py <输出目录>
输出：学科统计结果.txt、学科置信区间.json、table3_with_ci.tex（论文附录用，英文）
"""
import itertools
import json
import math
import os
import sys

N = {"CS": 745, "Phy": 379, "Stat": 366, "Math": 245, "EE": 128, "Econ": 137, "QBio": 114, "QFin": 86}
CN = {"CS": "计算机", "Phy": "物理", "Stat": "统计", "Math": "数学", "EE": "电子工程",
      "Econ": "经济", "QBio": "定量生物", "QFin": "定量金融"}
D = list(N)
T = {  # 模型: [总体, CS, Phy, Stat, Math, EE, Econ, QBio, QFin]（论文 Table 3）
    "MiniCPM-V 2.6":         [15.59, 16.51, 18.73, 15.85, 10.20, 10.16, 16.06, 15.79, 15.12],
    "InternVL2.5-8B":        [22.32, 21.34, 26.39, 24.32, 13.88, 17.97, 32.12, 19.30, 23.26],
    "MiniCPM-V 4.5":         [34.32, 25.91, 44.85, 33.88, 30.20, 30.47, 40.88, 51.75, 46.51],
    "InternVL3.5-8B":        [34.95, 37.99, 30.34, 36.07, 20.82, 38.28, 43.80, 36.84, 43.02],
    "Qwen3-VL-4B":           [64.91, 63.89, 71.24, 55.46, 62.04, 64.06, 67.88, 80.70, 69.77],
    "Qwen3-VL-8B":           [68.32, 67.11, 70.98, 66.12, 62.45, 71.88, 70.80, 76.32, 73.26],
    "Gemma 3 27B":           [47.32, 50.34, 51.72, 47.81, 32.24, 41.41, 57.66, 38.60, 46.51],
    "Mistral-Small-3.1-24B": [49.00, 40.13, 60.95, 45.08, 45.71, 50.78, 63.50, 64.91, 52.33],
    "Claude Sonnet 5":       [69.09, 70.07, 71.50, 60.11, 61.22, 80.47, 73.72, 79.82, 72.09],
    "DeepSeek-V4-Flash":     [79.45, 80.54, 77.57, 83.06, 71.84, 79.69, 83.94, 78.95, 77.91],
    "GLM-4.6V":              [80.95, 80.67, 82.59, 80.05, 74.29, 85.16, 86.86, 82.46, 81.40],
}


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return 100 * (c - h), 100 * (c + h)


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
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


def kendall_tau_b(a, b):
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
    return (c - d) / math.sqrt((c + d + ta) * (c + d + tb))


def two_prop_p(k1, n1, k2, n2):
    p = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0
    return math.erfc(abs((k1 / n1 - k2 / n2) / se) / math.sqrt(2))


def binom_two_sided(k, n):
    pk = [math.comb(n, i) * 0.5 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] + 1e-15))


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        print('用法：python3 代码/discipline_stats.py <输出目录>')
        return
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    out = []
    say = out.append

    # 由准确率反推答对题数，并校验与 Table 3 完全一致
    K = {}
    for m, v in T.items():
        K[m] = {}
        for d, a in zip(D, v[1:]):
            k = round(a * N[d] / 100)
            assert abs(100 * k / N[d] - a) < 0.006, (m, d, a)
            K[m][d] = k
        assert abs(100 * sum(K[m].values()) / 2200 - v[0]) < 0.006, m

    say("== 1. 各学科 Wilson 95% 置信区间半宽（百分点，11 个模型平均 / 最大）")
    for d in D:
        hw = [(wilson(K[m][d], N[d])[1] - wilson(K[m][d], N[d])[0]) / 2 for m in T]
        say(f"{CN[d]:6s} 题数={N[d]:4d}  平均 ±{sum(hw)/len(hw):.1f}  最大 ±{max(hw):.1f}")

    say("\n== 2. 数学是否稳定低于模型自身的总体准确率")
    below = sum(1 for v in T.values() if v[4] < v[0])
    say(f"{below}/11 个模型数学低于自身总体准确率；双侧符号检验 p = {binom_two_sided(below, 11):.4f}")
    for m, v in T.items():
        km, kr = K[m]["Math"], sum(K[m].values()) - K[m]["Math"]
        say(f"  {m:22s} 数学 {v[4]:5.2f} vs 其余学科 {100*kr/1955:5.2f}  p={two_prop_p(km, 245, kr, 1955):.4f}")
    km = sum(K[m]["Math"] for m in T)
    kr = sum(sum(K[m].values()) - K[m]["Math"] for m in T)
    say(f"  合并 11 个模型：数学 {100*km/(245*11):.2f} vs 其余 {100*kr/(1955*11):.2f}  "
        f"p={two_prop_p(km, 245*11, kr, 1955*11):.2e}")

    say("\n== 3. 各学科的模型排名与总体排名的一致性")
    allv = [v[0] for v in T.values()]
    for j, d in enumerate(D):
        col = [v[j + 1] for v in T.values()]
        say(f"{CN[d]:6s} 题数={N[d]:4d}  Spearman ρ={spearman(col, allv):.3f}  Kendall τ-b={kendall_tau_b(col, allv):.3f}")
    pairs = [spearman([v[i + 1] for v in T.values()], [v[j + 1] for v in T.values()])
             for i, j in itertools.combinations(range(8), 2)]
    say(f"学科两两之间的 Spearman ρ：平均 {sum(pairs)/len(pairs):.3f}，最小 {min(pairs):.3f}")
    R = [rank([v[j + 1] for v in T.values()]) for j in range(8)]
    Rsum = [sum(R[j][i] for j in range(8)) for i in range(11)]
    mR = sum(Rsum) / 11
    W = 12 * sum((x - mR) ** 2 for x in Rsum) / (8 ** 2 * (11 ** 3 - 11))
    say(f"Kendall's W（8 个学科对 11 个模型的排名一致性）= {W:.3f}，χ²={8*10*W:.1f}，自由度=10")

    say("\n== 4. 合并为 Table 3 表头的两大组")
    G = {"基础与计算科学（CS/物理/统计/数学）": ["CS", "Phy", "Stat", "Math"],
         "应用与交叉科学（电子工程/经济/定量生物/定量金融）": ["EE", "Econ", "QBio", "QFin"]}
    for g, ds in G.items():
        n = sum(N[d] for d in ds)
        hw = [(wilson(sum(K[m][d] for d in ds), n)[1] - wilson(sum(K[m][d] for d in ds), n)[0]) / 2 for m in T]
        say(f"{g}  题数={n}  置信区间半宽平均 ±{sum(hw)/len(hw):.1f}")
        for m in T:
            say(f"   {m:22s} {100*sum(K[m][d] for d in ds)/n:5.2f}")

    say("\n== 5. 图 5b 热力图每格显著性（格内数字 = 该学科准确率 − 模型总体准确率；* p<0.05，** p<0.01）")
    say("模型".ljust(22) + "".join(CN[d].rjust(8) for d in D))
    sig = {d: [0, 0] for d in D}
    for m, v in T.items():
        row = m.ljust(22)
        tot = sum(K[m].values())
        for d in D:
            k, n = K[m][d], N[d]
            p = two_prop_p(k, n, tot - k, 2200 - n)
            diff = 100 * k / n - v[0]
            star = "**" if p < 0.01 else ("*" if p < 0.05 else "")
            if p < 0.05:
                sig[d][0 if diff > 0 else 1] += 1
            row += f"{diff:+7.1f}{star:<3s}"
        say(row)
    say("各学科显著格数（高于 / 低于模型自身平均）：")
    for d in D:
        say(f"  {CN[d]}：高于 {sig[d][0]} 个，低于 {sig[d][1]} 个")
    say(f"共 {sum(a+b for a, b in sig.values())}/88 格显著（纯随机情况下约 4.4 格）")

    # 88项同一检验族的 Holm 校正，避免把未经多重比较校正的星号当作确认性结论。
    tests = []
    for m, v in T.items():
        tot = sum(K[m].values())
        for d in D:
            p = two_prop_p(K[m][d], N[d], tot-K[m][d], 2200-N[d])
            tests.append({'model': m, 'discipline': d, 'p_raw': p,
                          'difference_pp': 100*K[m][d]/N[d]-v[0]})
    tests.sort(key=lambda x: x['p_raw'])
    running = 0.0
    for i, t in enumerate(tests):
        running = max(running, min(1.0, (len(tests)-i)*t['p_raw']))
        t['p_holm'] = running
    say('\n== 5b. 88次比较的 Holm 校正（双侧，α=0.05）')
    for t in tests:
        if t['p_holm'] < .05:
            say(f"  {t['model']} / {CN[t['discipline']]}: Δ={t['difference_pp']:+.2f} pp, p_Holm={t['p_holm']:.6g}")
    say(f"Holm校正后显著：{sum(t['p_holm'] < .05 for t in tests)}/88。")
    say('局限：Wilson区间和两比例检验假设题目独立；同文档问题可能相关。跨模型重复回答不能视为独立样本，合并p值/11模型符号检验仅供诊断，不用于rebuttal确认性结论。排名相关是描述性结果，不能证明所有相邻模型差异显著。')
    with open(os.path.join(out_dir, '多重比较校正.json'), 'w', encoding='utf-8') as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)

    say("\n== 6. 完整置信区间表（准确率 [下限, 上限]）")
    tab = {m: {CN[d]: [round(100 * K[m][d] / N[d], 2), *[round(x, 1) for x in wilson(K[m][d], N[d])]]
               for d in D} for m in T}
    for m in T:
        say(m.ljust(22) + " ".join(f"{CN[d]}:{tab[m][CN[d]][0]:.1f}[{tab[m][CN[d]][1]:.1f},{tab[m][CN[d]][2]:.1f}]" for d in D))

    with open(os.path.join(out_dir, "学科统计结果.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(out_dir, "学科置信区间.json"), "w", encoding="utf-8") as f:
        json.dump({"答对题数": K, "准确率与Wilson置信区间": tab}, f, ensure_ascii=False, indent=1)
    # 论文附录用的 LaTeX 表（论文是英文，所以表内保持英文）
    L = [r"\begin{table*}[t]\centering\small",
         r"\caption{Discipline-level accuracy (\%) with Wilson 95\% confidence intervals. $n$ is the number of questions per discipline.}",
         r"\label{tab:subject_results_ci}\resizebox{\textwidth}{!}{\begin{tabular}{l" + "c" * 8 + r"}\toprule",
         "Model & " + " & ".join(r"\textbf{%s} ($n$=%d)" % (d, N[d]) for d in D) + r" \\ \midrule"]
    for m in T:
        L.append(m + " & " + " & ".join(r"%.1f \scriptsize{[%.1f, %.1f]}" % tuple(tab[m][CN[d]]) for d in D) + r" \\")
    L.append(r"\bottomrule\end{tabular}}\end{table*}")
    with open(os.path.join(out_dir, "table3_with_ci.tex"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
