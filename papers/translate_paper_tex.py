from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import time
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parent
SOURCE_DIR_CANDIDATES = ("source_clean", "source")
OUTPUT_DIR = "translation_latex"
CACHE_NAMES = {
    "argos": "translation_cache_argos.json",
    "mymemory": "translation_cache_mymemory.json",
}
STATUS_NAME = "translation_status.json"
PLACEHOLDER_RE = r"ZZXPH\d{4}XZZ"

VISIBLE_COMMANDS = {
    "title",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "subparagraph",
    "caption",
    "itempar",
    "textbf",
    "textit",
    "emph",
    "thanks",
    "footnote",
    "Comment",
    "makebox",
}

TRANSLATE_ENVIRONMENTS = {
    "abstract",
    "algorithm",
    "itemize",
    "enumerate",
    "figure",
    "figure*",
    "table",
    "table*",
    "minipage",
    "wrapfigure",
    "tabular",
    "tabularx",
}

PROTECTED_COMMAND_BLOCKS = {
    "hypersetup",
    "lstset",
    "tikzset",
    "pgfplotsset",
    "captionsetup",
    "setminted",
}

PROTECTED_BEGIN_LINES = {
    "tcolorbox",
}

PROTECTED_ENVIRONMENTS = {
    "equation",
    "equation*",
    "align",
    "align*",
    "alignat",
    "alignat*",
    "gather",
    "gather*",
    "multline",
    "multline*",
    "split",
    "tikzpicture",
    "axis",
    "lstlisting",
    "verbatim",
    "minted",
}

NAMED_TERMS = [
    "DreamerV4",
    "DreamerV3",
    "DreamerV2",
    "DriveDreamer",
    "World Models",
    "World Model",
    "DeepMind Control Suite",
    "TensorFlow Probability",
    "DeepMind Lab",
    "Dreamer",
    "PlaNet",
    "MuZero",
    "TD-MPC",
    "GAIA",
    "Genie",
    "Atari",
    "D4PG",
    "A3C",
    "PPO",
    "DDPG",
    "SAC",
    "DQN",
    "Rainbow",
    "SimPLe",
    "RSSM",
    "CNN",
    "POMDP",
    "MDP",
    "ELBO",
    "VIB",
    "NCE",
]

POST_REPLACEMENTS = {
    "梦想家": "Dreamer",
    "梦想控制:学习行为": "梦中控制：学习行为",
    "由后人想象": "通过潜在想象",
    "普拉内特": "PlaNet",
    "普拉Net": "PlaNet",
    "穆Zero": "MuZero",
    "潜伏": "潜在",
    "远景行为": "长时程行为",
    "长视野行为": "长时程行为",
    "长地平线": "长时程",
    "地平线": "时域",
    "行动模型": "动作模型",
    "行动": "动作",
    "价值模型": "值函数模型",
    "价值估计": "值估计",
    "价值": "值",
    "数据效率": "数据效率",
    "世界模式": "世界模型",
    "模型状态": "模型状态",
    "表示学习": "表征学习",
    "表示模型": "表征模型",
    "表示&": "表征&",
    "代表性学习": "表征学习",
    "代表权": "表征",
    "过渡": "转移",
    "环境互动": "环境交互",
    "基因-环境相互作用": "环境交互",
    "探测噪声": "探索噪声",
    "探索噪音": "探索噪声",
    "随机种子剧集": "随机种子回合",
    "种子剧集": "种子回合",
    "随机种子事件": "随机种子回合",
    "种子事件": "种子回合",
    "剧集": "回合",
    "事件": "回合",
    "粒种子": "个随机种子",
    "无型号": "无模型",
    "无模型剂": "无模型智能体",
    "D4PGZ": "D4PG",
    "视距行为": "长时程行为",
    "想象视野": "想象时域",
    "不对称性能": "渐近性能",
    "业绩": "性能",
    "强化学习代理": "强化学习智能体",
    "代理": "智能体",
}


