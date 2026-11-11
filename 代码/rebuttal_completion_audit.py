"""Read-only audit of original measurements; write derived coverage and taxonomy tables."""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / '05_模型测试结果/ScienceDoc_11models_results_20261111'
OUT = ROOT / '02_学科统计'
AUDIT = ROOT / '03_Judge一致性标注'
MERGES = [
    ('Computational Complexity', 'Data Structures and Algorithms', 'Algorithms and Complexity'),
    ('Computers and Society', 'Social and Information Networks', 'Computers, Society, and Networks'),
    ('Computer Vision and Pattern Recognition', 'Multimedia', 'Computer Vision and Multimedia'),
    ('Distributed Systems', 'Hardware Architecture', 'Distributed Systems and Architecture'),
    ('Astrophysics of Galaxies', 'Cosmology and Nongalactic Astrophysics', 'Galaxies and Cosmology'),
    ('Mesoscale and Nanoscale Physics', 'Soft Condensed Matter', 'Condensed Matter Physics'),
    ('Algebras', 'Representation Theory', 'Algebra and Representation Theory'),
    ('Biomolecules', 'Molecular Networks', 'Biomolecules and Molecular Networks'),
    ('Computational Finance', 'Mathematical Finance', 'Computational and Mathematical Finance'),
]
MAPPING = {old: new for a, b, new in MERGES for old in (a, b)}


def read(path):
    with path.open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)


