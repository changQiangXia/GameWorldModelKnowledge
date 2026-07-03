# papersofGW 精校状态

更新时间：2026-07-02

## 精校策略

两篇论文均采用“Argos 初译 + 三轮精校”的流程：

1. 第一轮：修正术语、标题、摘要、引言和方法部分的核心表述，统一 world model、tokenizer、agent、policy、frame、parallel decoding、controllability 等术语。
2. 第二轮：检查实验、表格、图注和附录，修复直译标题、错误指标名称、损坏的 LaTeX 宏和不自然句式。
3. 第三轮：抽取 PDF 可见文本，扫描坏词、英文脚注残留、术语错译和公式/数值误写，并进行最后的人工读感修正。

## diffusionAndDOOM

主要校对内容：

- 将标题、摘要、导言、交互式世界模拟定义、GameNGen 方法、训练与推理说明改写为更自然的中文论文表述。
- 统一 `GameNGen`、`DOOM`、`Stable Diffusion`、`ViZDoom`、`teacher forcing`、`agent`、`policy`、`frame`、`diffusion model` 等术语。
- 修正实验结果、图像/视频质量、人类评估、消融实验、附录样本、奖励函数、数据集规模、蒸馏和 Chrome Dino 示例中的机器翻译痕迹。
- 汉化作者脚注中的 `Equal contribution` 和 `Work done while at Google Research`。
- 最终 PDF 编译通过，21 页；源码和 PDF 抽文本未命中目标坏词清单。

## mineWorld

主要校对内容：

- 重写标题、作者脚注、摘要、导言、贡献点、框架概览、tokenizer、Transformer 解码器、并行解码、数据预处理、指标、实现细节、主要结果、案例研究和结论。
- 统一 `MineWorld`、`Minecraft`、`Oasis`、`VPT`、`VQ-VAE`、`IDM`、`APM`、`FPS`、`token`、`tokenizer`、`Transformer`、`next-token prediction`、`parallel decoding`、`controllability` 等术语。
- 修复 LaTeX 宏损坏、图环境参数损坏、表格字段误译以及附录中的明显机翻词。
- 将 `隐藏暗淡`、`MLP 阴暗`、`数字头`、`数字层`、`亚当W`、`视觉助推器`、`开心`、`PSNR 系统` 等误译改为正确术语。
- 将学习率 `$3e^{-4}$` 修正为 `$3\times10^{-4}$`，避免数学含义错误。
- 最终 PDF 编译通过，11 页；源码和 PDF 抽文本未命中目标坏词清单。

## 质量边界

本次结果适合作为个人阅读、备份和后续研究笔记使用。已经做过三轮精校并修正明显机翻痕迹，但并未按出版级译稿标准逐句对照原文审校。