@dataclass
class TranslationStats:
    translated_segments: int = 0
    cache_hits: int = 0
    failures: int = 0
    skipped_files: int = 0
    translated_files: int = 0


class MyMemoryEngine:
    def __init__(self, delay: float = 3.0, retries: int = 5):
        deps = pathlib.Path(r"D:\gameWorld\.deep_translator_deps")
        if deps.exists():
            sys.path.insert(0, str(deps))
        from deep_translator import MyMemoryTranslator

        self.translator = MyMemoryTranslator(source="en-US", target="zh-CN")
        self.delay = delay
        self.retries = retries

    def translate(self, text: str) -> str:
        for attempt in range(1, self.retries + 1):
            try:
                translated = self.translator.translate(text)
                time.sleep(self.delay)
                return translated
            except Exception as exc:
                if attempt == self.retries:
                    raise
                message = str(exc).lower()
                if "too many requests" in message or "429" in message:
                    time.sleep(60.0 * attempt)
                else:
                    time.sleep(2.0 * attempt)


class ArgosDirectEngine:
    def __init__(self):
        deps = pathlib.Path(r"D:\gameWorld\.argos_translate_deps")
        if deps.exists():
            sys.path.insert(0, str(deps))
        import ctranslate2
        from argostranslate import package, settings

        self.package = self.find_or_install_package(package)
        model_path = str(self.package.package_path / "model")
        self.settings = settings
        self.translator = ctranslate2.Translator(
            model_path,
            device=settings.device,
            inter_threads=settings.inter_threads,
            intra_threads=settings.intra_threads,
            compute_type=settings.compute_type,
        )

    @staticmethod
    def find_or_install_package(package_module):
        packages = [
            pkg
            for pkg in package_module.get_installed_packages()
            if pkg.from_code == "en" and pkg.to_code == "zh"
        ]
        if packages:
            return packages[0]

        model_path = pathlib.Path(
            r"C:\Users\cWX1444846\.local\cache\argos-translate\downloads\translate-en_zh.argosmodel"
        )
        if model_path.exists():
            package_module.install_from_path(model_path)
            packages = [
                pkg
                for pkg in package_module.get_installed_packages()
                if pkg.from_code == "en" and pkg.to_code == "zh"
            ]
            if packages:
                return packages[0]
        raise RuntimeError("Argos en->zh model is not installed.")

    def translate(self, text: str) -> str:
        sentences = split_for_argos(text)
        if not sentences:
            return text
        tokenized = [self.package.tokenizer.encode(sentence) for sentence in sentences]
        target_prefix = None
        if self.package.target_prefix != "":
            target_prefix = [[self.package.target_prefix]] * len(tokenized)
        translated_batches = self.translator.translate_batch(
            tokenized,
            target_prefix=target_prefix,
            replace_unknowns=True,
            max_batch_size=self.settings.batch_size,
            batch_type="tokens",
            beam_size=max(1, self.settings.beam_size),
            num_hypotheses=1,
            length_penalty=0.2,
            return_scores=False,
        )
        pieces: list[str] = []
        for translated_batch in translated_batches:
            value = self.package.tokenizer.decode(translated_batch.hypotheses[0])
            if self.package.target_prefix != "" and value.startswith(self.package.target_prefix):
                value = value[len(self.package.target_prefix) :]
            pieces.append(value.lstrip())
        return "".join(pieces)


