# World Model 论文译文校对记录

更新日期：2026-06-29

## 本轮校对范围

本轮不是重新翻译，而是在 Argos 译文基础上做译后编辑，重点降低机翻味并保留 LaTeX 结构。

已完成的工作：

- 统一高频术语：智能体、世界模型、归一化、预训练、训练、策略网络、价值网络、稀疏奖励、潜在动作等。
- 修正一批明显错译：如“智能体人”“智能体商”“基因互动环境”“驱动梦想器”“可伸缩的药剂”“世界型号”等。
- 统一部分中文标点和中英文混排空格。
- 人工润色主要入口内容：
  - Dreamer：摘要、导言开头和贡献条目。
  - DreamerV2：摘要、导言开头。
  - DreamerV3：摘要、导言开头。
  - DreamerV4：标题、摘要、导言开头和贡献条目。
  - PlaNet：摘要。
  - MuZero：摘要和导言开头。
  - GAIA：标题和摘要。
  - WorldModel：摘要和导言开头。
  - DriveDreamer：重建版标题、摘要和导言开头。
  - Genie：重建版标题、摘要和导言开头。
  - TD-MPC：重建版标题、摘要和导言开头。
- 本轮继续精修正文关键章节：
  - Dreamer：控制概览、行为学习、潜在动力学、实验、相关工作、结论、超参数与离散控制附录、核心算法框，以及 overview/schema/video/bars/horizon/value/value-small 等关键图注。
  - DreamerV2：方法中的 actor-critic 学习、实验说明、相关工作、改动概述、超参数表、消融表和关键图注。
  - DreamerV3：算法章节中世界模型学习、critic/actor 学习、symlog/symexp two-hot 等段落；继续校正实验章节、PPO 基线方法、优化器、环境实例/随机种子/计算设置、Atari100k 评估协议表、PPO 超参数表和 Minecraft 物品成功率图注。
  - DreamerV4：World Model 智能体、因果分词器、交互式动力学、想象训练、高效 Transformer、Minecraft 离线钻石实验、动作泛化、模型设计、相关工作、讨论，以及主要图表说明。
  - GAIA：导言、相关工作、基准构建、评价结果、讨论、限制、数据卡、扩展评价和样例表格。
  - PlaNet：潜在空间规划、实验章节、超参数、状态空间规划、混合智能体、多步预测、潜在序列模型、视频预测等段落。
  - Genie：方法主干、模型组件、LAM、视频 tokenizer、动力学模型、推断流程、数据集与训练细节、定性结果、智能体训练、消融研究、相关工作、结论、社会影响、作者贡献。
  - DriveDreamer：总体框架、第一阶段训练、Auto-DM、ActionFormer、训练与评价设置、可控驾驶视频生成、驾驶动作生成、讨论与结论、补充材料摘要。
  - TD-MPC：按英文抽取文本重写导言、预备知识、MPPI 推理、TOLD 模型、训练目标、实验设置、相关工作与结论；将 PDF 双栏错位的旧正文和附录残片从输出中隐藏，并整理为附录要点摘要。
  - MuZero：统一标题和 AlphaZero/Stockfish/Elmo 等专名；重写导言、相关工作、算法说明、结果、结论、AlphaZero 对比、搜索算法、超参数、数据生成、网络输入、网络架构、训练、Reanalyze、评估设置和主要图表说明。
  - WorldModel：继续精修导言、智能体模型、VAE/MDN-RNN/Controller 说明、OpenAI Gym rollout 伪代码说明、CarRacing 实验、VizDoom 实验、梦中训练、策略迁移、欺骗世界模型、温度消融、迭代训练、相关工作、讨论、致谢，以及附录中的 ConvVAE、MDN-RNN、Controller、CMA-ES 和 DoomRNN 说明。
