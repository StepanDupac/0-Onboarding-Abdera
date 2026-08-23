"""Build Quant_Research_Handbook.pdf from docs/, figures/ and the logo.

Self-contained: a small Markdown-to-HTML converter for the subset used in docs/, matplotlib for
real mathematical typesetting, and headless Chrome for the print. No pandoc, no LaTeX install.

    python3 .source/make_figures.py
    python3 .source/build_pdf.py
"""
from __future__ import annotations

import base64
import hashlib
import html
import re
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
PACK = SOURCE.parent
DOCS = SOURCE / "docs"
FIGURES = SOURCE / "figures"
EQUATIONS = FIGURES / "equations"
LOGO = SOURCE / "abdera-logo-v1.png"
OUTPUT = PACK / "Quant_Research_Handbook.pdf"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

FIRM = "Abdera Trading"
TITLE = "Quantitative Research"
SUBTITLE = "What the work looks like, told through one real day of it"
PACK_ID = "ABD-ONB-R1"

INK = "#14161a"
CREAM = "#f4efe4"
ACCENT = "#b8894a"
BLUE = "#2f5d78"
MUTED = "#5b6570"
RULE = "#dde1e6"
COVER_BG = "#090908"   # sampled from the logo so the mark blends into the page


def render_equation(latex: str, display: bool = True) -> Path:
    """Typeset one LaTeX expression to SVG with matplotlib's mathtext."""
    EQUATIONS.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256((latex + str(display)).encode("utf-8")).hexdigest()[:16]
    path = EQUATIONS / f"eq_{digest}.svg"
    if path.exists():
        return path
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"mathtext.fontset": "cm", "svg.fonttype": "path"})
    try:
        from matplotlib import mathtext
        mathtext.MathTextParser("path").parse(f"${latex}$", 72, None)
    except Exception as error:
        raise SystemExit(
            f"cannot typeset this expression:\n  {latex}\n{error}\n"
            "matplotlib mathtext covers most of LaTeX but not all of it; "
            "\\tfrac is one known gap."
        ) from None
    figure = plt.figure(figsize=(6.6, 0.9))
    figure.text(0.5, 0.5, f"${latex}$", ha="center", va="center",
                fontsize=16 if display else 13, color=INK)
    figure.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.05, transparent=True)
    plt.close(figure)
    return path


