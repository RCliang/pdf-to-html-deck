#!/usr/bin/env python3
"""生成 test/fixture.pdf —— 6 页 ASCII 文本 + 书签结构:

    Preface          (顶级,第 1 页)
    I Basics         (顶级"部分",匹配默认 --part-regex)
      Chapter One    (子级,第 3 页)
      Chapter Two    (子级,第 5 页)

纯标准库手写 PDF(xref 逐对象计偏移);产物已入库,一般无需重跑。
用法: python3 test/make_fixture.py [输出路径]
"""
import sys

PAGES = 6
TEXTS = [
    "Preface page one. Fixture deck for smoke tests. Lorem ipsum line A.",
    "Preface page two. Second page of front matter. Lorem ipsum line B.",
    "Chapter One page one. Body text for the first chapter. Lorem ipsum line C.",
    "Chapter One page two. More body text. Lorem ipsum line D.",
    "Chapter Two page one. Body text for the second chapter. Lorem ipsum line E.",
    "Chapter Two page two. The final fixture page. Lorem ipsum line F.",
]


def content(text):
    return (f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET\n").encode("latin-1")


def build():
    # 对象编号:1 Catalog · 2 Pages · 3-8 Page · 9 Font · 10 Outlines · 11-14 条目 · 15-20 内容流
    out = bytearray(b"%PDF-1.4\n")
    offsets = {}

    def add(num, body):
        offsets[num] = len(out)
        out.extend(f"{num} 0 obj\n".encode())
        out.extend(body)
        out.extend(b"\nendobj\n")

    kids = " ".join(f"{3 + i} 0 R" for i in range(PAGES))
    add(1, f"<< /Type /Catalog /Pages 2 0 R /Outlines 10 0 R >>".encode())
    add(2, f"<< /Type /Pages /Kids [{kids}] /Count {PAGES} >>".encode())
    for i in range(PAGES):
        add(3 + i, (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << /F1 9 0 R >> >> /Contents {15 + i} 0 R >>").encode())
    add(9, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add(10, b"<< /Type /Outlines /First 11 0 R /Last 12 0 R /Count 4 >>")
    # 11 Preface(顶级章)→ 第1页(obj 3);12 I Basics(部分)→ 第3页(obj 5)
    add(11, b"<< /Title (Preface) /Parent 10 0 R /Next 12 0 R /Dest [3 0 R /XYZ null null null] >>")
    add(12, (b"<< /Title (I Basics) /Parent 10 0 R /Prev 11 0 R /First 13 0 R /Last 14 0 R "
             b"/Count 2 /Dest [5 0 R /XYZ null null null] >>"))
    add(13, b"<< /Title (Chapter One) /Parent 12 0 R /Next 14 0 R /Dest [5 0 R /XYZ null null null] >>")
    add(14, b"<< /Title (Chapter Two) /Parent 12 0 R /Prev 13 0 R /Dest [7 0 R /XYZ null null null] >>")
    for i, text in enumerate(TEXTS):
        body = content(text)
        add(15 + i, b"<< /Length %d >>\nstream\n" % len(body) + body + b"endstream")

    size = 15 + PAGES
    xref_at = len(out)
    out.extend(f"xref\n0 {size}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for num in range(1, size):
        out.extend(f"{offsets[num]:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode())
    return bytes(out)


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "test/fixture.pdf"
    with open(dest, "wb") as f:
        f.write(build())
    print(f"fixture written: {dest} ({len(build())} bytes header calc)")