- 修正本轮发现的高置信错译：
  - GAIA 中 “法学硕士/有限责任公司/多式联运/Acne粗俗/白色;5876号”等分别修为 LLM、大语言模型、多模态、寻常痤疮、`White; 5,876` 等。
  - DreamerV2 中 “分类潜在物/政策py/二进制潜质/图层规范/游戏机介质/国 籍”等修为分类潜变量、策略熵、二值潜变量、层归一化、玩家中位数、IQN 等。
  - DreamerV4 中 “标致器/快捷键模型/变压器/承包商数据集/铁皮条/世代”等按上下文修为分词器、Shortcut 模型、Transformer、VPT Contractor 数据集、铁镐、生成等。
  - Genie 中 “变压器/标致器/列车时间/地面真实/甲骨文行为克隆/政策”等按上下文修为 Transformer、tokenizer、训练时、真实值、oracle 行为克隆、策略等。
  - PlaNet 中 “后期空间规划/毒剂/混合剂/最小序列模型/微薄奖励”等修为潜在空间规划、智能体、混合智能体、潜在序列模型、稀疏奖励等。
  - DriveDreamer 中 “基因人/驱动政策/自留心/核聚变/亚当W/大量 textbackslash 公式残片”等改写为可读的驾驶世界模型术语和说明段落。
  - TD-MPC 中 “拉面机/厌食/真菌/无模式/地面真实/光碟化/回归/大量 QQ 公式残片”等不再进入成品 PDF，主体内容改为人工校订的可读重构版。
  - MuZero 中 “政策/值功能/报酬/模式/州/任职人数函数/隐蔽状态/绍吉/朔木/鱼类/艾尔莫/拖带/保险单/联合国/类人猿 X/洛杉矶/妇女 Pacman”等按上下文修为策略、价值函数、奖励、模型、状态、表示函数、隐藏状态、将棋、Stockfish、Elmo、自举、策略损失、AlphaZero、Ape-X、LASER、Ms.~Pacman 等。
  - WorldModel 中 “人造物剂/概率遗传模型/无模式/主计长/MDN-RN/音轨/随机保险单/自愿援助/MDN-RNN 导弹/联合国/报酬/变量自动编码器/经常神经网络/健身值/毁灭之光/向实际环境转移政策”等已按上下文修为智能体、概率生成模型、无模型、控制器、MDN-RNN、赛道、随机策略、VAE、奖励、变分自编码器、循环神经网络、适应度、DoomTakeCover-v0、向真实环境迁移策略等。
  - Dreamer 中 “物剂/联合国/值功能/政策/无模式/动作模式/值模式/SLAC 剂/离心控制/免费的鼻涕虫/高斯人/经常状态空间模式/进化神经网络/切片反射/控制为 World Models/当前模式状态/悬浮轨道/基因目标/KL 偏差”等已按上下文修为智能体、和、价值函数、策略、无模型、动作模型、价值模型、SLAC 智能体、离散控制、free nats、对角高斯分布、循环状态空间模型、卷积神经网络、随机反向传播、用世界模型进行控制、当前模型状态、留出轨迹、生成式目标、KL 散度等。
  - DreamerV3 中 “变压器/政策/联合国/物剂/近乎政策优化/渐变剪接/特务/插座边界/基准物剂/有条不紊的政策”等已按上下文修为 Transformer、策略、和、智能体、近端策略优化、梯度裁剪、智能体、episode 边界、基线智能体、随机策略等。

## 编译核查

所有译文均已重新编译，并通过 `pdfinfo` 可读性检查。

| 论文 | PDF 页数 | 编译状态 |
|---|---:|---|
| Dreamer | 21 | 通过 |
| DreamerV2 | 26 | 通过 |
| DreamerV3 | 41 | 通过 |
| DreamerV4 | 33 | 通过 |
| DriveDreamer | 4 | 通过 |
| GAIA | 21 | 通过 |
| Genie | 16 | 通过 |
| MuZero | 19 | 通过 |
| PlaNet | 19 | 通过 |
| TD-MPC | 4 | 通过 |
| WorldModel | 19 | 通过 |

## 仍需注意

DriveDreamer、Genie、TD-MPC 是从 PDF 提取文本重建的译文，不是原始 LaTeX 源码翻译。DriveDreamer 和 Genie 的主干正文已做块级校对，但补充材料、参考文献和部分公式仍可能保留 PDF 抽取造成的错位和字体警告；TD-MPC 的成品 PDF 已改为主体章节人工重构版，附录和参考文献以要点说明替代逐条复刻，若后续需要完整附录译文，需要再按英文原文逐节补全。

源码路线论文的版式更稳定，但正文深处仍可能存在局部直译。WorldModel 本轮已覆盖正文后半部分和附录，并重新编译、扫描高风险错译词；如继续精修，可转向其他论文的深层正文、附录和表格说明，建议按优先级逐章处理：摘要、导言、方法、实验、结论，然后再处理附录和表格说明。

## 2026-06-29 追加校对记录

本次继续对 PlaNet 进行深层译后校对，重点处理 PDF 可见正文和图注中的机翻痕迹：

- `sections/abstract.tex`：统一“潜在过冲”、回合数、纯模型智能体等表述，去除“潜在 overshooting”中英硬混写。
- `sections/introduction.tex`：重写引言主要段落，修正“游戏游戏”“贝尔曼备份宣传奖励”“双链武器”“花样成分”等直译或错译。
- `sections/model.tex`：重写训练目标和确定性路径段落，统一“标准变分下界、数据对数似然、变分后验、确定性路径、随机路径、循环神经网络”等术语。
- `sections/overshooting.tex`：整节重写为“潜在过冲”，修正“后期过度射击、底部过度射击、KL 潜水常态器、最终剂、办案情况、下边的边框”等错误，并修复数学环境中的中文句号。
- `sections/related.tex` 和 `sections/appendix.tex`：润色相关工作、下界推导、状态诊断等段落，修正“国家诊断、衍生物、可变后缀、Jensen 的不平等性、观测空间过度射击”等表述。
- 图注：校对 `figures/domains`、`figures/overshooting`、`figures/score_model`、`figures/score_agent`、`figures/score_multi`、`figures/score_multi/figure_avg`、`figures/score_overshooting`、`figures/score_activation`、`figures/prediction`、`figures/diagnostics`、`figures/mpc`，统一任务名和图注术语，修正“纸牌/彻塔/华克/打开-打开/纯定型/潜射/五至九十五分之五”等可见错译。

