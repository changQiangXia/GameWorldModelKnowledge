# Game World Model 学习资料库

这个仓库用于整理我在 world model 和 game world model 方向上的学习资料，包括教程、论文原文、论文翻译、复现要点、前置数学知识和阶段性理解笔记。

当前重点方向包括：Dreamer 系列、VAE/RSSM、DINO/DINOv2、具身智能研究版图、benchmark、game world model，以及 MineWorld 等游戏世界模型论文。

## 快速入口

| 路径 | 内容 |
| --- | --- |
| `world_model_tutorial.pdf` | 世界模型主教程 PDF，适合直接阅读 |
| `world_model_tutorial.tex` | 世界模型主教程 LaTeX 源文件，修改教程时优先编辑这里 |
| `prerequisiteKnowledge/` | 前置知识笔记，如最大似然、KL 散度、ELBO、Jensen 不等式、VAE 等 |
| `papers/` | world model、Dreamer 等方向的论文原文 PDF 与翻译 PDF |
| `papersofGW/` | game world model 方向的论文原文 PDF 与翻译 PDF；本地可放研究材料 |
| `papersofGW/mineWorld/` | MineWorld 相关资料目录；Git 默认只保留论文原文和翻译 PDF |
| `suggestions/` | 本地修订建议目录；仓库只保留 `.gitkeep` 占位文件 |

## 内容地图

主教程和相关笔记目前覆盖以下主题：

- 基础脉络：Dyna、model-based reinforcement learning、World Models、PlaNet
- 生成式状态建模：VAE、VQ-VAE、latent state、RSSM、ELBO
- Dreamer 系列：Dreamer、DreamerV2、DreamerV3，以及 actor-critic 想象训练
- 其他世界模型路线：MuZero、TD-MPC、Transformer-based world model
- 表征学习补充：DINO、DINOv2、JEPA
- 具身智能相关讨论：world model、VLA、LAM、benchmark 与评测协议
- 游戏世界模型：MineWorld、GameNGen、DIAMOND、Genie、MineDojo、Craftax
- 复现关注点：数据来源、算力需求、输入输出定义、指标计算和个人设备可行性

## 论文目录约定

`papers/` 和 `papersofGW/` 中默认只提交两类文件：

```text
papers/<paper>/<paper>.pdf
papers/<paper>/translation_latex/main.pdf

papersofGW/<paper>/<paper>.pdf
papersofGW/<paper>/translation_latex/main.pdf
```

也就是说，论文原文 PDF 和翻译后的 PDF 会保留在 Git 中；其他过程文件默认只在本地保留。

默认不提交的内容包括：

- 论文抽取文本
- 翻译缓存和状态文件
- 翻译用 LaTeX 中间文件
- 下载的源码、压缩包和临时数据
- 本地 Python 依赖目录
- LaTeX 编译中间产物
- `suggestions/` 中除 `.gitkeep` 以外的个人修改建议

如果某篇论文的翻译 PDF 不在 `translation_latex/main.pdf`，需要按实际路径补充 `.gitignore` 白名单。

## 编译教程

如果本机安装了 TeX Live 或其他支持 XeLaTeX 的 LaTeX 环境，可以在仓库根目录执行：

```powershell
latexmk -xelatex -interaction=nonstopmode -halt-on-error world_model_tutorial.tex
```

编译成功后会生成或更新：

```text
world_model_tutorial.pdf
```

LaTeX 中间文件如 `.aux`、`.log`、`.toc`、`.xdv`、`.fls`、`.fdb_latexmk` 已通过 `.gitignore` 排除。

## 建议工作流

1. 修改 Markdown 笔记或 `world_model_tutorial.tex`。
2. 如果修改了 `world_model_tutorial.tex`，重新编译 `world_model_tutorial.pdf`。
3. 检查 PDF 是否能正常打开，内容是否更新。
4. 运行 `git status` 检查待提交文件。
5. 手动 commit 和 push。

## 维护原则

这个仓库主要保存最终可阅读、可备份的学习材料。源码、依赖、缓存、抽取文本和临时脚本尽量留在本地，不作为仓库内容长期维护。论文目录中优先保留原文 PDF 和翻译 PDF，避免把一次性处理过程全部提交进去。
