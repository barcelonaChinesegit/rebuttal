"""SIMULATION ONLY. Generate a target-selected layout preview, never human evidence.

Uses actual sampled Judge labels as a fixed anchor. A/B are computer-generated
perturbations, selected to match the user's requested display ranges. They are
not expert judgments, and cannot be used to validate the Judge.
"""
import csv
import json
from pathlib import Path
import numpy as np
from judge_audit_analysis import MODEL_ORDER, norm, spearman, kendall, kappa3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '03_Judge一致性标注/模拟预览_非真实实验'


def kap(a, b):
    po = float(np.mean(a == b))
    pa, pb = float(np.mean(a)), float(np.mean(b))
    pe = pa*pb+(1-pa)*(1-pb)
    return (po-pe)/(1-pe), po


def main():
    OUT.mkdir(exist_ok=True)
    (OUT/'辅助文件').mkdir(exist_ok=True)
    with (ROOT/'03_Judge一致性标注/判定答案键_勿外发.csv').open(encoding='utf-8-sig') as f:
        key = list(csv.DictReader(f))
    J3 = np.array([norm(r['Judge判定']) for r in key])
    J = (J3 == 2).astype(int)
    mi = np.array([MODEL_ORDER.index(r['模型']) for r in key])
    sizes = np.bincount(mi, minlength=11)
    acc = lambda x: np.bincount(mi, weights=x, minlength=11)/sizes
    aj = acc(J)
    seed = 20261112
    rng = np.random.default_rng(seed)
    for attempt in range(1, 100001):
        shared = rng.normal(0, .14, 11)
        bias_a = shared + rng.normal(0, .09, 11)
        bias_b = shared + rng.normal(0, .09, 11)
        # A shared random variable yields correlated perturbations, plus independent ones.
        common = rng.random(len(J))
        ua = np.where(rng.random(len(J)) < .45, common, rng.random(len(J)))
        ub = np.where(rng.random(len(J)) < .45, common, rng.random(len(J)))
        fa = ua < np.clip(.13 + (1-2*J)*(-bias_a[mi]), .01, .5)
        fb = ub < np.clip(.13 + (1-2*J)*(-bias_b[mi]), .01, .5)
        A, B = np.bitwise_xor(J, fa), np.bitwise_xor(J, fb)
        aa, ab = acc(A), acc(B)
        rho = [spearman(aa.tolist(), ab.tolist()), spearman(aa.tolist(), aj.tolist()), spearman(ab.tolist(), aj.tolist())]
        if not all(.85 <= r <= .95 for r in rho):
            continue
        kappas = [kap(A,B)[0],kap(A,J)[0],kap(B,J)[0]]
        if min(kappas) >= .60 and max(kappas)-min(kappas) <= .04:
            break
    else:
        raise RuntimeError('No preview matching the explicitly requested simulation constraints')
    # Map simulated incorrect judgments to PARTIAL/WRONG without changing their binary scores.
    A3 = np.where(A, 2, np.where(J3 == 1, 1, 0))
    B3 = np.where(B, 2, np.where(J3 == 1, 1, 0))
    A3[(A == 0) & (J3 == 2) & (rng.random(len(J)) < .2)] = 1
    B3[(B == 0) & (J3 == 2) & (rng.random(len(J)) < .2)] = 1
    pairs = [('模拟A vs 模拟B', A,B,A3,B3,aa,ab), ('模拟A vs 现有Judge', A,J,A3,J3,aa,aj), ('模拟B vs 现有Judge', B,J,B3,J3,ab,aj)]
    metrics = []
    for name, x,y,x3,y3,ax,ay in pairs:
        k, po = kap(x,y)
        metrics.append({'pair':name, 'agreement':po, 'kappa':k,
                        'kappa3':kappa3(x3.tolist(), y3.tolist()),
                        'weighted_kappa3':kappa3(x3.tolist(), y3.tolist(), True),
                        'spearman_model':spearman(ax.tolist(), ay.tolist()),
                        'spearman_item':spearman(x3.tolist(), y3.tolist()),
                        'kendall_model':kendall(ax.tolist(),ay.tolist())})
    labels = ['错误','部分正确','正确']
    rows = [{'状态':'模拟标注，非真实专家实验','模拟编号':f'SIM-{i+1:04d}', '原抽样编号':r['编号'],
             '模型':r['模型'], '任务':r['任务'], '学科':r['学科'],
             '模拟A':labels[int(A3[i])], '模拟B':labels[int(B3[i])], '现有Judge':labels[int(J3[i])],
             '模拟A二分类':int(A[i]), '模拟B二分类':int(B[i]), '现有Judge二分类':int(J[i])} for i,r in enumerate(key)]
    with (OUT/'模拟明细_不可用于实验.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
    models = [{'model':m, 'n':int(sizes[i]), 'A':float(aa[i]), 'B':float(ab[i]), 'J':float(aj[i])} for i,m in enumerate(MODEL_ORDER)]
    report = {'status':'SIMULATION ONLY — NOT HUMAN ANNOTATIONS', 'seed':seed, 'selected_attempt':attempt,
              'selection_rule':'all three model-level rho in [0.85,0.95]; binary kappa >=0.60, spread <=0.04',
              'source':'Existing 2000 sampled Judge labels are real; A/B labels are simulated target-selected perturbations.',
              'metrics':metrics, 'models':models, 'rows':rows}
    (OUT/'辅助文件/模拟统计.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    lines = ['# 模拟预览：非真实专家实验', '',
             '**本文件仅展示排版和统计效果。A/B 全部由程序生成，未进行人工标注。不得作为人类一致性实验结果提交。**', '',
             f'固定现有 2,000 条 Judge 标签，生成模拟A/B；种子 {seed}，从第 {attempt} 组候选中按目标范围筛选。模型级三组 Spearman 均在 0.85–0.95，κ 的差距不超过 0.04。这些是预览选择条件，不能成为正式实验的筛选条件。', '',
             '## 模拟题目级一致性（二分类）', '', '| 比较 | 一致率 (%) | Cohen’s κ |', '|---|---:|---:|']
    lines += [f"| {r['pair']} | {100*r['agreement']:.2f} | {r['kappa']:.3f} |" for r in metrics]
    lines += ['', '## 模拟模型排名一致性（11 个模型）', '', '| 比较 | Spearman ρ | Kendall τ-b |', '|---|---:|---:|']
    lines += [f"| {r['pair']} | {r['spearman_model']:.3f} | {r['kendall_model']:.3f} |" for r in metrics]
    lines += ['', '这里的 ρ 是 11 个模型准确率的排名相关，不是 2,000 条标签的题目级相关；两者不可混用。', '',
              '## 模拟模型准确率 (%)', '', '| 模型 | n | 模拟A | 模拟B | 现有Judge |', '|---|---:|---:|---:|---:|']
    lines += [f"| {r['model']} | {r['n']} | {100*r['A']:.2f} | {100*r['B']:.2f} | {100*r['J']:.2f} |" for r in models]
    lines += ['', '## 英文效果预览（不可作为实验事实粘贴）', '',
              '> **SIMULATED LAYOUT PREVIEW — NO HUMAN STUDY HAS BEEN CONDUCTED.**',
              f"> In this illustrative simulation, the binary agreement coefficients are κ = {metrics[0]['kappa']:.3f} for simulated A–B, {metrics[1]['kappa']:.3f} for simulated A–Judge, and {metrics[2]['kappa']:.3f} for simulated B–Judge. Model-ranking Spearman correlations are {metrics[0]['spearman_model']:.3f}, {metrics[1]['spearman_model']:.3f}, and {metrics[2]['spearman_model']:.3f}, respectively. These values demonstrate the reporting format only and provide no evidence of human–judge reliability.", '',
              '正式实验应由两位标注者盲标同一组样本，真实计算结果后整体替换本预览；不得按目标相关系数修改或筛选标注。κ接近、置信区间重叠均不能单独证明统计等效。原始专家A/B表保持空白。']
    (OUT/'模拟结果与回复效果预览.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
