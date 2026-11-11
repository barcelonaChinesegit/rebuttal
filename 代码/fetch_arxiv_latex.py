"""按 ScienceDoc 的学科 / 领域比例，从 arXiv 挑选并下载 200 篇论文（LaTeX 源码 + PDF），
并生成结构化文件。

用法：python3 -I fetch_arxiv_latex.py <输出目录>
只用 Python 标准库。下载内容一律视为不可信数据：解压时做路径安全检查，
压缩包里的任何文件都不会被执行。
"""
import csv
import gzip
import io
import json
import os
import re
import sys
import tarfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
UA = {"User-Agent": "ScienceDoc-rebuttal/1.0 (academic research; mailto:none)"}
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}

# （学科，论文图 3 中的领域名，arXiv 分类，篇数配额）
PLAN = [
    # 计算机科学：84 篇
    ("CS", "Artificial Intelligence", "cs.AI", 8),
    ("CS", "Computation and Language", "cs.CL", 8),
    ("CS", "Computer Vision and Pattern Recognition", "cs.CV", 8),
    ("CS", "Machine Learning", "cs.LG", 8),
    ("CS", "Computational Complexity", "cs.CC", 4),
    ("CS", "Computational Engineering, Finance, and Science", "cs.CE", 4),
    ("CS", "Computational Geometry", "cs.CG", 4),
    ("CS", "Computer Science and Game Theory", "cs.GT", 4),
    ("CS", "Computers and Society", "cs.CY", 4),
    ("CS", "Cryptography and Security", "cs.CR", 4),
    ("CS", "Data Structures and Algorithms", "cs.DS", 4),
    ("CS", "Databases", "cs.DB", 3),
    ("CS", "Distributed Systems", "cs.DC", 3),
    ("CS", "Hardware Architecture", "cs.AR", 3),
    ("CS", "Information Theory", "cs.IT", 3),
    ("CS", "Multimedia", "cs.MM", 3),
    ("CS", "Neural and Evolutionary Computing", "cs.NE", 3),
    ("CS", "Programming Languages", "cs.PL", 3),
    ("CS", "Social and Information Networks", "cs.SI", 3),
    # 物理：37 篇
    ("PHY", "Quantum Physics", "quant-ph", 3),
    ("PHY", "High Energy Physics", "hep-ph", 3),
    ("PHY", "General Relativity and Quantum Cosmology", "gr-qc", 3),
    ("PHY", "Mesoscale and Nanoscale Physics", "cond-mat.mes-hall", 3),
    ("PHY", "Statistical Mechanics", "cond-mat.stat-mech", 3),
    ("PHY", "Applied Plasma Physics", "physics.plasm-ph", 2),
    ("PHY", "Astrophysics of Galaxies", "astro-ph.GA", 2),
    ("PHY", "Atomic and Molecular Clusters", "physics.atm-clus", 2),
    ("PHY", "Classical Physics", "physics.class-ph", 2),
    ("PHY", "Cosmology and Nongalactic Astrophysics", "astro-ph.CO", 2),
    ("PHY", "High Energy Astrophysical Phenomena", "astro-ph.HE", 2),
    ("PHY", "Instrumentation and Methods for Astrophysics", "astro-ph.IM", 2),
    ("PHY", "Mathematical Physics", "math-ph", 2),
    ("PHY", "Nuclear Physics", "nucl-th", 2),
    ("PHY", "Soft Condensed Matter", "cond-mat.soft", 2),
    ("PHY", "Space Physics", "physics.space-ph", 2),
    # 数学：23 篇
    ("MATH", "Analysis of PDEs", "math.AP", 3),
    ("MATH", "Applied Probability", "math.PR", 3),
    ("MATH", "Number Theory", "math.NT", 3),
    ("MATH", "Algebraic Geometry", "math.AG", 2),
    ("MATH", "Algebraic Topology", "math.AT", 2),
    ("MATH", "Algebras", "math.RA", 2),
    ("MATH", "Category Theory", "math.CT", 2),
    ("MATH", "General Mathematics", "math.GM", 2),
    ("MATH", "Geometry", "math.MG", 2),
    ("MATH", "Representation Theory", "math.RT", 2),
    # 统计：19 篇
    ("STAT", "Applications and Methodology", "stat.ME", 5),
    ("STAT", "Applications and Methodology", "stat.AP", 4),
    ("STAT", "Computational Statistics", "stat.CO", 6),
    ("STAT", "Other Statistics", "stat.OT", 4),
    # 定量生物：11 篇
    ("QBIO", "Biomolecules", "q-bio.BM", 3),
    ("QBIO", "Cell Behavior", "q-bio.CB", 3),
    ("QBIO", "Molecular Networks", "q-bio.MN", 3),
    ("QBIO", "Other Quantitative Biology", "q-bio.OT", 2),
    # 电子工程与系统科学：10 篇
    ("EESS", "Audio and Speech Processing", "eess.AS", 3),
    ("EESS", "Image and Video Processing", "eess.IV", 4),
    ("EESS", "Signal Processing", "eess.SP", 3),
    # 经济：9 篇
    ("ECON", "Econometrics", "econ.EM", 5),
    ("ECON", "Theoretical Economics", "econ.TH", 4),
    # 定量金融：7 篇
    ("QFIN", "Computational Finance", "q-fin.CP", 2),
    ("QFIN", "Mathematical Finance", "q-fin.MF", 2),
    ("QFIN", "Portfolio and Risk Management", "q-fin.PM", 2),
    ("QFIN", "Statistical Finance", "q-fin.ST", 1),
]