def main():
    from judge_audit_sample import allocate, task_of, DISCIPLINE
    import random
    allrows = read(PACK / 'human_agreement_all_models.csv')
    pool = [r for r in allrows if r['in_current_release'] == 'True' and r['answer_verdict'] in ('correct', 'partial', 'wrong')]
    key = read(AUDIT / '判定答案键_勿外发.csv')
    assert len(key) == len({r['编号'] for r in key}) == len({(r['模型'], r['正式题号']) for r in key}) == 2000
    by_pair = {(r['model_name'], r['current_qa_id']): r for r in pool}
    assert len(by_pair) == len(pool)
    sample = [by_pair[(r['模型'], r['正式题号'])] for r in key]
    strata = defaultdict(list)
    for r in pool:
        strata[(r['model_name'], task_of(r), DISCIPLINE[r['primary_category']])].append(r)
    allocation = allocate(strata, 2000)
    rng = random.Random(2027)
    regenerated = []
    for k in sorted(strata):
        regenerated.extend(rng.sample(strata[k], allocation[k]))
    rng.shuffle(regenerated)
    assert [(r['model_name'], r['current_qa_id']) for r in regenerated] == [(r['模型'], r['正式题号']) for r in key]
    progress = {}
    for who in ('A', 'B'):
        ws = load_workbook(AUDIT / f'专家{who}标注表.xlsx', read_only=True, data_only=True)['标注']
        rows = list(ws.values)[1:]
        assert len(rows) == len({r[0] for r in rows}) == 2000
        assert {r[0] for r in rows} == {r['编号'] for r in key}
        progress[who] = sum(r[6] in ('正确', '部分正确', '错误') for r in rows)
    gaps = {}
    for field, getter in [('模型', lambda r:r['model_name']), ('任务', task_of), ('学科', lambda r:r['primary_category']), ('Judge判定', lambda r:r['answer_verdict'])]:
        a, b = Counter(map(getter, pool)), Counter(map(getter, sample))
        gaps[field] = max(abs(100*b[k]/len(sample)-100*a[k]/len(pool)) for k in a)
    # Use consensus metadata across model files; never infer a missing field from question text.
    meta = {}
    for f in sorted((PACK / 'per_model_details').glob('*/details.csv')):
        for r in read(f):
            if r['in_current_release'] != 'True' or not r['current_qa_id'] or not r['primary_category']:
                continue
            k, v = r['current_qa_id'], (r['primary_category'], r['secondary_category'])
            if k in meta:
                assert meta[k] == v, (k, meta[k], v)
            meta[k] = v
    fields = sorted(set(meta.values()))
    assert len(fields) == 61
    counts = Counter(meta.values())
    mapping = [{'学科': d, '原领域': f, '合并领域': MAPPING.get(f, f), '已核实题数': counts[d, f]} for d, f in fields]
    assert len({(r['学科'], r['合并领域']) for r in mapping}) == 52
    write(OUT / '领域合并映射_61到52.csv', list(mapping[0]), mapping)
    official = read(PACK / 'qa_id_mapping_final_2200.csv')
    assert len({r['new_qa_id'] for r in official}) == 2200
    question_map = []
    for r in official:
        q = r['new_qa_id']; d, f = meta.get(q, ('', ''))
        question_map.append({'正式题号':q, '学科':d, '原领域':f, '合并领域':MAPPING.get(f, f), '状态':'已核实' if f else '缺少原始元数据'})
    write(OUT / '2200题领域合并对照.csv', list(question_map[0]), question_map)
    manifest = read(ROOT / '06_200篇结构化论文/manifest.csv')
    for r in manifest:
        r['合并领域'] = MAPPING.get(r['领域（论文图3）'], r['领域（论文图3）'])
    write(OUT / '200篇结构化论文_合并领域索引.csv', list(manifest[0]), manifest)
    models = sorted({r['模型'] for r in key})
    model_rows = []
    for m in models:
        subset = [r for r in key if r['模型'] == m]
        c = Counter(r['Judge判定'] for r in subset)
        model_rows.append({'model':m, 'n':len(subset), 'correct':c['正确'], 'partial':c['部分正确'], 'wrong':c['错误'], 'judge_accuracy':c['正确']/len(subset)})
    result = {'status':'真实专家标注尚未开始', 'n':2000, 'human_completed':progress,
              'original_pool':len(allrows), 'judged_pool':len(pool), 'strata':len(strata),
              'unique_questions':len({r['正式题号'] for r in key}), 'sampling_reproduced':True,
              'max_distribution_difference_pp':gaps, 'models':model_rows,
              'missing_question_metadata':[r['正式题号'] for r in question_map if not r['原领域']],
              'recovered_sample_metadata':[{'编号':r['编号'], '题号':r['正式题号'], '原学科':r['学科'], '核实学科':meta[r['正式题号']][0]} for r in key if r['学科']=='未标学科']}
    (AUDIT / '真实标注进度与Judge统计.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    lines = ['# 真实标注进度与 Judge 统计', '',
             f"真实标注：专家 A {progress['A']}/2000；专家 B {progress['B']}/2000。人—人及人—Judge 的 ρ、κ 均为 N/A（缺少真实标注），不是 0。", '',
             '抽样种子 2027 已重新计算，2,000 个编号及对应样本逐项一致。样本为 2,000 个模型回答，包含 1,349 道不同问题。', '',
             '| 模型 | n | Judge 正确 | 部分正确 | 错误 | Judge 准确率 (%) |', '|---|---:|---:|---:|---:|---:|']
    lines += [f"| {r['model']} | {r['n']} | {r['correct']} | {r['partial']} | {r['wrong']} | {100*r['judge_accuracy']:.2f} |" for r in model_rows]
    lines += ['', '## 抽样差距（百分点）', '']
    lines += [f'- {k}：最大绝对差 {v:.4f}。' for k,v in gaps.items()]
    lines += ['', 'A0033 / rea_126、A1836 / rea_090 的原始样本元数据缺失；其他模型的同题元数据一致为 Physics。为保留抽样可复现性，原答案键和盲标表未改写，分析时可按正式题号补齐。',
              '', '## 领域合并', '', '已生成 61→52 完整映射、2,200 题逐题对照及 200 篇结构化论文合并索引。',
              f"已核实 {len(meta)} 题；待补原始元数据：{', '.join(result['missing_question_metadata'])}。这两题没有猜填。",
              'Space Biophysics 保留原数据名称；200篇下载索引采用 Space Physics，两者对应关系仍需作者核对。合并只改变报告分类，不增加样本量或统计功效。']
    (AUDIT / '真实标注进度与Judge统计.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