def embed_svg(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text[text.index("<svg"):]
    return re.sub(r'\swidth="[^"]*"|\sheight="[^"]*"', "", text, count=2)


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return text


def convert(markdown: str) -> str:
    out: list[str] = []
    lines = markdown.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]

        figure = re.match(r"^!\[([a-z_]+)\]\(Figure: (.+)\)$", line.strip())
        if figure:
            name, caption = figure.group(1), figure.group(2)
            source = FIGURES / f"{name}.svg"
            if source.exists():
                out.append(
                    f'<figure>{embed_svg(source)}'
                    f'<figcaption>{inline(caption)}</figcaption></figure>'
                )
            index += 1
            continue

        if line.startswith("```"):
            language = line[3:].strip()
            block = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            if language in ("math", "mathbox"):
                svg = embed_svg(render_equation(" ".join(b.strip() for b in block)))
                css = "equation boxed" if language == "mathbox" else "equation"
                out.append(f'<div class="{css}">{svg}</div>')
            else:
                body = "\n".join(html.escape(b) for b in block)
                out.append(f"<pre><code>{body}</code></pre>")
            continue

        if line.startswith("|") and index + 1 < len(lines) and set(lines[index + 1].strip()) <= set("|-: "):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            index += 2
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                rows.append([c.strip() for c in lines[index].strip().strip("|").split("|")])
                index += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in header)
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>"
                           for row in rows)
            out.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
            continue

        if re.match(r"^#{1,6} ", line):
            level = len(line) - len(line.lstrip("#"))
            out.append(f"<h{level}>{inline(line[level:].strip())}</h{level}>")
            index += 1
            continue

        if line.startswith(">"):
            block = []
            while index < len(lines) and lines[index].startswith(">"):
                block.append(lines[index].lstrip("> ").rstrip())
                index += 1
            out.append("<blockquote>" + inline(" ".join(block)) + "</blockquote>")
            continue

        if re.match(r"^\s*[-*] ", line) or re.match(r"^\s*\d+\. ", line):
            ordered = bool(re.match(r"^\s*\d+\. ", line))
            items: list[str] = []
            while index < len(lines) and (
                re.match(r"^\s*[-*] ", lines[index]) or re.match(r"^\s*\d+\. ", lines[index])
                or (items and lines[index].startswith("  ") and lines[index].strip())
            ):
                current = lines[index]
                if re.match(r"^\s*[-*] ", current) or re.match(r"^\s*\d+\. ", current):
                    items.append(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", current))
                else:
                    items[-1] += " " + current.strip()
                index += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            continue

        if line.strip() == "---":
            out.append("<hr>")
            index += 1
            continue

        if not line.strip():
            index += 1
            continue

        block = []
        while index < len(lines) and lines[index].strip() and not re.match(
            r"^(#{1,6} |\||```|>|\s*[-*] |\s*\d+\. |!\[|---$)", lines[index]
        ):
            block.append(lines[index].strip())
            index += 1
        out.append("<p>" + inline(" ".join(block)) + "</p>")

    return "\n".join(out)


CSS = f"""
@page {{ size: A4; margin: 19mm 17mm 17mm; }}
@page :first {{ margin: 0; }}
body {{ margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact;
        font-family: "Charter","Georgia",serif; font-size: 10.5pt; line-height: 1.52; color: {INK}; }}

h1 {{ font-size: 18pt; margin: 0 0 12pt; padding: 0 0 7pt; color: {INK};
      border-bottom: 2.5px solid {ACCENT}; page-break-before: always; page-break-after: avoid; }}
h1:first-of-type {{ page-break-before: avoid; }}
h2 {{ font-size: 13.5pt; margin: 19pt 0 6pt; color: {BLUE}; page-break-after: avoid; }}
h3 {{ font-size: 11pt; margin: 14pt 0 4pt; color: {INK}; page-break-after: avoid; }}
p {{ margin: 0 0 7pt; text-align: justify; hyphens: auto; }}

code {{ font-family: "SF Mono","Menlo",monospace; font-size: 8.8pt; background: #f1f3f5;
        color: #33383f; padding: 1px 3.5px; border-radius: 2.5px; }}
pre {{ background: #fbfbfa; border: 1px solid {RULE}; border-left: 3px solid {BLUE};
       padding: 8pt 10pt; margin: 9pt 0; page-break-inside: avoid; overflow-x: auto; }}
pre code {{ background: none; padding: 0; font-size: 8.4pt; line-height: 1.42; color: #2a2f36; }}

.equation {{ text-align: center; margin: 11pt 0; page-break-inside: avoid; }}
.equation svg {{ height: 34px; }}
.equation.boxed {{ background: {CREAM}; border: 1px solid {ACCENT}; border-radius: 4px;
                   padding: 9pt 6pt; margin: 13pt 0; }}
.equation.boxed svg {{ height: 38px; }}

table {{ border-collapse: collapse; width: 100%; margin: 9pt 0; font-size: 9.3pt;
         page-break-inside: avoid; }}
th {{ background: {INK}; color: {CREAM}; text-align: left; padding: 4.5pt 6pt; font-weight: 600; }}
td {{ padding: 4pt 6pt; border-bottom: 1px solid {RULE}; vertical-align: top; }}
tbody tr:nth-child(even) {{ background: #fafbfc; }}

blockquote {{ margin: 10pt 0; padding: 8pt 12pt; background: {CREAM};
              border-left: 3px solid {ACCENT}; page-break-inside: avoid; }}
blockquote p {{ margin: 0; }}

figure {{ margin: 12pt 0; page-break-inside: avoid; text-align: center; }}
figure svg {{ width: 100%; max-width: 460pt; height: auto; }}
figcaption {{ font-size: 8.4pt; color: {MUTED}; margin-top: 4pt; font-style: italic; }}

ul, ol {{ margin: 0 0 7pt; padding-left: 19pt; }}
li {{ margin: 0 0 2.5pt; }}
hr {{ border: none; border-top: 1px solid {RULE}; margin: 13pt 0; }}
strong {{ font-weight: 600; }}

.cover {{ background: {COVER_BG}; color: {CREAM}; padding: 150pt 60pt 0;
          height: 297mm; width: 210mm; box-sizing: border-box; text-align: center;
          page-break-after: always; }}
.cover img {{ width: 190pt; margin-bottom: 6pt; }}
.cover .firm {{ font-size: 10.5pt; letter-spacing: 5px; color: {ACCENT}; margin-bottom: 26pt; }}
.cover .divider {{ width: 54pt; height: 1.5px; background: {ACCENT}; margin: 0 auto 26pt; }}
.cover h1 {{ font-size: 30pt; border: none; color: {CREAM}; margin: 0 0 12pt;
             page-break-before: avoid; padding: 0; }}
.cover .sub {{ font-size: 12.5pt; font-style: italic; color: #b9bec6; margin-bottom: 44pt; }}
.cover .note {{ font-size: 9.8pt; color: #9aa1aa; max-width: 350pt; margin: 0 auto;
                text-align: left; line-height: 1.6; }}
.cover .note strong {{ color: {CREAM}; }}
.cover .packid {{ margin-top: 40pt; font-size: 8.5pt; letter-spacing: 2.5px; color: #6c7480; }}

.toc {{ page-break-after: always; }}
.toc h1 {{ page-break-before: avoid; }}
.toc td:first-child {{ color: {ACCENT}; font-weight: 600; width: 34pt; }}
"""


def main() -> int:
    if not FIGURES.exists():
        print("run: python3 .source/make_figures.py", file=sys.stderr)
        return 1

    cover = (
        f'<div class="cover">'
        f'<img src="{data_uri(LOGO)}" alt="">'
        f'<div class="divider"></div>'
        f"<h1>{TITLE}</h1><div class='sub'>{SUBTITLE}</div>"
        "<div class='note'><p>This pack walks through one complete day of quantitative research: "
        "a hypothesis taken from the literature to a measured verdict, and a deliverable shipped."
        "</p><p><strong>The headline idea died. The thing that shipped came from somewhere "
        "else.</strong> That is the ordinary shape of the work, which is why this is the pack we "
        "send rather than a success story.</p>"
        "<p>Companion code, figures and a candidate exercise accompany this document.</p>"
        f"</div><div class='packid'>{PACK_ID}</div></div>"
    )

    sources = sorted(DOCS.glob("*.md"))
    toc = ['<div class="toc"><h1>Contents</h1><table><tbody>']
    for path in sources:
        heading = path.read_text(encoding="utf-8").split("\n", 1)[0].lstrip("# ").strip()
        number, _, title = heading.partition(". ")
        toc.append(f"<tr><td>{html.escape(number)}</td><td>{html.escape(title or heading)}</td></tr>")
    toc.append("</tbody></table></div>")

    parts = [cover, "\n".join(toc)]
    for path in sources:
        parts.append(convert(path.read_text(encoding="utf-8")))

    document = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{FIRM} — {TITLE}</title><style>{CSS}</style></head><body>"
        + "\n".join(parts) + "</body></html>"
    )
    scratch = SOURCE / ".handbook.html"
    scratch.write_text(document, encoding="utf-8")

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={OUTPUT}", str(scratch)],
        check=True, capture_output=True,
    )
    scratch.unlink()
    print(f"wrote {OUTPUT.name} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