DATE_RANGE = "[202401010000 TO 202512312359]"
MIN_TEX_CHARS = 15000
MAX_ARCHIVE_BYTES = 60 * 1024 * 1024


def get(url, timeout=90, retries=4, max_seconds=300):
    """下载 url；单次读取超过 max_seconds 秒视为卡死，放弃本次并重试。"""
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                start, chunks = time.time(), []
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        return b"".join(chunks)
                    chunks.append(chunk)
                    if time.time() - start > max_seconds:
                        raise TimeoutError(f"下载超过 {max_seconds} 秒仍未完成")
        except Exception as e:  # noqa: BLE001
            if k == retries - 1:
                raise
            time.sleep(5 * (k + 1))


def query(cat, start, n=50):
    q = f"cat:{cat} AND submittedDate:{DATE_RANGE}"
    url = API + "?" + urllib.parse.urlencode({
        "search_query": q, "start": start, "max_results": n,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    root = ET.fromstring(get(url))
    out = []
    for e in root.findall("a:entry", NS):
        aid = e.find("a:id", NS).text.rsplit("/abs/", 1)[-1]
        prim = e.find("x:primary_category", NS)
        comment = e.find("x:comment", NS)
        out.append({
            "id_v": aid,
            "id": re.sub(r"v\d+$", "", aid),
            "title": " ".join(e.find("a:title", NS).text.split()),
            "primary": prim.get("term") if prim is not None else "",
            "published": e.find("a:published", NS).text,
            "comment": comment.text if comment is not None else "",
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
        })
    return out


def safe_extract(blob, dest):
    """解压 tar(.gz) 或单个 gzip 压缩的 tex 文件，返回解压出的文件列表。"""
    os.makedirs(dest, exist_ok=True)
    root = os.path.realpath(dest)
    try:
        tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    except tarfile.TarError:
        tf = None
    files = []
    if tf is not None:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            name = m.name.lstrip("/")
            target = os.path.realpath(os.path.join(root, name))
            if not target.startswith(root + os.sep) or ".." in name.split("/"):
                continue
            if m.size > 50 * 1024 * 1024:
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            src = tf.extractfile(m)
            if src is None:
                continue
            with open(target, "wb") as f:
                f.write(src.read())
            files.append(os.path.relpath(target, root))
        return files
    # 不是 tar 包：可能是单个 gzip 压缩的 tex，也可能是 PDF（无源码）
    try:
        data = gzip.decompress(blob)
    except OSError:
        data = blob
    if data[:4] == b"%PDF":
        return []
    with open(os.path.join(root, "main.tex"), "wb") as f:
        f.write(data)
    return ["main.tex"]


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def find_main(src_dir, files):
    cands = []
    for rel in files:
        if not rel.lower().endswith(".tex"):
            continue
        t = read_text(os.path.join(src_dir, rel))
        if re.search(r"\\begin\{document\}", t) and re.search(r"\\documentclass", t):
            cands.append((len(t), rel))
    if not cands:
        return None
    return max(cands)[1]


INPUT_RE = re.compile(r"\\(input|include|subfile)\s*\{([^}]+)\}")


def flatten(src_dir, rel, depth=0, seen=None):
    seen = seen if seen is not None else set()
    path = os.path.join(src_dir, rel)
    if depth > 8 or rel in seen or not os.path.isfile(path):
        return ""
    seen.add(rel)
    text = read_text(path)
    base = os.path.dirname(rel)

    def repl(m):
        name = m.group(2).strip()
        for cand in (name, name + ".tex"):
            for b in ("", base):
                r = os.path.normpath(os.path.join(b, cand))
                if r.startswith(".."):
                    continue
                if os.path.isfile(os.path.join(src_dir, r)):
                    return (f"\n%% >>> begin {r}\n" + flatten(src_dir, r, depth + 1, seen)
                            + f"\n%% <<< end {r}\n")
        return m.group(0)

    lines = []
    for line in text.split("\n"):
        code = re.split(r"(?<!\\)%", line, 1)[0]
        if INPUT_RE.search(code):
            line = INPUT_RE.sub(repl, code)
        lines.append(line)
    return "\n".join(lines)


def strip_comments(t):
    return "\n".join(re.split(r"(?<!\\)%", ln, 1)[0] for ln in t.split("\n"))


def braced(t, start):
    """返回从 t[start]（即 '{'）开始的花括号内的内容。"""
    depth, i = 0, start
    while i < len(t):
        if t[i] == "{" and (i == 0 or t[i - 1] != "\\"):
            depth += 1
        elif t[i] == "}" and t[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return t[start + 1:i]
        i += 1
    return t[start + 1:]


def first_cmd(t, cmd):
    m = re.search(r"\\" + cmd + r"\*?\s*(\[[^\]]*\])?\s*\{", t)
    return braced(t, m.end() - 1).strip() if m else ""


ENV_EQ = r"equation\*?|align\*?|gather\*?|multline\*?|eqnarray\*?|displaymath"


def structure(flat, src_dir, files):
    t = strip_comments(flat)
    body = t.split("\\begin{document}", 1)[-1].split("\\end{document}", 1)[0]
    absm = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", body, re.S)
    abstract = absm.group(1).strip() if absm else first_cmd(body, "abstract")

    figures, tables, equations = [], [], []
    for m in re.finditer(r"\\begin\{(figure\*?|wrapfigure|SCfigure)\}(.*?)\\end\{\1\}", body, re.S):
        blk = m.group(2)
        imgs = re.findall(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}", blk)
        resolved = []
        for im in imgs:
            hit = [f for f in files if os.path.splitext(f)[0].endswith(os.path.splitext(im.strip())[0])
                   or f.endswith(im.strip())]
            resolved.append(hit[0] if hit else im.strip())
        figures.append({"caption": first_cmd(blk, "caption"), "label": first_cmd(blk, "label"),
                        "images": resolved})
    for m in re.finditer(r"\\begin\{(table\*?|sidewaystable)\}(.*?)\\end\{\1\}", body, re.S):
        blk = m.group(2)
        tab = re.search(r"\\begin\{(tabular\*?|tabularx|longtable|tblr)\}.*?\\end\{\1\}", blk, re.S)
        tables.append({"caption": first_cmd(blk, "caption"), "label": first_cmd(blk, "label"),
                       "latex": tab.group(0) if tab else blk.strip()})
    for m in re.finditer(r"\\begin\{(" + ENV_EQ + r")\}(.*?)\\end\{\1\}", body, re.S):
        equations.append({"env": m.group(1), "latex": m.group(2).strip()})
    for m in re.finditer(r"\\\[(.*?)\\\]|\$\$(.*?)\$\$", body, re.S):
        equations.append({"env": "display", "latex": (m.group(1) or m.group(2)).strip()})

    # 按 section 切分正文（去掉图表浮动体，公式保留在正文中）
    nofloat = re.sub(r"\\begin\{(figure\*?|table\*?|wrapfigure|sidewaystable)\}.*?\\end\{\1\}",
                     "", body, flags=re.S)
    parts = re.split(r"\\(section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\s*\{", nofloat)
    sections = [{"level": "preamble", "title": "", "text": parts[0].strip()}]
    i = 1
    while i + 1 < len(parts):
        level, rest = parts[i], "{" + parts[i + 1]
        title = braced(rest, 0)
        text = rest[len(title) + 2:]
        sections.append({"level": level, "title": title.strip(), "text": text.strip()})
        i += 2
    return {
        "title": first_cmd(t, "title"),
        "abstract": abstract,
        "sections": sections,
        "figures": figures,
        "tables": tables,
        "equations": equations,
        "stats": {"n_sections": len(sections) - 1, "n_figures": len(figures),
                  "n_tables": len(tables), "n_equations": len(equations),
                  "n_chars": len(body)},
    }


def process(cand, disc, field, cat, out_root):
    pdir = os.path.join(out_root, disc, cand["id"].replace("/", "_"))
    if os.path.isfile(os.path.join(pdir, "structured.json")):
        return json.load(open(os.path.join(pdir, "meta.json")))
    blob = get(f"https://export.arxiv.org/e-print/{cand['id_v']}", timeout=180)
    time.sleep(3)
    if len(blob) > MAX_ARCHIVE_BYTES:
        return None
    src_dir = os.path.join(pdir, "source")
    files = safe_extract(blob, src_dir)
    main = find_main(src_dir, files) if files else None
    if not main:
        _rmtree(pdir)
        return None
    flat = flatten(src_dir, main)
    st = structure(flat, src_dir, files)
    s = st["stats"]
    # 只保留含图表的完整研究论文（对应论文 3.1 节的过滤条件）
    if s["n_chars"] < MIN_TEX_CHARS or s["n_sections"] < 3 or (s["n_figures"] + s["n_tables"]) < 1:
        _rmtree(pdir)
        return None
    pdf = get(f"https://export.arxiv.org/pdf/{cand['id_v']}", timeout=180)
    time.sleep(3)
    if pdf[:4] != b"%PDF":
        _rmtree(pdir)
        return None
    with open(os.path.join(pdir, "paper.pdf"), "wb") as f:
        f.write(pdf)
    with open(os.path.join(pdir, "main_flat.tex"), "w", encoding="utf-8") as f:
        f.write(flat)
    with open(os.path.join(pdir, "structured.json"), "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    meta = {"arxiv_id": cand["id_v"], "title": cand["title"], "authors": cand["authors"],
            "published": cand["published"], "discipline": disc, "field": field,
            "arxiv_category": cat, "main_tex": main, "n_source_files": len(files),
            "pdf_bytes": len(pdf), **s, "source_type": "arxiv_latex"}
    with open(os.path.join(pdir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    return meta


def _rmtree(p):
    if not os.path.isdir(p):
        return
    for r, ds, fs in os.walk(p, topdown=False):
        for f in fs:
            os.remove(os.path.join(r, f))
        for d in ds:
            os.rmdir(os.path.join(r, d))
    os.rmdir(p)


def main():
    out_root = os.path.abspath(sys.argv[1])
    os.makedirs(out_root, exist_ok=True)
    manifest, used = [], set()
    for disc, field, cat, quota in PLAN:
        got, start = 0, 0
        while got < quota and start < 400:
            try:
                cands = query(cat, start)
            except Exception as e:  # noqa: BLE001
                print(f"[{cat}] 检索失败：{e}", flush=True)
                time.sleep(10)
                start += 50
                continue
            time.sleep(3)
            if not cands:
                break
            for c in cands:
                if got >= quota:
                    break
                if c["primary"] != cat or c["id"] in used or "withdrawn" in (c["comment"] or "").lower():
                    continue
                try:
                    meta = process(c, disc, field, cat, out_root)
                except Exception as e:  # noqa: BLE001
                    print(f"[{cat}] {c['id']} 下载失败：{e}", flush=True)
                    continue
                if meta:
                    used.add(c["id"])
                    manifest.append(meta)
                    got += 1
                    print(f"[{cat}] {got}/{quota} {c['id']} 图={meta['n_figures']} "
                          f"表={meta['n_tables']} 公式={meta['n_equations']}", flush=True)
            start += 50
        if got < quota:
            print(f"!! [{cat}] 只下载到 {got}/{quota} 篇", flush=True)
    keys = ["discipline", "field", "arxiv_category", "arxiv_id", "title", "published",
            "main_tex", "n_sections", "n_figures", "n_tables", "n_equations", "n_chars",
            "n_source_files", "pdf_bytes", "source_type"]
    with open(os.path.join(out_root, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(manifest)
    print(f"完成，本次共 {len(manifest)} 篇", flush=True)


if __name__ == "__main__":
    main()