class SegmentTranslator:
    def __init__(self, cache_path: pathlib.Path, backend: str = "argos"):
        self.backend = backend
        if backend == "argos":
            self.engine = ArgosDirectEngine()
        elif backend == "mymemory":
            self.engine = MyMemoryEngine()
        else:
            raise ValueError(f"Unknown translation backend: {backend}")
        self.cache_path = cache_path
        self.stats = TranslationStats()
        if cache_path.exists():
            self.cache = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            self.cache = {}

    def save_cache(self) -> None:
        temp = self.cache_path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.cache_path)

    def translate(self, text: str) -> str:
        if not should_translate(text):
            return text
        chunks = split_for_translation(text)
        translated_chunks = [self.translate_chunk(chunk) for chunk in chunks]
        sep = "" if self.backend == "argos" else " "
        return postprocess_translation(sep.join(part for part in translated_chunks if part))

    def translate_chunk(self, text: str) -> str:
        if not should_translate(text):
            return text
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key in self.cache:
            cached = self.cache[key]
            if cached != text:
                self.stats.cache_hits += 1
                if self.backend == "argos":
                    cached = sanitize_argos_output(cached)
                return postprocess_translation(cached)
        try:
            if self.backend == "argos":
                translated = self.translate_with_placeholders_preserved(text)
                translated = sanitize_argos_output(translated)
            else:
                translated = self.engine.translate(text)
            translated = postprocess_translation(translated)
            self.cache[key] = translated
            self.stats.translated_segments += 1
            return translated
        except Exception as exc:
            self.stats.failures += 1
            print(f"WARN translate failed: {type(exc).__name__}: {exc}", flush=True)
            return text
        return text

    def translate_with_placeholders_preserved(self, text: str) -> str:
        parts = re.split(rf"({PLACEHOLDER_RE})", text)
        translated_parts: list[str] = []
        for part in parts:
            if not part:
                continue
            if re.fullmatch(PLACEHOLDER_RE, part):
                translated_parts.append(part)
            elif should_translate(part):
                translated_parts.append(self.engine.translate(part))
            else:
                translated_parts.append(part)
        return "".join(translated_parts)


def sanitize_argos_output(text: str) -> str:
    # Argos may hallucinate TeX-structural braces/brackets in plain text.
    # Real LaTeX commands and math are protected as placeholders before this runs.
    return text.replace("{", "").replace("}", "").replace("[", "").replace("]", "")


def should_translate(text: str) -> bool:
    visible = re.sub(PLACEHOLDER_RE, "", text)
    return bool(re.search(r"[A-Za-z]{3,}", visible))


def split_for_translation(text: str, max_chars: int = 470) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= max_chars:
        return [text]

    pieces = re.split(r"(?<=[.!?;:])\s+", text)
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if not piece:
            continue
        candidate = f"{current} {piece}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(piece) <= max_chars:
            current = piece
        else:
            chunks.extend(split_long_piece(piece, max_chars=max_chars))
            current = ""
    if current:
        chunks.append(current)
    return chunks


def split_for_argos(text: str, max_chars: int = 260) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []
    pieces = re.split(r"(?<=[.!?;:])\s+", text)
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if not piece:
            continue
        candidate = f"{current} {piece}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(piece) <= max_chars:
            current = piece
        else:
            chunks.extend(split_long_piece(piece, max_chars=max_chars))
            current = ""
    if current:
        chunks.append(current)
    return chunks


def split_long_piece(text: str, max_chars: int) -> list[str]:
    words = text.split(" ")
    chunks: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = word
    if current:
        chunks.append(current)
    return chunks


def postprocess_translation(text: str) -> str:
    result = text
    for source, target in POST_REPLACEMENTS.items():
        result = result.replace(source, target)
    result = result.replace(" ,", "，").replace(" .", "。")
    result = separate_latex_commands_from_cjk(result)
    return result


def separate_latex_commands_from_cjk(text: str) -> str:
    # xeCJK treats CJK characters as letters, so \macro中文 can be parsed
    # as a single undefined control sequence. Insert an empty group boundary.
    return re.sub(r"\\([A-Za-z]+)(?=[\u3400-\u9fff])", r"\\\1{}", text)