验证结果：

- PlaNet 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 19 页。
- 对 PlaNet 成品 PDF 执行高风险错译词扫描，未发现目标词命中。
- 对 `D:\gameWorld\papers` 下所有已生成的 `translation_latex\main.pdf` 执行全局 PDF 可见文本扫描，未发现本轮维护的高风险错译词命中。

## 2026-06-29 追加校对记录（二）

本次继续对 DreamerV2 进行译后校对，重点处理方法章节和 PDF 可见图表说明中的机翻痕迹：

- `sections/method.tex`：重写 DreamerV2 方法章节中“世界模型学习”到“想象 MDP”的主要段落，统一 model-based agent、world model、RSSM、posterior/prior、categorical latent、representation model、straight-through gradient、KL balancing、actor/critic 等术语。
- `figures/model/figure.tex`：重写世界模型图注，修正“后期状态、前置、绝对变量、形状状态、编辑 RSSM”等错误。
- `algos/st.tex` 和 `algos/klbalancing.tex`：修正算法标题为“使用自动微分实现直通梯度”和“使用自动微分实现 KL 平衡”。
- 图注：校对 `figures/abl`、`figures/agg`、`figures/first`、`figures/vs`、`figures/tasks-baselines`、`figures/tasks-latents`、`figures/tasks-repr`、`figures/hum-score`、`figures/hum-video`、`figures/mon-score`、`figures/mon-video`，修正“剪辑记录平整的分数、浮雕、Gamer 正常、游戏机、勘探方法、形象中汲取”等可见错译。
- `sections/appendix.tex`：修正附录标题“模式自由比较、梯队和 KL 平衡障碍、表征学习缺陷”为“无模型比较、潜变量与 KL 平衡消融、表征学习消融”。
- `tables/sep.tex`：重写 Atari 单游戏分数表说明，修正 DreamerV2/IQN/Rainbow 与人类玩家、世界纪录基线的比较描述。

验证结果：

- DreamerV2 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 27 页。
- 对 DreamerV2 成品 PDF 执行本轮高风险错译词扫描，未发现目标词命中。
- 对 `D:\gameWorld\papers` 下所有已生成的 `translation_latex\main.pdf` 执行全局 PDF 可见文本扫描，未发现本轮维护的高风险错译词命中。

## 2026-06-29 追加校对记录（三）

本次收尾 DriveDreamer，并对 DreamerV4 做了一轮更完整的 PDF 可见文本校对：

- DriveDreamer：验证上一轮重构译文输出，确认隐藏的参考文献和补充材料抽取碎片没有进入 PDF；成品 PDF 为 4 页。
- DriveDreamer：PDF 可见文本扫描未命中 `model low`、`Drivecess`、`Autoencodes`、`Mcvd`、`Fcos3d`、`autonousmous` 等抽取/错译残留；源码中被 `\iffalse` 隐藏的坏片段不影响成品输出。
- DreamerV4 `main.tex`：修正“扩散模式、流量匹配、交互式动态、统一分布、对数正常分布、VPT(过滤)、BC(备注)、episode 说明、在线互动、长远战略”等译法，重写离线钻石挑战、人类交互、相关工作、讨论等处的硬译句。
- DreamerV4 图注：校对 `figures/actgen`、`figures/method`、`figures/imag`、`figures/wmtask`、`figures/rl`、`figures/inputs`、`figures/wmtasks`，修正“动作概括、开源器、自愿预防、路西德、绿洲、反向互动、幻觉结构、编织互动”等可见错译。
- DreamerV4 表格：校对 `tables/setups`、`tables/rl_success`、`tables/rl_timing`、`tables/mc_items`、`tables/mc_tasks`、`tables/mc_ladder`，统一 Minecraft 物品名为原木、木板、工作台、木棍、木镐、圆石、石镐、铁矿石、熔炉、铁锭、铁镐、钻石。
- DreamerV4 附录：将 `appendix.tex` 中仍保留英文的“数据集、Minecraft 划分、SOAR Robotics、Epic Kitchens、Dreamer 前代方法、人类交互”等段落和章节标题翻译为中文，任务代码保留英文标识。

验证结果：

- DriveDreamer 使用 `pdfinfo` 验证，`main.pdf` 为 4 页；PDF 可见文本高风险扫描未发现目标词命中。
- DreamerV4 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 33 页。
- DreamerV4 PDF 可见文本扫描未命中本轮维护的高风险错译词；唯一残留英文 `Offline Diamond Challenge` 来自嵌入图形中的英文元素，不是 LaTeX 正文、表注或图注。
- 对 `D:\gameWorld\papers` 下所有已生成的 `translation_latex\main.pdf` 执行全局 PDF 可见文本扫描，目前仅 DreamerV3 仍有 4 处高风险命中，下一步优先处理。

## 2026-06-29 追加校对记录（四）

本次继续处理 DreamerV3，并顺手清理全局扫描暴露出的 Atari 任务名硬译问题。重点不再是大段重写，而是修正 PDF 可见表格、图注和术语行中的残留机翻痕迹：

