#!/usr/bin/env python3
"""extract_pdf.py — 把 PDF 书籍按书签目录拆成「每章一个文本文件」+ manifest.json

用法:
  python3 extract_pdf.py <book.pdf> [-o OUTDIR] [--min-pages N] [--part-regex REGEX]

输出:
  OUTDIR/ch01.txt … chNN.txt   每章全文,页首带 [pN] 页码标记
  OUTDIR/../manifest.json      章号/标题/所属部分/页码范围/字数(供后续规划页数与派发)

设计要点(来自实战):
  - 依赖 PDF 书签(outline);无书签的书先用 --min-pages 0 查看整书,再手工分章。
  - 深度 0 且匹配 --part-regex 的书签视为「部分」(如 "I 基础"),其子书签为章;
    其余深度 0 书签直接作为章(前言/附录等前置材料)。
  - 章的结束页 = 下一个书签的起始页,最后一章到书尾。
依赖: pip3 install pypdf  (或 PyPDF2)。fontTools 缺失的告警可忽略。
"""
import argparse
import json
import logging
import os
import re
import sys

logging.getLogger("pypdf").setLevel(logging.ERROR)

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:
        sys.exit("需要 pypdf:pip3 install pypdf")


def flatten_outline(reader):
    flat = []

    def walk(items, depth):
        for it in items:
            if isinstance(it, list):
                walk(it, depth + 1)
            else:
                try:
                    pg = reader.get_destination_page_number(it)
                except Exception:
                    pg = None
                flat.append({"depth": depth, "title": str(it.title).strip(), "page": pg})

    try:
        walk(reader.outline, 0)
    except Exception as e:
        sys.exit(f"PDF 无书签或书签不可读({e});请先为 PDF 添加书签再运行。")
    return flat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("-o", "--outdir", default="work/text")
    ap.add_argument("--min-pages", type=int, default=0,
                    help="页数少于此值的章仍提取,但在 manifest 标记 tiny(通常跳过不做页)")
    ap.add_argument("--part-regex", default=r"^(I|II|III|IV|V|VI|VII|VIII|IX|X)\s",
                    help="识别「部分」级书签的正则(默认罗马数字前缀)")
    args = ap.parse_args()

    part_re = re.compile(args.part_regex)
    os.makedirs(args.outdir, exist_ok=True)

    reader = PdfReader(args.pdf)
    n = len(reader.pages)
    flat = [f for f in flatten_outline(reader) if f["page"] is not None]

    entries, cur_part = [], None
    for it in flat:
        if it["depth"] == 0:
            if part_re.match(it["title"]):
                cur_part = it["title"]
                entries.append({"kind": "part", "part": cur_part,
                                "title": it["title"], "start": it["page"]})
            else:
                entries.append({"kind": "chapter", "part": None,
                                "title": it["title"], "start": it["page"]})
        elif it["depth"] == 1 and cur_part:
            entries.append({"kind": "chapter", "part": cur_part,
                            "title": it["title"], "start": it["page"]})

    for i, e in enumerate(entries):
        e["end"] = entries[i + 1]["start"] if i + 1 < len(entries) else n

    manifest, chap_no = [], 0
    for e in entries:
        if e["kind"] != "chapter":
            continue
        chap_no += 1
        pages = []
        for p in range(e["start"], min(e["end"], n)):
            try:
                t = reader.pages[p].extract_text() or ""
            except Exception:
                t = ""
            pages.append(f"[p{p + 1}]\n{t}")
        text = "\n".join(pages)
        fname = f"ch{chap_no:02d}.txt"
        with open(os.path.join(args.outdir, fname), "w", encoding="utf-8") as f:
            f.write(text)
        manifest.append({
            "no": chap_no, "file": fname, "title": e["title"], "part": e["part"],
            "start": e["start"] + 1, "end": e["end"], "pages": e["end"] - e["start"],
            "chars": len(text), "tiny": (e["end"] - e["start"]) < args.min_pages,
        })

    manifest_path = os.path.join(os.path.dirname(args.outdir.rstrip("/")) or ".", "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print(f"书:{args.pdf} · {n} 页 · {chap_no} 章 → {args.outdir}/ + {manifest_path}\n")
    for m in manifest:
        flag = " (tiny,建议跳过)" if m["tiny"] else ""
        print(f"ch{m['no']:02d} p{m['start']}-{m['end']} ({m['pages']:>3}p, {m['chars']:>6}字) "
              f"[{m['part'] or '—'}] {m['title']}{flag}")


if __name__ == "__main__":
    main()