def load_text(path: pathlib.Path) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def save_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def find_main_tex(source_dir: pathlib.Path) -> pathlib.Path:
    candidates = []
    for path in source_dir.rglob("*.tex"):
        text = load_text(path)
        if "\\documentclass" in text:
            candidates.append(path)
    if candidates:
        return sorted(candidates, key=lambda p: (p.name != "main.tex", len(str(p))))[0]
    main = source_dir / "main.tex"
    if main.exists():
        return main
    tex_files = sorted(source_dir.rglob("*.tex"))
    if not tex_files:
        raise FileNotFoundError(f"No .tex files found in {source_dir}")
    return tex_files[0]


def copy_source_tree(source_dir: pathlib.Path, output_dir: pathlib.Path, force: bool) -> None:
    if output_dir.exists():
        if not force:
            return
        if output_dir.resolve() == output_dir.parent.resolve():
            raise RuntimeError(f"Refusing to remove suspicious output path: {output_dir}")
        shutil.rmtree(output_dir)
    shutil.copytree(source_dir, output_dir)


def source_for_paper(paper_dir: pathlib.Path) -> pathlib.Path:
    for name in SOURCE_DIR_CANDIDATES:
        candidate = paper_dir / name
        if candidate.exists() and any(candidate.glob("*.tex")):
            return candidate
        if candidate.exists() and list(candidate.rglob("*.tex")):
            return candidate
    raise FileNotFoundError(f"No usable LaTeX source directory found for {paper_dir.name}")


def should_translate_file(path: pathlib.Path, main_tex: pathlib.Path) -> bool:
    rel_parts = set(path.parts)
    if path == main_tex:
        return True
    if "sections" in rel_parts or "figures" in rel_parts or "tables" in rel_parts or "algos" in rel_parts:
        return True
    return False


def split_comment(line: str) -> tuple[str, str]:
    escaped = False
    for index, char in enumerate(line):
        if char == "\\" and not escaped:
            escaped = True
            continue
        if char == "%" and not escaped:
            return line[:index], line[index:]
        escaped = False
    return line, ""


def translate_tex_content(text: str, translator: SegmentTranslator) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    protected_env: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^\s*\\author\b", line):
            block, index = collect_brace_block(lines, index)
            output.append(block)
            continue
        if protected_env is None and starts_protected_command_block(line):
            block, index = collect_brace_block(lines, index)
            output.append(block)
            continue
        if protected_env is None and starts_protected_begin_line(line):
            output.append(line)
            index += 1
            continue
        if protected_env is None and starts_table_option_block(line):
            block, index = collect_brace_block(lines, index)
            output.append(block)
            continue
        if protected_env is None and starts_multiline_visible_command(line):
            block, index = collect_brace_block(lines, index)
            output.append(translate_line(block, translator))
            continue
        env_begin = re.search(r"\\begin\{([^}]+)\}", line)
        env_end = re.search(r"\\end\{([^}]+)\}", line)
        if protected_env:
            output.append(line)
            if env_end and env_end.group(1) == protected_env:
                protected_env = None
            index += 1
            continue
        if env_begin and env_begin.group(1) in PROTECTED_ENVIRONMENTS:
            output.append(line)
            if not (env_end and env_end.group(1) == env_begin.group(1)):
                protected_env = env_begin.group(1)
            index += 1
            continue
        if line.lstrip().startswith("%"):
            output.append(line)
            index += 1
            continue
        body, comment = split_comment(line)
        translated = translate_line(body, translator)
        output.append(translated + comment)
        index += 1
    return "".join(output)


def starts_protected_command_block(line: str) -> bool:
    match = re.match(r"^\s*\\([A-Za-z]+)\*?", line)
    return bool(match and match.group(1) in PROTECTED_COMMAND_BLOCKS and brace_delta(line) > 0)


def starts_protected_begin_line(line: str) -> bool:
    match = re.match(r"^\s*\\begin\{([^}]+)\}", line)
    return bool(match and match.group(1) in PROTECTED_BEGIN_LINES)