- DreamerV3：完成 `sections/methods.tex` 和 `sections/experiments.tex` 的整节人工润色后，继续校对 `sections/related.tex`、`sections/supplement.tex`、`figures/arxiv_minecraft/figure.tex`、`figures/minecraft/figure.tex`、`figures/tasks/figure.tex`、`figures/arxiv_bars/figure.tex`、`figures/bars/figure.tex`、`figures/model/figure.tex`、`figures/ablations/figure.tex` 等 PDF 可见说明。
- DreamerV3：校对 `tables/benchmarks.tex`、`tables/modelsizes.tex`、`tables/hparams.tex`、`tables/hparams_ppo.tex`、`tables/scores_bsuite.tex`、`tables/scores_dmcp.tex`、`tables/scores_dmcv.tex`、`tables/scores_dmlab.tex`、`tables/scores_procgen.tex`，统一“环境步数、回放比率、模型规模、随机种子、GPU 天数”等表头，并保留 BSuite、DMLab、ProcGen、DeepMind Control Suite 的官方任务名。
- DreamerV3：进一步修正 `tables/scores_atari.tex`、`tables/scores_atari100k.tex`、`tables/atari100k_setting.tex` 中的 Atari 游戏名和算法名，避免“战略规划、图瓦卢、IRIS（爱尔兰国际空间研究所）、游戏机中位数、环境台阶、智能体台阶”等硬译；Atari 游戏名统一保留官方英文，如 `Alien`、`Ms Pacman`、`Qbert`、`Road Runner`、`Seaquest`、`Yars Revenge`、`Zaxxon`。
- Dreamer：修正 `sections/appendix.tex` 中 DeepMind Control Suite 任务名硬译，统一为 `Acrobot Swingup`、`Cartpole Balance`、`Cartpole Balance Sparse`、`Cartpole Swingup`、`Cartpole Swingup Sparse`、`Cheetah Run`、`Cup Catch`、`Finger Spin`、`Finger Turn Easy`、`Finger Turn Hard`、`Hopper Hop`、`Hopper Stand`、`Pendulum Swingup`、`Quadruped Run`、`Quadruped Walk`、`Reacher Easy`、`Reacher Hard`、`Walker Run`、`Walker Stand`、`Walker Walk`；同时修正脚注和表头中的“本体感受、环境步骤”。
- Dreamer：修正 `figures/tasks/figure.tex` 的任务图小标题和图注，将“杯赛、循环、霍普尔、华克、四进制、接触动态”等改为 `Cup Catch`、`Acrobot Swingup`、`Hopper`、`Walker`、`Quadruped` 和“接触动力学”。
- DreamerV2：修正 `sections/related.tex` 中“本体感受输入”为“本体感知输入”；重校 `tables/sep.tex`，将 Atari 单游戏分数表中的硬译任务名统一恢复为官方英文名，并将“玩家”表头改为“人类玩家”。由于表格内容变紧凑，成品 PDF 页数由 27 页变为 26 页。
- MuZero：修正 `main.tex` 中两张 Atari 结果表的任务名，将“外国人、电线、节点、泊车、分组、百分点、维护者、伦杜罗、高速公路、密码、沟谷、主角、分钟、克贝尔、海上扣押、魔导、报复”等统一恢复为官方 Atari 游戏名。

验证结果：

- Dreamer 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 21 页。
- DreamerV2 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 26 页。
- DreamerV3 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 41 页。
- MuZero 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 19 页；仍有原模板/棋盘字体相关 warning，但不影响 PDF 输出。
- 对 `D:\gameWorld\papers` 下所有已生成的 `translation_latex\main.pdf` 执行全局 PDF 可见文本扫描，未发现本轮维护的坏译专用词表命中。`TD-MPC\translation_latex\main.tex` 中仍保留被隐藏的旧 PDF 抽取碎片，成品 `main.pdf` 未包含这些碎片。

## 2026-06-29 追加校对记录（五）

本次继续对 GAIA 做 PDF 可见文本校对，重点处理摘要、导言、相关工作、基准说明、讨论、限制和附录示例中的机翻痕迹：

- GAIA `main.tex`：重写摘要中“将标志着 AI 研究取得重要进展”“数据可通过此处访问”等套话和硬译，改为更自然的基准说明与 Hugging Face 项目页表述。
- GAIA 图 1 和图 2：将“基本事实”统一为“标准答案”，将“工作时间/最后一个回答”改为“执行代码/最终回答”，并润色冰淇淋、Excel 销售额、代码解释器等样例说明。
- GAIA 导言：改写“不是继续提高人类难度，而是……”等公式化句式，整理 t-AGI 讨论、开发集/排行榜说明和“开放式生成评价”结尾，减少宣传式表达。
- GAIA 相关工作：修正“节 A中的讨论”、`ToolQA(`、`Gorilla(`、`OpenAGI(`、`WebGPT Nakano` 等 LaTeX 引用拼接痕迹，保持英文系统/基准名并让中文句子可读。
- GAIA 讨论与限制：重写“API之后关闭的模型”“象征性生成的随机性”“社会经济格局”“欠规定的问题”等直译表达，统一为“闭源助手的可复现性、生成随机性、社会经济结构、信息不足的问题”等说法。
- GAIA 数据卡和扩展说明：修正“curators/annotators、职等、答复、错配的原因、附加说明的问题”等表头和表注，改为“策划者/标注者、级别、答案、不匹配原因、标注示例”。
- GAIA 附录示例：润色 Kuznetzov/Nedoshivina 标本保存地点、Goldfinger 片尾颜色、Rubik 魔方谜题等 GPT4 解答示例，清理“沉淀所在、破坏者、面孔、立方体构成它的侧面”等硬译。

