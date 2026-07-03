# World Model 论文翻译交付状态

更新日期：2026-06-26

## 主流程

- 翻译主流程：Argos Translate（英文到中文）。
- 编译方式：XeLaTeX / latexmk。
- 输出结构：每篇论文保留在同名目录下，译文位于 `translation_latex/`。
- 主要输出文件：
  - `D:\gameWorld\papers\<论文名>\translation_latex\main.tex`
  - `D:\gameWorld\papers\<论文名>\translation_latex\main.pdf`

## 状态表

| 论文 | 处理方式 | 原 PDF | 译文 LaTeX | 译文 PDF | 页数 |
|---|---|---:|---:|---:|---:|
| Dreamer | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 21 |
| DreamerV2 | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 27 |
| DreamerV3 | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 41 |
| DreamerV4 | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 32 |
| DriveDreamer | 基于 PDF 提取文本重建 | 1 | 是 | 是 | 14 |
| GAIA | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 21 |
| Genie | 基于 PDF 提取文本重建 | 1 | 是 | 是 | 19 |
| MuZero | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 19 |
| PlaNet | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 19 |
| TD-MPC | 基于 PDF 提取文本重建 | 1 | 是 | 是 | 21 |
| WorldModel | 基于 LaTeX 源码翻译 | 1 | 是 | 是 | 19 |

## 说明

DreamerV3 已重新从 `source.tar.gz` 解包到 `source_clean/`，并完成 Argos 翻译与 XeLaTeX 编译。

DriveDreamer、Genie、TD-MPC 的 arXiv 源码下载失败，因此采用现有 `extracted.txt` 的 PDF 文本提取结果进行重建翻译。这三篇的译文 PDF 可读，但不能完全恢复原论文的公式、图片、双栏排版和复杂表格结构。

Dreamer、DreamerV2、DreamerV3、DreamerV4、GAIA、MuZero、PlaNet、WorldModel 使用 LaTeX 源码路线翻译，版式保真度高于重建路线。

`D:\gameWorld\papers\_test` 是测试目录，里面没有论文 PDF，未计入论文处理清单。