def starts_table_option_block(line: str) -> bool:
    return bool(re.search(r"\\begin\{(?:mytabular|tblr)\}", line) and brace_delta(line) > 0)


def starts_multiline_visible_command(line: str) -> bool:
    match = re.match(r"^\s*\\([A-Za-z]+)\*?", line)
    return bool(match and match.group(1) in VISIBLE_COMMANDS and brace_delta(line) > 0)


def collect_brace_block(lines: list[str], start: int) -> tuple[str, int]:
    block = lines[start]
    balance = brace_delta(block)
    index = start + 1
    while balance > 0 and index < len(lines):
        block += lines[index]
        balance += brace_delta(lines[index])
        index += 1
    return block, index


def brace_delta(line: str) -> int:
    body, _comment = split_comment(line)
    delta = 0
    escaped = False
    for char in body:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            delta += 1
        elif char == "}":
            delta -= 1
    return delta


def translate_line(line: str, translator: SegmentTranslator) -> str:
    if not should_translate(line):
        return line
    prefix = re.match(r"^\s*", line).group(0)
    suffix = "\n" if line.endswith("\n") else ""
    core = line[len(prefix) : len(line) - len(suffix) if suffix else len(line)]
    core = translate_visible_command_args(core, translator)
    protected, placeholders = protect_latex(core)
    if not should_translate(protected):
        return prefix + restore_placeholders(protected, placeholders) + suffix
    translated = translator.translate(protected)
    restored = postprocess_translation(restore_placeholders(translated, placeholders))
    return prefix + restored + suffix


def translate_visible_command_args(text: str, translator: SegmentTranslator) -> str:
    result: list[str] = []
    i = 0
    while i < len(text):
        if text[i] != "\\":
            result.append(text[i])
            i += 1
            continue
        match = re.match(r"\\([A-Za-z]+)\*?", text[i:])
        if not match:
            result.append(text[i])
            i += 1
            continue
        name = match.group(1)
        command_end = i + len(match.group(0))
        if name not in VISIBLE_COMMANDS:
            result.append(text[i:command_end])
            i = command_end
            continue
        parsed = parse_command_first_brace(text, i)
        if parsed is None:
            result.append(text[i:command_end])
            i = command_end
            continue
        head, inner, tail_index = parsed
        inner = re.sub(r"^\s*%\s*", "", inner)
        inner = re.sub(r"(?<!\\)%[ \t]*(\r?\n)?", lambda match: match.group(1) or "", inner)
        inner_protected, placeholders = protect_latex(inner)
        translated_inner = translator.translate(inner_protected)
        result.append(head + postprocess_translation(restore_placeholders(translated_inner, placeholders)) + "}")
        i = tail_index
    return "".join(result)


def parse_command_first_brace(text: str, start: int) -> tuple[str, str, int] | None:
    match = re.match(r"\\[A-Za-z]+\*?", text[start:])
    if not match:
        return None
    index = start + len(match.group(0))
    while index < len(text) and text[index].isspace():
        index += 1
    while index < len(text) and text[index] == "[":
        end = find_matching(text, index, "[", "]")
        if end is None:
            return None
        index = end + 1
        while index < len(text) and text[index].isspace():
            index += 1
    if index >= len(text) or text[index] != "{":
        return None
    end = find_matching(text, index, "{", "}")
    if end is None:
        return None
    head = text[start : index + 1]
    inner = text[index + 1 : end]
    return head, inner, end + 1


def find_matching(text: str, start: int, open_char: str, close_char: str) -> int | None:
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return index
    return None


