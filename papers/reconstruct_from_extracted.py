from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from dataclasses import dataclass

from translate_paper_tex import ArgosDirectEngine


ROOT = pathlib.Path(__file__).resolve().parent
OUTPUT_DIR = "translation_latex"

TITLE_BY_PAPER = {
    "DriveDreamer": "DriveDreamer: Towards Real-world-driven World Models for Autonomous Driving",
    "Genie": "Genie: Generative Interactive Environments",
    "TD-MPC": "Temporal Difference Learning for Model Predictive Control",
}


@dataclass
class Stats:
    translated: int = 0
    cache_hits: int = 0
    preserved: int = 0
    headings: int = 0


class CachedArgos:
    def __init__(self, cache_path: pathlib.Path):
        self.engine = ArgosDirectEngine()
        self.cache_path = cache_path
        if cache_path.exists():
            self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            self.cache = {}
        self.stats = Stats()

    def save(self) -> None:
        self.cache_path.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def translate(self, text: str) -> str:
        normalized = normalize_space(text)
        if not normalized:
            return ""
        if normalized in self.cache:
            self.stats.cache_hits += 1
            return self.cache[normalized]
        translated = self.engine.translate(normalized)
        self.cache[normalized] = translated
        self.stats.translated += 1
        if self.stats.translated % 25 == 0:
            self.save()
        return translated


def normalize_space(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def escape_latex(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def clean_lines(raw: str) -> list[str]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    raw = raw.replace("\f", "\n\n")
    lines: list[str] = []
    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        if stripped in {"Proprietary + Confidential"}:
            continue
        lines.append(stripped)
    return lines


def paragraph_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        if not line:
            if current:
                blocks.append(" ".join(current))
                current = []
            continue
        if is_heading(line):
            if current:
                blocks.append(" ".join(current))
                current = []
            blocks.append(line)
            continue
        current.append(line)
        if len(" ".join(current)) > 1200:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def is_heading(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) > 100:
        return False
    if stripped.lower() in {
        "abstract",
        "references",
        "acknowledgements",
        "acknowledgments",
        "appendix",
    }:
        return True
    if re.match(r"^\d+(\.\d+)*\.?\s+[A-Z][A-Za-z0-9 ,:/()\-–]+$", stripped):
        return True
    if re.match(r"^[A-Z][A-Za-z0-9 ,:/()\-–]{3,}$", stripped) and not stripped.endswith("."):
        words = stripped.split()
        return len(words) <= 8
    return False


def heading_level(text: str) -> str:
    stripped = text.strip()
    if stripped.lower() in {"abstract", "references", "acknowledgements", "acknowledgments", "appendix"}:
        return "section*"
    match = re.match(r"^(\d+(?:\.\d+)*)", stripped)
    if not match:
        return "section*"
    depth = match.group(1).count(".")
    return "section" if depth == 0 else "subsection" if depth == 1 else "subsubsection"


def should_translate(text: str) -> bool:
    letters = len(re.findall(r"[A-Za-z]", text))
    if letters < 8:
        return False
    symbols = len(re.findall(r"[=<>|{}^_\\]", text))
    return symbols / max(1, len(text)) < 0.12


def render_block(block: str, translator: CachedArgos, in_references: bool) -> tuple[str, bool]:
    if is_heading(block):
        translator.stats.headings += 1
        level = heading_level(block)
        heading_text = re.sub(r"^\d+(\.\d+)*\.?\s+", "", block).strip()
        translated = translator.translate(heading_text) if should_translate(heading_text) else heading_text
        is_refs = heading_text.lower() == "references"
        return f"\\{level}{{{escape_latex(translated)}}}\n", is_refs

    if in_references or not should_translate(block):
        translator.stats.preserved += 1
        return escape_latex(normalize_space(block)) + "\n\n", in_references

    translated = translator.translate(block)
    return escape_latex(translated) + "\n\n", in_references


def build_tex(name: str, blocks: list[str], translator: CachedArgos) -> str:
    title = TITLE_BY_PAPER.get(name, name)
    body: list[str] = []
    in_references = False
    for block in blocks:
        rendered, entered_refs = render_block(block, translator, in_references)
        body.append(rendered)
        in_references = in_references or entered_refs

    return rf"""\documentclass[10pt]{{article}}
\usepackage[a4paper,margin=1in]{{geometry}}
\usepackage{{xeCJK}}
\setCJKmainfont{{FandolSong-Regular.otf}}[ItalicFont=FandolKai-Regular.otf]
\setCJKsansfont{{FandolHei-Regular.otf}}
\setCJKmonofont{{FandolFang-Regular.otf}}
\usepackage{{hyperref}}
\usepackage{{enumitem}}
\setlist{{nosep,leftmargin=1.5em}}
\hypersetup{{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt
\setlength{{\parindent}}{{2em}}
\setlength{{\parskip}}{{0.35em}}
\emergencystretch=3em
\sloppy

\title{{{escape_latex(title)}\\[0.5em]\large 中文重构译文}}
\author{{Argos Translate 本地翻译}}
\date{{}}

\begin{{document}}
\maketitle

\noindent\textbf{{说明：}} 本文档由 PDF 抽取文本重构生成，用于在缺少可用 arXiv LaTeX 源码时备份中文译文。章节和段落为自动恢复，图表、公式和双栏排版未按原始论文完整复刻。

\bigskip

{''.join(body)}

\end{{document}}
"""


def reconstruct(name: str, force: bool = False) -> dict:
    paper_dir = ROOT / name
    extracted = paper_dir / "extracted.txt"
    if not extracted.exists():
        raise FileNotFoundError(extracted)

    output_dir = paper_dir / OUTPUT_DIR
    if output_dir.exists() and force:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    translator = CachedArgos(paper_dir / "translation_cache_argos_reconstruct.json")
    raw = extracted.read_text(encoding="utf-8", errors="replace")
    blocks = paragraph_blocks(clean_lines(raw))
    tex = build_tex(name, blocks, translator)
    (output_dir / "main.tex").write_text(tex, encoding="utf-8", newline="")
    translator.save()

    status = {
        "paper": name,
        "mode": "reconstructed_from_extracted_txt",
        "blocks": len(blocks),
        "stats": translator.stats.__dict__,
        "output": str(output_dir / "main.tex"),
    }
    (paper_dir / "reconstruction_status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct translated LaTeX from extracted PDF text.")
    parser.add_argument("papers", nargs="+")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for name in args.papers:
        status = reconstruct(name, force=args.force)
        print(json.dumps(status, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