验证结果：

- GAIA 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 仍为 21 页。
- 对 GAIA 成品 PDF 执行坏译专用词表扫描，未发现 `标志着`、`基本事实`、`整品脱`、`工作时间`、`最后一个回答`、`职等`、`错配`、`沉淀`、`API之后`、`象征性生成`、`ToolQA(`、`OpenAGI(`、`WebGPT Nakano` 等目标命中。
- 对 `D:\gameWorld\papers` 下所有已生成的 `translation_latex\main.pdf` 执行全局 PDF 可见文本扫描，仅 PlaNet 命中一句正常数学说明“此处省略条件中的动作”，不是坏译残留。

## 2026-06-29 追加校对记录（六）

本次继续对 DreamerV3 做首页和结论段校对，重点处理 PDF 第一屏即可看到的硬译和模板标签问题：

- `main.tex`：将标题从“掌握多元域通过World Models”改为“通过世界模型掌握多样领域”；显式设置 `caption` 的 figure/table 名称，使成品 PDF 图注从 `Figure` 改为“图”。
- `sections/abstract.tex` 和 `sections/intro.tex`：将“人工智能中的重要挑战”等宣传式表述改为“人工智能中的难题”，并改写“不仅……而且”“尤其值得注意的是”等公式化句式。
- `sections/algorithm.tex`：将“目标不是只在同一领域内解决相似任务，而是……”改为更直接的跨领域学习说明。
- `sections/experiments.tex`：将“显著超过 PPO”“长期挑战”等表述改为更克制的性能比较和“长期难题”。
- `sections/discussion.tex`：重写结论段，修正“掌握广泛的域”“从各种数据和计算预算中大力学习”“重要的里程碑”“铺平道路”等直译和套话。
- `figures/arxiv_bars/figure.tex`、`figures/bars/figure.tex`、`figures/ablations/figure.tex`：润色首页基准摘要和消融图注，减少“显著、值得注意、不仅……也……”等模板化表达。

验证结果：

- DreamerV3 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 仍为 41 页。
- PDF 可见文本确认标题已变为“通过世界模型掌握多样领域”，图注标签已从 `Figure` 变为“图”。
- 对 DreamerV3 成品 PDF 扫描 `掌握多元域`、`通过World Models`、`大力学习`、`掌握广泛的域`、`重要的里程碑`、`Figure [0-9]`、`Table [0-9]` 等目标词，未发现命中。

## 2026-06-29 追加校对记录（七）

本次处理多篇译文中 PDF 图表标签仍显示为英文 `Figure/Table` 的问题：

- Dreamer、DreamerV2、DreamerV4、PlaNet、WorldModel：在 `main.tex` 中文支持区加入对 `caption` 与 `\fnum@figure/\fnum@table` 的显式覆盖，使成品 PDF 图表标签显示为“图/表”。
- DreamerV2：将标题“掌握 Atari 带宽度World Models”修正为“使用离散世界模型掌握 Atari”。

验证结果：

- Dreamer、DreamerV2、DreamerV4、PlaNet、WorldModel 均重新编译通过，页数分别为 21、26、33、19、19。
- PDF 可见文本抽查确认图表标签已显示为“图/表”。
- 全局扫描 `Figure [0-9]|Table [0-9]` 后，仅 Genie 仍有英文附录/表格碎片命中；这些属于重构译文中的未翻译英文正文，下一步单独处理。

## 2026-06-29 追加校对记录（八）

本次继续降低成品 PDF 的机翻痕迹，重点处理 Genie 重构译文后半部分和全局扫描暴露出的模板化表达：

- Genie `main.tex`：将首页作者栏从“Argos Translate 本地翻译”改为“中文译文备份”，并把通讯作者行改为更自然的中文格式。
- Genie `main.tex`：重写“其它示例轨迹”之后的附录块，补全图 16、图 17、数据集筛选流程、训练细节、规模化实验、行为克隆和 CoinRun 可复现实例中的英文残留。
- Genie `main.tex`：将表 4 至表 17 的英文表题统一改为中文，保留 Platformers、CoinRun、tokenizer、BC、LAM、TPU 等技术名和数据项。
- DreamerV2、DreamerV3、DreamerV4、PlaNet、TD-MPC、WorldModel：小范围改写 PDF 可见文本中的“至关重要”“不是……而是……”等模板化句式，使语气更接近论文中文表达。
- DriveDreamer、TD-MPC：清理首页“Argos Translate 本地翻译”模板痕迹；DriveDreamer 另将导言中的“不只是……而是……”改为直接陈述。

验证结果：