def protect_latex(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def add(value: str) -> str:
        key = f"ZZXPH{len(placeholders):04d}XZZ"
        placeholders[key] = value
        return key

    text = protect_named_terms(text, add)
    result: list[str] = []
    i = 0
    while i < len(text):
        if text[i] in {"&"}:
            result.append(add(text[i]))
            i += 1
            continue
        if text.startswith("$$", i):
            end = text.find("$$", i + 2)
            if end != -1:
                result.append(add(text[i : end + 2]))
                i = end + 2
                continue
        if text[i] == "$":
            end = find_unescaped(text, "$", i + 1)
            if end != -1:
                result.append(add(text[i : end + 1]))
                i = end + 1
                continue
        if text.startswith("\\(", i):
            end = text.find("\\)", i + 2)
            if end != -1:
                result.append(add(text[i : end + 2]))
                i = end + 2
                continue
        if text.startswith("\\[", i):
            end = text.find("\\]", i + 2)
            if end != -1:
                result.append(add(text[i : end + 2]))
                i = end + 2
                continue
        if text[i] == "\\":
            parsed = parse_full_command(text, i)
            if parsed:
                command_text, end = parsed
                result.append(add(command_text))
                i = end
                continue
        result.append(text[i])
        i += 1
    return "".join(result), placeholders


def protect_named_terms(text: str, add_placeholder) -> str:
    result = text
    for term in sorted(NAMED_TERMS, key=len, reverse=True):
        pattern = re.compile(rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])")
        result = pattern.sub(lambda match: add_placeholder(match.group(0)), result)
    return result


def find_unescaped(text: str, char: str, start: int) -> int:
    index = start
    while True:
        index = text.find(char, index)
        if index == -1:
            return -1
        slash_count = 0
        probe = index - 1
        while probe >= 0 and text[probe] == "\\":
            slash_count += 1
            probe -= 1
        if slash_count % 2 == 0:
            return index
        index += 1


def parse_full_command(text: str, start: int) -> tuple[str, int] | None:
    match = re.match(r"\\([A-Za-z]+|.)\*?", text[start:])
    if not match:
        return None
    index = start + len(match.group(0))
    while index < len(text) and text[index].isspace():
        index += 1
    while index < len(text) and text[index] == "[":
        end = find_matching(text, index, "[", "]")
        if end is None:
            break
        index = end + 1
        while index < len(text) and text[index].isspace():
            index += 1
    while index < len(text) and text[index] == "{":
        end = find_matching(text, index, "{", "}")
        if end is None:
            break
        index = end + 1
        while index < len(text) and text[index].isspace():
            index += 1
    return text[start:index], index


def restore_placeholders(text: str, placeholders: dict[str, str]) -> str:
    result = text
    for key, value in reversed(list(placeholders.items())):
        result = result.replace(key, value)
    for key, value in reversed(list(placeholders.items())):
        result = result.replace(key, value)
    return result


def strip_legacy_cjk_support(output_dir: pathlib.Path) -> None:
    for path in output_dir.rglob("*.tex"):
        text = load_text(path)
        updated = re.sub(
            r"^(\s*)\\usepackage(?:\[[^\]]*\])?\{CJKutf8\}\s*%?\s*$",
            lambda match: f"{match.group(1)}% \\usepackage{{CJKutf8}}",
            text,
            flags=re.MULTILINE,
        )
        updated = re.sub(r"\\begin\{CJK\}\{UTF8\}\{[^}]+\}", "", updated)
        updated = updated.replace(r"\end{CJK}", "")
        if updated != text:
            save_text(path, updated)


