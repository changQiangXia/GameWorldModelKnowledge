# papersofGW 翻译状态

更新时间：2026-07-02

## 目录结构

`D:\gameWorld\papersofGW` 已按 `D:\gameWorld\papers` 的论文目录风格整理。每篇论文目录中保留：

- 原始 PDF
- `source.tar.gz`
- `source_clean\`
- `extracted.txt`
- `translation_latex\`
- `translation_cache_argos.json`
- `translation_status.json`

## 论文清单

### diffusionAndDOOM

- 原始 PDF：`D:\gameWorld\papersofGW\diffusionAndDOOM\diffusionAndDOOM.pdf`
- 清洗源码：`D:\gameWorld\papersofGW\diffusionAndDOOM\source_clean`
- 译文 LaTeX：`D:\gameWorld\papersofGW\diffusionAndDOOM\translation_latex\main.tex`
- 译文 PDF：`D:\gameWorld\papersofGW\diffusionAndDOOM\translation_latex\main.pdf`
- 翻译后编译：通过，21 页。
- 初译后端：Argos。
- 初译统计：292 个翻译片段，11 个缓存命中，0 个失败，2 个 `.tex` 文件参与翻译。

### mineWorld

- 原始 PDF：`D:\gameWorld\papersofGW\mineWorld\mineWorld.pdf`
- 清洗源码：`D:\gameWorld\papersofGW\mineWorld\source_clean`
- 译文 LaTeX：`D:\gameWorld\papersofGW\mineWorld\translation_latex\main.tex`
- 译文 PDF：`D:\gameWorld\papersofGW\mineWorld\translation_latex\main.pdf`
- 翻译后编译：通过，11 页。
- 初译后端：Argos。
- 初译统计：194 个翻译片段，5 个缓存命中，0 个失败，1 个 `.tex` 文件参与翻译。

## 验证

- 两篇论文的 `translation_latex\main.tex` 均可通过 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 编译。
- 两篇论文的译文 PDF 均已用 `pdftotext` 抽取可见文本并扫描常见机翻坏词、英文脚注残留和术语错误。
- `papersofGW` 下未发现遗留的 `.py`、`.ps1`、`.tmp`、`.bak` 临时脚本/文件。

说明：`translation_cache_argos.json` 保存的是 Argos 初译缓存，可能保留初译阶段的原始机器翻译片段；最终校对结果以 `translation_latex\main.tex` 和编译后的 `main.pdf` 为准。