- Genie 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 为 15 页。
- DreamerV2、DreamerV3、DreamerV4、PlaNet、TD-MPC、WorldModel 重新编译通过，页数分别为 26、41、33、19、4、19。
- DriveDreamer、TD-MPC 再次重新编译通过，页数均为 4。
- 对全部 `translation_latex/main.pdf` 执行 PDF 可见文本扫描，未发现 `Figure [0-9]`、`Table [0-9]`、`Argos Translate`、`Corresponding authors`、`Consistent to findings`、`Scaling model size`、`Scaling batch size`、`Genie Model` 等目标残留。
- 对全部成品 PDF 执行坏译词表扫描，未发现本轮维护的 `标志着`、`值得注意的是`、`至关重要`、`不只是……而是`、`不是……而是`、`基本事实`、`工作时间`、`最后一个回答`、`错配`、`职等`、`潜在 overshooting` 等目标命中。

## 2026-06-29 追加校对记录（九）

本次继续对短篇 PDF 重构译文做人工可读性检查，重点处理 DriveDreamer 中仍偏宣传式、模板化的表达：

- DriveDreamer `main.tex`：重写摘要开头，将“有望理解驾驶环境”“首个基于真实世界驾驶场景构建的世界模型”等表述改为更克制的研究对象和实验结果说明。
- DriveDreamer `main.tex`：将“复杂环境的综合表示”“世界模型为这一转变提供了可能”“显著进展”等宣传式或模板化表达改为直接的技术描述。
- DriveDreamer `main.tex`：改写可控视频生成和驾驶动作生成段落，删除“形成了对驾驶世界的综合理解”“较高的可控性和多样性，有潜力”等拔高句式，并去掉“不仅……也……”结构。
- DriveDreamer `main.tex`：重写结论段，将“提供了新的方向”“至关重要”等空泛总结改为“给出一种实现路线”，并补充闭环驾驶和安全评估仍需验证的限制。

验证结果：

- DriveDreamer 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 仍为 4 页。
- DriveDreamer PDF 可见文本扫描未发现 `有望`、`首个`、`综合理解`、`综合表示`、`显著进展`、`更深入`、`较高的可控性`、`有潜力`、`提供了新的方向`、`提供了可能`、`至关重要`、`不仅`、`不是……而是` 等目标残留。
- 对全部 `translation_latex/main.pdf` 执行全局扫描，未发现本轮维护的坏译词表、`Argos Translate`、`Figure [0-9]`、`Table [0-9]` 等目标命中。

## 2026-06-29 追加校对记录（十）

本次继续抽查 MuZero 的 PDF 可见文本，并顺手清理全局扩展扫描中新暴露出的摘要/讨论段模板词：

- MuZero `main.tex`：重写摘要和导言开头，将“核心挑战之一”“巨大成功”“显著成功”“新的最优水平”“超人表现”等表达改为更克制的“长期问题”“很强结果”“当时最好的结果”“超越人类水平的表现”。
- MuZero `main.tex`：将章节标题“以前的工作”改为“相关工作”，将“6 承认”改为“6 致谢”。
- MuZero `main.tex`：重写结论句，将“强大的学习与规划方法”“提供了一条可行路径”改为“学习模型与规划结合后，可以用于缺少完美模拟器的现实世界问题”。
- DreamerV4 `main.tex`：将摘要中“为构建智能体提供了一条可行路径”改为“从而用于构建智能体”。
- PlaNet `sections/abstract.tex`：将摘要开头“规划方法已经取得了显著成功”改为“规划方法已经非常有效”。
- Genie `main.tex`：将讨论段中的“作者承认”改为“作者同时指出/论文指出”，避免与此前“承认”标题坏译混淆，也便于全局词表扫描。

验证结果：

- MuZero 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 仍为 19 页。
- DreamerV4、PlaNet 重新编译通过，页数分别为 33、19。
- Genie 重新编译通过，`main.pdf` 仍为 15 页。
- MuZero PDF 可见文本扫描未发现 `承认`、`巨大成功`、`显著成功`、`核心挑战`、`新的最优水平`、`超人表现`、`可行路径` 等目标残留。
- 对全部 `translation_latex/main.pdf` 执行全局扩展扫描，未发现本轮维护的坏译词表、`Argos Translate`、`Figure [0-9]`、`Table [0-9]`、`承认`、`巨大成功`、`显著成功`、`核心挑战`、`新的最优水平`、`超人表现`、`可行路径` 等目标命中。

## 2026-06-29 追加校对记录（十一）

本次继续扩展扫描“提供路径/可能、强大的、令人……”等更宽泛的模板表达，并只处理人工判断为机翻味明显的可见句子：

- DreamerV2 `sections/discussion.tex`：将“世界模型还为……提供了新的可能”改为“世界模型还可用于……”，减少结论段的宣传式收束。
- DreamerV3 `sections/experiments.tex`：将“强大的 MuZero 算法”改为“MuZero 算法”，保留比较对象，去掉主观修饰。
- DreamerV4 `main.tex`：将“为未来……提供了可能”改为“表明，未来可以……”，并将“令人惊讶的是”改为“结果显示”。
- DreamerV4 `figures/actgen/figure.tex`：将“为利用多样化无标签网络视频学习模拟器提供了路径”改为“并将其用于多样化无标签网络视频中的模拟器学习”。
- GAIA `main.tex`：将“结果都令人失望”改为“结果都较差”。
- Genie `main.tex`：将摘要中的“为训练未来的通用智能体提供了一条路径”改为“提供了一种思路”。