def patch_chinese_support(output_dir: pathlib.Path, source_dir: pathlib.Path, main_tex: pathlib.Path) -> pathlib.Path:
    output_main = output_dir / main_tex.relative_to(source_dir)
    strip_legacy_cjk_support(output_dir)
    commands = output_dir / "commands.tex"
    if commands.exists():
        text = load_text(commands)
        text = re.sub(
            r"^\\usepackage\[utf8\]\{inputenc\}\s*$",
            lambda _match: r"% \usepackage[utf8]{inputenc}",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(
            r"^\\usepackage\[T1\]\{fontenc\}\s*$",
            lambda _match: r"% \usepackage[T1]{fontenc}",
            text,
            flags=re.MULTILINE,
        )
        save_text(commands, text)

    text = load_text(output_main)
    if "% Chinese translation support" not in text:
        support = r"""

% Chinese translation support
\usepackage{xeCJK}
\setCJKmainfont{FandolSong-Regular.otf}[ItalicFont=FandolKai-Regular.otf]
\setCJKsansfont{FandolHei-Regular.otf}
\setCJKmonofont{FandolFang-Regular.otf}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 1pt
\renewcommand{\abstractname}{摘要}
\renewcommand{\figurename}{图}
\renewcommand{\tablename}{表}
\renewcommand{\refname}{参考文献}
\renewcommand{\contentsname}{目录}
\makeatletter
\AtBeginDocument{%
  \@ifundefined{crefname}{}{%
    \crefname{figure}{图}{图}%
    \Crefname{figure}{图}{图}%
    \crefname{table}{表}{表}%
    \Crefname{table}{表}{表}%
    \crefname{section}{节}{节}%
    \Crefname{section}{节}{节}%
    \crefname{appendix}{附录}{附录}%
    \Crefname{appendix}{附录}{附录}%
    \crefname{algocf}{算法}{算法}%
    \Crefname{algocf}{算法}{算法}%
  }%
  \@ifundefined{SetAlgorithmName}{}{\SetAlgorithmName{算法}{算法}{算法列表}}%
}
\makeatother
\raggedbottom
"""
        marker = "\\begin{document}"
        if marker in text:
            text = text.replace(marker, support + "\n" + marker, 1)
        else:
            text = support + "\n" + text
        save_text(output_main, text)
    return output_main


def translate_paper(name: str, force: bool = False, limit_files: int | None = None, backend: str = "argos") -> dict:
    paper_dir = ROOT / name
    source_dir = source_for_paper(paper_dir)
    output_dir = paper_dir / OUTPUT_DIR
    copy_source_tree(source_dir, output_dir, force=force)

    source_main = find_main_tex(source_dir)
    output_main = output_dir / source_main.relative_to(source_dir)
    cache_name = CACHE_NAMES[backend]
    translator = SegmentTranslator(paper_dir / cache_name, backend=backend)

    tex_files = sorted(output_dir.rglob("*.tex"))
    translated_paths: list[str] = []
    for path in tex_files:
        source_path = source_dir / path.relative_to(output_dir)
        if not should_translate_file(source_path, source_main):
            translator.stats.skipped_files += 1
            continue
        text = load_text(path)
        translated = translate_tex_content(text, translator)
        save_text(path, translated)
        translated_paths.append(str(path.relative_to(output_dir)))
        translator.stats.translated_files += 1
        translator.save_cache()
        print(f"TRANSLATED {name}: {path.relative_to(output_dir)}", flush=True)
        if limit_files and translator.stats.translated_files >= limit_files:
            break

    output_main = patch_chinese_support(output_dir, source_dir, source_main)
    translator.save_cache()
    status = {
        "paper": name,
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "main_tex": str(output_main),
        "backend": backend,
        "cache": str(paper_dir / cache_name),
        "translated_files": translated_paths,
        "stats": translator.stats.__dict__,
    }
    (paper_dir / STATUS_NAME).write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translate arXiv LaTeX paper sources to Chinese.")
    parser.add_argument("papers", nargs="+", help="Paper folder name(s), for example Dreamer.")
    parser.add_argument("--backend", choices=sorted(CACHE_NAMES), default="argos", help="Translation backend. Defaults to local Argos.")
    parser.add_argument("--force", action="store_true", help="Recreate translation_latex from source.")
    parser.add_argument("--limit-files", type=int, help="Translate only this many .tex files for debugging.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for name in args.papers:
        status = translate_paper(name, force=args.force, limit_files=args.limit_files, backend=args.backend)
        print(json.dumps(status["stats"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
