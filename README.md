# Game World Model 学习资料库

本仓库用于整理 world model、game world model、Dreamer 系列、DINO/DINOv2、具身智能 benchmark 以及 MineWorld 等相关学习资料。当前内容以中文笔记、LaTeX 教程、论文理解文档和复现要点为主。

## 目录结构

```text
.
├── world_model_tutorial.tex        # 世界模型教程 LaTeX 源文件
├── world_model_tutorial.pdf        # 世界模型教程 PDF
├── prerequisiteKnowledge/          # 前置知识笔记，如 VAE、ELBO、KL、最大似然等
├── papersofGW/                     # game world model 相关论文、源码和理解笔记
├── papers/                         # 本地论文资料目录
└── suggestions/                    # 本地修改建议和迭代记录，默认不提交
```

## 核心文档

- `world_model_tutorial.pdf`
  - 主教程，梳理从 Dyna、VAE、World Models、PlaNet、Dreamer、MuZero、TD-MPC 到 DINO、benchmark 和 game world model 的发展脉络。
  - 已根据本地修改建议进行补强，重点扩展了 VAE、RSSM、Dreamer actor-critic、DINO、benchmark 和 game world model 内容。

- `world_model_tutorial.tex`
  - 主教程的 LaTeX 源文件。
  - 若需要修改教程，应优先编辑该文件，再重新编译 PDF。

- `prerequisiteKnowledge/`
  - 记录学习世界模型前需要掌握的基础知识。
  - 包括最大似然、KL 散度、ELBO、Jensen 不等式、VAE、`p_\theta` / `q_\phi` 等概念解释。

- `papersofGW/mineWorld/`
  - MineWorld 论文、源码和理解笔记相关目录。
  - 重点内容包括算法输入输出、VQ-VAE、动作 tokenizer、视觉 token、动作可控性评估、视频质量指标和个人设备复现思路。

## 主要主题

当前资料覆盖以下研究线索：

- world model 基础
- model-based reinforcement learning
- VAE / latent state / RSSM
- PlaNet / Dreamer / DreamerV2 / DreamerV3
- MuZero / TD-MPC
- Transformer-based world model
- DINO / DINOv2 / JEPA 表征学习
- VLA / LAM / 具身智能研究版图
- benchmark 与评测协议
- game world model
- MineWorld / GameNGen / DIAMOND / Genie / MineDojo / Craftax

## 编译教程 PDF

如果本机安装了 TeX Live 或其他支持 XeLaTeX 的 LaTeX 环境，可以在仓库根目录执行：

```powershell
latexmk -xelatex -interaction=nonstopmode -halt-on-error world_model_tutorial.tex
```

编译成功后会生成或更新：

```text
world_model_tutorial.pdf
```

LaTeX 中间文件如 `.aux`、`.log`、`.toc`、`.xdv`、`.fls`、`.fdb_latexmk` 已在 `.gitignore` 中排除。

## Git 注意事项

本仓库主要建议提交：

- Markdown 学习笔记
- LaTeX 教程源文件
- 最终教程 PDF
- 轻量级配置和说明文件

默认不建议提交：

- 本地翻译依赖目录
- Argos / deep-translator 下载依赖
- 翻译缓存文件
- LaTeX 编译中间产物
- 下载的论文 PDF 原件
- 大体积压缩包
- `suggestions/` 本地修改建议目录

如果确实需要把某篇论文 PDF 或数据文件纳入版本管理，可以按需修改 `.gitignore`。

## 建议工作流

1. 修改 Markdown 或 LaTeX 源文件。
2. 如果修改了 `world_model_tutorial.tex`，重新编译 PDF。
3. 检查 PDF 是否正常打开。
4. 运行 `git status` 检查待提交文件。
5. 手动 commit 和 push。

## 备注

该目录包含大量学习过程中的资料整理和阶段性笔记。部分论文原文、源码压缩包和翻译缓存可能仅适合本地保留，不一定适合推送到公开仓库。