验证结果：

- DreamerV2、DreamerV3、DreamerV4、GAIA、Genie 均重新编译通过，页数分别为 26、41、33、21、15。
- 硬性坏译词表扫描未发现 `提供了新的可能`、`强大的 MuZero`、`令人惊讶的是`、`令人失望`、`提供了一条路径` 等目标命中。
- 更宽泛的扫描仍会命中若干正常技术用语，如 `视觉复杂性`、`丰富的训练信号`、`复杂性集中在世界模型`、`长期以来仍是开放问题`；这些经人工判断属于语义正常的技术表述，本轮未机械替换。

## 2026-06-29 追加校对记录（十二）

本次继续检查 WorldModel 的 PDF 第一屏和方法段落，并修正多篇源码模板中摘要标题仍显示为英文的问题：

- WorldModel `main.tex`：覆盖 ICML 模板硬编码的 abstract 环境，使 PDF 首页摘要标题从 `Abstract` 改为“摘要”。
- WorldModel `main.tex`：润色导言和控制器段落，将“足够强大”“丰富的空间和时间表示”“大部分复杂性集中在世界模型”“重要的实践好处”“高度紧凑”等表达改为更直接的技术描述。
- Dreamer `main.tex`：覆盖 ICLR abstract 环境，使 PDF 首页摘要标题显示为“摘要”。
- DreamerV2 `main.tex`：覆盖 ICLR abstract 环境，使 PDF 首页摘要标题显示为“摘要”。
- PlaNet `main.tex`：覆盖 ICML abstract 环境，使 PDF 首页摘要标题显示为“摘要”。
- DreamerV2 `sections/abstract.tex`：将“强大世界模型”改为“学得世界模型”。

验证结果：

- WorldModel 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，`main.pdf` 仍为 19 页。
- Dreamer、DreamerV2、PlaNet 重新编译通过，页数分别为 21、26、19。
- Dreamer、DreamerV2、PlaNet、WorldModel 首页 PDF 可见文本均显示“摘要”，且未再出现独立的英文 `Abstract` 标签。
- 全局硬性坏译词表扫描未发现 `足够强大`、`丰富的空间`、`很强的表达能力`、`大部分复杂性`、`重要的实践好处`、`高度紧凑`、`强大世界模型` 等目标命中，也未发现此前维护的 `Argos Translate`、`Figure [0-9]`、`Table [0-9]` 等目标残留。

## 2026-06-29 追加校对记录（十三）

本次继续处理 PDF 可见公式和方法段中残留的英文结构标签，重点覆盖 Dreamer、DreamerV2 和 PlaNet：

- Dreamer `sections/overview.tex`：将“加强学习”修正为“强化学习”；将公式旁的 `Representation model`、`Transition model`、`Reward model` 改为“表征模型、转移模型、奖励模型”。
- Dreamer `sections/dynamics.tex`：将 `Representation model`、`Observation model`、`Reward model`、`Transition model`、`State model` 改为“表征模型、观测模型、奖励模型、转移模型、状态模型”。
- Dreamer `sections/behavior.tex`：将 `Action model`、`Value model` 改为“动作模型、价值模型”。
- DreamerV2 `sections/method.tex`：将公式中的 `Recurrent model`、`Representation model` 改为“循环模型、表征模型”；将 `Actor`、`Critic` 标签改为中文冒号格式。
- PlaNet `sections/planning.tex` 和 `sections/model.tex`：将 `Policy`、`Transition model`、`Observation model`、`Reward model`、`Deterministic state model`、`Stochastic state model` 等公式标签改为对应中文。

验证结果：

- Dreamer、DreamerV2、PlaNet 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，页数分别为 21、26、19。
- 对三篇成品 PDF 扫描 `Representation model:`、`Transition model:`、`Observation model:`、`Reward model:`、`Value model:`、`Action model:`、`State model:`、`Recurrent model:`、`Policy:`，未发现残留。
- 源码扫描未发现 `加强学习` 或上述英文公式标签残留。
- 对全部 `translation_latex/main.pdf` 执行全局硬性坏译词表扫描，未发现本轮维护的英文公式标签和既有坏译词表命中。

## 2026-06-29 追加校对记录（十四）

本次继续检查英文结构词残留，重点处理源码可控的参考文献标题：

- Dreamer `main.tex`：显式覆盖 `natbib` 的 `\bibsection`，使参考文献标题从 `References` 改为“参考文献”。
- DreamerV2 `main.tex`：显式覆盖 `natbib` 的 `\bibsection`，使参考文献标题从 `References` 改为“参考文献”。
- PlaNet `main.tex`：显式覆盖 `natbib` 的 `\bibsection`，使参考文献标题从 `References` 改为“参考文献”。

验证结果：

- Dreamer、DreamerV2、PlaNet 重新编译通过，页数分别为 21、26、19。
- 三篇成品 PDF 中均可见“参考文献”标题，未再命中独立的 `References` 标题。
- 全局结构词扫描仅剩 WorldModel 参考文献条目中的书名 `Introduction to Reinforcement Learning`，不是正文标题或模板残留。
- 全局硬性坏译词表扫描未发现本轮维护的结构标签和既有坏译目标命中。

## 2026-06-29 追加校对记录（十五）

本次继续处理首页模板残留、短篇重构稿源码清理，以及 Genie 中仍偏宣传式的中文表达：

- Dreamer `main.tex`：将首页页眉 `Published as a conference paper at ICLR 2020` 本地化为“发表于 ICLR 2020 会议论文”，并将作者脚注中的 `Correspondence to:` 改为“通讯作者：”。
- DreamerV2 `main.tex`：将首页页眉 `Published as a conference paper at ICLR 2021` 本地化为“发表于 ICLR 2021 会议论文”，并将作者脚注中的 `Correspondence to:` 改为“通讯作者：”。
- PlaNet `main.tex`：覆盖 ICML 模板的作者脚注输出，将 `Correspondence to:` 改为“通讯作者：”，避免首页脚注仍显示英文模板。
- DreamerV4 `commands.tex`：将首页脚注 `Equal contribution` 和 `Website` 改为“共同一作”和“项目网站”，保留 Google DeepMind、San Francisco 与项目链接等元信息。
- Genie `main.tex`：重写摘要、导言和定性结果中的若干句子，将“一个全新的世界”“新颖且富有创造性的内容”“重要前沿”“真正沉浸式的体验”“值得注意的是”“自然涌现的能力”“更重要的是”等表达改为更具体的论文式表述。
- TD-MPC `main.tex` 和 DriveDreamer `main.tex`：删除隐藏在 `\iffalse...\fi` 中的旧 PDF 抽取碎片。它们此前不进入成品 PDF，但源码中包含明显坏译和不可读参考文献残片，不适合作为备份长期保留。

验证结果：

- DreamerV4、Genie、TD-MPC、DriveDreamer 均使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，页数分别为 33、15、4、4。
- Dreamer、DreamerV2、PlaNet 的首页模板本地化结果已通过 PDF 文本抽查；全库首页前 100 行扫描未再命中 `Published as`、`conference paper`、`Correspondence to:`、`Equal contribution`、`Website:` 等模板残留。
- DreamerV4 成品 PDF 首页可见“共同一作”和“项目网站”，未再出现 `Equal contribution` 或 `Website:`。
- Genie 成品 PDF 未再命中本轮处理的宣传式表达：`值得注意的是`、`新颖且富有创造`、`重要前沿`、`真正沉浸式`、`完全想象`、`自然涌现`、`更重要的是`、`全新的世界`。
- TD-MPC 和 DriveDreamer 的 `translation_latex` 源码未再命中 `\iffalse`、`拉面机`、`当地迷你`、`autonousmous` 等旧抽取碎片标记。
- 对全部 `translation_latex/main.pdf` 执行全局硬性坏译词表扫描，未发现既有坏译目标、新增模板英文目标或本轮新增宣传式表达命中。

## 2026-06-29 追加校对记录（十六）

本次按“可以结束”的要求做收尾审计，不再扩展新一轮正文润色范围：

- 盘点 `D:\gameWorld\papers` 下 11 个论文目录：Dreamer、DreamerV2、DreamerV3、DreamerV4、DriveDreamer、GAIA、Genie、MuZero、PlaNet、TD-MPC、WorldModel 均保留根目录原始 PDF，且均存在 `translation_latex/main.tex` 与 `translation_latex/main.pdf`。
- 删除 DreamerV2 `figures/first/figure.tex` 中已注释的旧英文图注/脚注块。该块不进入 PDF，但包含 `According to its authors`、`Gamer normalized task median` 等旧英文残留，不适合作为最终备份源码保留。

验证结果：

- DreamerV2 使用 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 重新编译通过，成品仍为 26 页。
- 全部 11 篇译文 PDF 均可由 `pdfinfo` 读取页数：Dreamer 21、DreamerV2 26、DreamerV3 41、DreamerV4 33、DriveDreamer 4、GAIA 21、Genie 15、MuZero 19、PlaNet 19、TD-MPC 4、WorldModel 19。
- 对全部 `translation_latex/main.pdf` 执行收尾扫描，未命中 `Published as`、`conference paper`、`Correspondence to:`、`Equal contribution`、`Website:`、`Argos Translate`、`Figure [0-9]`、`Table [0-9]`，也未命中本轮维护的典型机翻表达。
- 对全部 `translation_latex` 源码执行收尾扫描，未命中 `\iffalse`、`拉面机`、`当地迷你`、`autonousmous`、`According to its authors`、`Gamer normalized task median` 等旧抽取或注释残留。
- 当前版本定位为个人备份和阅读版：明显模板残留、硬性错译词和主要机翻痕迹已清理；若后续用于公开发布，仍建议逐篇逐页做出版级人工精校。
