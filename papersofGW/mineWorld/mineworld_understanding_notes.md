# MineWorld 论文理解笔记

## 1. 目标

MineWorld 的目标是把 Minecraft 建模成一个可交互的世界模型：给定若干历史游戏画面和玩家动作，模型生成动作执行后的后续游戏画面。也就是说，它试图学习一个神经版 Minecraft 局部模拟器：

```text
历史画面 + 玩家动作 -> 未来画面
```

MineWorld 还要求生成画面对输入动作有响应。例如输入“向前走”“转动视角”“攻击”“使用物品”，生成画面应体现这些动作造成的变化。

## 2. 研究问题

论文用 $x_i$ 表示第 $i$ 步的视觉游戏状态，用 $a_i$ 表示在该状态下执行的玩家动作。世界模型的核心任务是**学习条件分布**：

$$
p(x_{i+1}\mid x_{<i}, a_i)
$$

其中：

- $x_i$ 是 Minecraft 画面，经过预处理后是 $224\times384$ 的 RGB 图像。
- $a_i$ 是键盘和鼠标动作，包括前进、后退、左右移动、跳跃、攻击、使用、丢弃物品、相机转动等。
- $x_{<i}$ 表示历史视觉状态。
- $x_{i+1}$ 是执行动作 $a_i$ 后的下一视觉状态。

这个公式是理解 MineWorld 的核心。它说明 MineWorld 是在动作条件下预测下一帧。**动作条件**是 game world model 和普通 video generation 的关键区别。

## 3. 模型输入输出

### 3.1 原始输入

从数据层面看，MineWorld 的原始输入是一段 Minecraft 轨迹：

$$
(x_1,a_1,x_2,a_2,\cdots,x_n,a_n)
$$

其中每个 $x_i$ 是一帧游戏画面，每个 $a_i$ 是该时刻记录到的玩家动作。

源码中的本地推理入口是 `inference.py`。它读取：

- `.mp4` 视频文件，作为画面来源。
- `.jsonl` 动作文件，作为键鼠动作来源。

推理时，代码先读取若干初始帧，将其转为视觉 token，然后读取后续动作 token，再调用生成函数预测后续视觉 token。

### 3.2 视觉输入-> token：VQ-VAE 视觉 tokenizer

MineWorld 先使用 VQ-VAE 把图像压缩成离散 token。可以把 VQ-VAE 理解为 VAE 的离散化版本：普通 VAE 通常把图像压缩为连续潜变量，而 VQ-VAE 把图像压缩为 codebook 中的离散编号。对 MineWorld 来说，VQ-VAE 的作用就是视觉 tokenizer：它负责把 Minecraft 画面编码成视觉 token，也负责把生成出的视觉 token 解码回图像。

和普通 VAE 对比，可以这样理解：

| 对比项 | VAE | VQ-VAE |
|---|---|---|
| 潜变量类型 | 连续向量 | 离散 code id |
| encoder 输出 | 分布参数或连续 latent | 连续特征，再量化到 codebook |
| 中间表示 | $z$ | codebook index + codebook vector |
| 常见训练项 | 重建项 + KL 正则 | 重建项 + codebook loss + commitment loss |
| 对 MineWorld 的意义 | 不方便直接作为 token | 可以直接作为 Transformer token |

VQ-VAE 内部有一个可学习的 codebook：

$$
E=\{e_1,e_2,\cdots,e_K\}
$$

encoder 先把图像编码为连续特征 $z_e(x)$。对每个空间位置，VQ-VAE 会在 codebook 中寻找最近的向量：

$$
k=\arg\min_j \|z_e(x)_{i,j}-e_j\|_2
$$

然后用对应的 codebook 向量 $e_k$ 替换原来的连续特征。这里的 $k$ 就是视觉 token id。

论文和源码中的关键数字是：

- 原始处理分辨率：$224\times384$
- 空间压缩率：$16\times$
- token 网格大小：$14\times24$
- 每帧视觉 token 数量：$14\times24=336$
- 视觉 codebook 大小：$8192$

也就是说，一帧图像 $x_i$ 会被视觉 tokenizer 编码为：

$$
v_i=(v_{i,1},v_{i,2},\cdots,v_{i,336})
$$

其中每个 $v_{i,j}$ 都是一个离散 id，取值范围大致对应 $0$ 到 $8191$。

为什么这里不直接用普通 VAE？原因在于 MineWorld 后面的主模型是自回归 Transformer，它最自然的训练形式是分类式 next-token prediction：

$$
p(t_i\mid t_{<i})
$$

如果使用普通 VAE，图像会被压缩成连续 latent，Transformer 就需要回归连续向量，训练和采样都会更麻烦。VQ-VAE 直接输出离散 token id，使图像可以像文本一样被 Transformer 建模。

VQ-VAE 自身的训练目标通常包含三部分：

$$
\mathcal{L}_{\mathrm{VQ}}
=
\|x-\hat{x}\|^2
+
\|\mathrm{sg}[z_e(x)]-e\|^2
+
\beta\|z_e(x)-\mathrm{sg}[e]\|^2
$$

第一项让 decoder 能重建图像；第二项更新 codebook，使 codebook 向量靠近 encoder 输出；第三项约束 encoder，使它稳定地贴近某个 codebook 向量。这里 $\mathrm{sg}[\cdot]$ 表示 stop-gradient。

源码对应位置：

- `vae.py`：视觉 tokenizer 封装。
- `inference.py`：调用 `model.tokenizer.tokenize_images(frames)`。
- `configs/*.yaml`：VQ-VAE checkpoint 路径写在 `tokenizer_config` 里。

### 3.3 动作输入-> token

MineWorld 的动作 tokenizer 是理解可控性的关键。Minecraft 的动作既有离散键盘动作，也有连续鼠标视角变化。源码 `mcdataset.py` 中将动作转为长度为 11 的 token 序列。

动作 token 序列大致结构如下：

```text
[act_bos],
camera_y,
camera_x,
hotbar,
forward/back,
left/right,
sprint/sneak,
use/attack,
jump,
drop/pickItem,
[act_eos]
```

对应代码在 `MCDataset.get_action_index_from_actiondict()` 中。几个关键点：

- 相机移动是**连续值**，先通过 `CameraQuantizer` **离散化**。
- `forward/back`、`left/right`、`sprint/sneak`、`use/attack` 等动作按互斥关系处理。
- **如果互斥动作同时出现，代码会将该组动作归为 `<null_act>`。**
- 推理时动作 token 会通过 `action_vocab_offset=8192` 平移到视觉 token 之后的 id 区间。

论文和配置文件中给出的总词表大小是：

$$
8192 + 70 = 8262
$$

源码中 `make_action_vocab()` 默认构造的动作符号数量与论文表述略有版本差异，实际模型配置以 `vocab_size: 8262` 为准。这种差异通常意味着有少量预留 token 或代码版本与论文实验版本不完全一致，不影响理解主流程。

### 3.4 状态+动作->训练序列

每个状态-动作对会被拼成：

$$
s_i=[v_i, g(a_i)]
$$

其中 $v_i$ 是 $336$ 个视觉 token，$g(a_i)$ 是 $11$ 个动作 token。所以一个状态-动作对长度为：

$$
336+11=347
$$

如果一个训练样本包含 $16$ 个状态-动作对，则序列长度为：

$$
347\times16=5552
$$

这也对应源码配置文件中的 `max_position_embeddings: 5552`。

最终训练序列可以写为：

$$
T=[v_1,g(a_1),v_2,g(a_2),\cdots,v_n,g(a_n)]
$$

这是一种很重要的设计：MineWorld 把二者放进同一个 token 序列中，让 Transformer 学习二者之间的条件关系。

## 4. 训练目标

MineWorld 使用自回归 Transformer，训练方式和语言模型类似。给定 token 序列 $T=(t_1,t_2,\cdots,t_N)$，模型学习：

$$
p_\theta(T)=\prod_{i=1}^{N}p_\theta(t_i\mid t_{<i})
$$

对应的负对数似然损失可以写成：

$$
\mathcal{L}(\theta)=-\sum_{i=1}^{N}\log p_\theta(t_i\mid t_{<i})
$$

这就是 next-token prediction。区别在于，**语言模型的 token 是文字，而 MineWorld 的 token 同时包括视觉 token 和动作 token**。

需要区分两套训练目标：VQ-VAE 负责把图像压成离散视觉 token，它的目标是重建图像并学习稳定 codebook；Transformer 负责建模 token 序列，它的目标是预测下一个视觉 token 或动作 token。MineWorld 的世界动态主要由 Transformer 学习，VQ-VAE 则提供“图像 <-> token”的接口。

这个设计带来一个有趣结果：模型理论上既可以当 world model，也可以当 policy model。

- **当给定历史画面和动作，预测后续视觉 token 时，它是 world model。**
- 当给定历史画面和动作，让模型继续预测动作 token 时，它也可以表现得像 policy model。

论文主要关注前者，也就是动作条件下的未来画面生成。源码 `lvm.py` 中的 `naive_generate()` 和 `img_diagd_generate()` 对应推理阶段的视觉 token 生成。

## 5. 推理

以 `inference.py` 为例，推理流程可以概括为：

```text
1. 读取输入视频中的初始帧
2. 将初始帧归一化并送入 VQ-VAE
3. 得到初始视觉 token
4. 读取 jsonl 中的动作
5. 将动作转成 11 个 action token
6. 把视觉 token 和当前动作 token 拼接
7. Transformer 生成下一帧的 336 个视觉 token
8. 生成完一帧后插入下一步动作 token
9. 重复生成多帧
10. 用 VQ-VAE 解码器把视觉 token 还原为视频
```

用公式表示，若已有视觉 token $v_1$，并给定动作 $g(a_1)$，模型生成：

$$
\hat{v}_2 \sim p_\theta(v_2\mid v_1,g(a_1))
$$

接着插入下一个动作 $g(a_2)$，生成：

$$
\hat{v}_3 \sim p_\theta(v_3\mid v_1,g(a_1),\hat{v}_2,g(a_2))
$$

这就是自回归 rollout。它和真实游戏引擎的区别是：真实游戏引擎显式维护状态和物理规则，MineWorld 只在 token 序列中隐式学习状态转移规律。

## 6. 算法创新点

### 6.1 把 Minecraft 世界模型建成视觉-动作 token 序列模型

MineWorld 的第一点贡献是把 Minecraft 的画面和动作都离散化为 token，并用自回归 Transformer 统一建模。

这条路线和 diffusion-based world model 不同。Oasis 和 GameNGen 更接近扩散式视频/帧生成；MineWorld 更接近“视觉语言模型化”的路线，即把游戏世界转成 token 序列，然后用 next-token prediction 训练。

优点是结构清晰、可扩展性强、和大语言模型技术栈兼容。缺点是逐 token 生成很慢，所以需要后面的并行解码。

### 6.2 动作 tokenizer 直接服务于可控性

MineWorld 没有只用文本提示或粗粒度条件，而是把键鼠动作拆成离散 token。这样做的意义是：

- 模型能显式看到玩家动作。
- 不同动作组可以按互斥关系建模。
- 评估时可以用同样的动作分组计算分类指标。

这使得 MineWorld 的评估不只看画质，还能看“动作是否真的被执行”。

### 6.3 Diagonal Decoding 提升实时性

自回归模型的最大瓶颈是生成慢。一帧有 $336$ 个视觉 token，如果严格按光栅顺序逐个生成，需要 $336$ 次 token 预测。

MineWorld 采用 diagonal decoding，利用图像 token 的空间冗余，让多行的部分 token 同时生成。论文给出的理论加速比为：

$$
r=\frac{h\times w}{h+w-1}
$$

对于 MineWorld 的视觉 token 网格，$h=14$，$w=24$，理论加速比约为：

$$
\frac{14\times24}{14+24-1}=\frac{336}{37}\approx9.08
$$

实际实验中约获得 $3\times$ 级别加速。理论值和实测值不同，主要因为真实推理还包含 KV cache、动作插入、采样、解码器开销和 GPU kernel 开销。

源码对应：

- `diagonal_decoding.py`
- `img_diagd_decode_n_tokens()`
- `img_diagd_prepare_inputs()`
- `inference.py` 中参数 `--accelerate-algo image_diagd`

代码中默认 `rownum=14`、`columnnum=24`、`pixnum=336`、`actnum=11`，这些都和论文中的 token 设计对应。

### 6.4 用 IDM 评估动作可控性

MineWorld 另一个重要贡献是评估设计。传统视频指标如 FVD、PSNR、SSIM、LPIPS 只能说明视频像不像，不能说明动作有没有生效。

MineWorld 使用逆动力学模型 IDM 从生成帧中反推动作：

$$
\hat{a}_i = \mathrm{IDM}(\hat{x}_i,\hat{x}_{i+1})
$$

然后比较 $\hat{a}_i$ 和原始输入动作 $a_i$。如果两者一致，说明生成画面确实体现了输入动作。

这个思路对 game world model 很重要，因为可玩性首先依赖动作响应，而不是单帧画质。

## 7. 数据集使用

### 7.1 数据来源

MineWorld 使用 VPT 数据集。该数据集来自 Minecraft 游戏视频，并配有对应的键盘和鼠标动作。

论文中的处理方式包括：

- 过滤没有记录动作的帧。
- 过滤 GUI 打开时的帧。
- 将长视频切分为 $16$ 帧片段。
- 随机划分训练集、验证集和测试集。

### 7.2 数据规模

论文给出的规模是：

- 训练集：$10$M 个视频片段。
- 训练帧数：$160$M 帧。
- 验证集：$0.5$k 个片段。
- 测试集：$1$k 个片段。
- 每个训练样本：$16$ 个状态-动作对。
- 每帧视觉 token：$336$。
- 每个动作 token：$11$。
- 每个状态-动作对：$347$ token。
- 总训练 token 数：约 $55$B。

计算关系如下：

$$
10\text{M clips}\times 16\text{ frames}\times 347\text{ tokens}\approx55.5\text{B tokens}
$$

### 7.3 数据预处理的意义

将分辨率从 $360\times640$ 调整为 $224\times384$，主要是为了降低计算成本，同时保持宽高比。再经过 $16\times$ 空间压缩后，每帧只剩 $336$ 个视觉 token。

这是一个典型 trade-off：

- 分辨率越高，细节越多，但 token 数和推理成本更高。
- 分辨率越低，模型更容易训练和推理，但细节会损失。

这也解释了 MineWorld 的局限：它能生成可交互 Minecraft 画面，但画质和真实游戏引擎仍有差距。

## 8. 实验结果评估

### 8.1 评估指标分两类

MineWorld 同时评估视频质量和动作可控性。

#### 8.1.1 视频质量指标

设真实视频为 $X=(x_1,\cdots,x_T)$，生成视频为 $\hat{X}=(\hat{x}_1,\cdots,\hat{x}_T)$。MineWorld 源码 `metrics/common_metrics.py` 会把生成视频目录和真实视频目录中的 `.mp4` 读成张量，再计算 FVD、LPIPS、SSIM 和 PSNR，并对多个视频取平均。

**FVD**

FVD 的全称是 Fréchet Video Distance，用于衡量真实视频分布和生成视频分布之间的距离。它通常先用预训练视频特征提取器 $\phi(\cdot)$ 把每个视频映射为特征向量：

$$
f_i=\phi(X_i),\quad \hat{f}_i=\phi(\hat{X}_i)
$$

然后分别估计真实视频特征和生成视频特征的均值与协方差：

$$
\mu_r,\Sigma_r=\mathrm{MeanCov}(\{f_i\}),\quad
\mu_g,\Sigma_g=\mathrm{MeanCov}(\{\hat{f}_i\})
$$

FVD 的计算形式为：

$$
\mathrm{FVD}
=
\|\mu_r-\mu_g\|_2^2
+
\mathrm{Tr}\left(
\Sigma_r+\Sigma_g-2(\Sigma_r\Sigma_g)^{1/2}
\right)
$$

FVD 越低，说明生成视频的整体分布越接近真实视频。它比单帧指标更关注视频级特征，但仍不能直接说明动作是否被正确执行。

**PSNR**

PSNR 基于像素级均方误差。对一帧图像，先计算：

$$
\mathrm{MSE}(x,\hat{x})
=
\frac{1}{HWC}
\sum_{h=1}^{H}
\sum_{w=1}^{W}
\sum_{c=1}^{C}
\left(x_{h,w,c}-\hat{x}_{h,w,c}\right)^2
$$

再计算：

$$
\mathrm{PSNR}(x,\hat{x})
=
10\log_{10}
\frac{\mathrm{MAX}^2}{\mathrm{MSE}(x,\hat{x})}
$$

其中 $\mathrm{MAX}$ 是像素最大值。如果图像归一化到 $[0,1]$，则 $\mathrm{MAX}=1$；如果使用 $0$ 到 $255$ 的像素，则 $\mathrm{MAX}=255$。视频 PSNR 通常对所有帧和所有样本求平均。PSNR 越高，像素级误差越小。

**SSIM**

SSIM 衡量两张图像在亮度、对比度和结构上的相似性。对图像局部窗口，SSIM 可写为：

$$
\mathrm{SSIM}(x,\hat{x})
=
\frac{
(2\mu_x\mu_{\hat{x}}+C_1)(2\sigma_{x\hat{x}}+C_2)
}{
(\mu_x^2+\mu_{\hat{x}}^2+C_1)(\sigma_x^2+\sigma_{\hat{x}}^2+C_2)
}
$$

其中 $\mu_x,\mu_{\hat{x}}$ 是局部均值，$\sigma_x^2,\sigma_{\hat{x}}^2$ 是局部方差，$\sigma_{x\hat{x}}$ 是协方差，$C_1,C_2$ 是避免分母为零的常数。视频 SSIM 通常对窗口、帧和样本求平均。SSIM 越高，说明结构越接近真实视频。

**LPIPS**

LPIPS 衡量感知距离。它不是直接比较像素，而是把真实图像和生成图像送入预训练视觉网络，比较不同层的特征差异。设第 $l$ 层特征为 $\phi_l(x)$，归一化后的特征为 $\hat{\phi}_l(x)$，则一帧图像的 LPIPS 可写为：

$$
\mathrm{LPIPS}(x,\hat{x})
=
\sum_l
\frac{1}{H_lW_l}
\sum_{h,w}
\left\|
w_l\odot
\left(
\hat{\phi}_l(x)_{h,w}
-
\hat{\phi}_l(\hat{x})_{h,w}
\right)
\right\|_2^2
$$

其中 $w_l$ 是学习得到的层权重，$\odot$ 表示逐通道加权。LPIPS 越低，说明两张图在感知特征上越接近。

补充一点：视觉 tokenizer 重建实验中还报告了 FID。FID 与 FVD 形式类似，也是比较真实样本和生成样本特征分布的 Fréchet 距离；区别是 FID 通常使用图像特征，FVD 使用视频特征。

#### 8.1.2 动作可控性指标

动作可控性不是直接看画面像不像，而是看生成视频是否真的执行了输入动作。MineWorld 的做法是：先把生成视频送入逆动力学模型 IDM，由 IDM 从相邻帧中反推动作；再把 IDM 预测出的动作和原始输入动作比较。

设输入动作为 $a_t$，生成视频帧为 $\hat{x}_t,\hat{x}_{t+1}$，IDM 预测动作为：

$$
\tilde{a}_t
=
\mathrm{IDM}(\hat{x}_t,\hat{x}_{t+1})
$$

如果 $\tilde{a}_t$ 与原始输入动作 $a_t$ 一致，说明生成画面较好地遵循了控制信号。

**离散动作分类**

源码 `metrics/IDM/inverse_dynamics_model.py` 会把动作拆成若干互斥子任务：

- 三分类任务：`back/forward/null`、`left/right/null`、`sneak/sprint/null`。
- 二分类任务：`use/null`、`attack/null`、`jump/null`、`drop/null`。

对第 $m$ 个子任务，记真实标签为 $y_t^{(m)}$，IDM 预测标签为 $\hat{y}_t^{(m)}$。对某个类别 $c$，定义：

$$
\mathrm{TP}_c=\sum_t \mathbf{1}[\hat{y}_t=c \land y_t=c]
$$

$$
\mathrm{FP}_c=\sum_t \mathbf{1}[\hat{y}_t=c \land y_t\neq c]
$$

$$
\mathrm{FN}_c=\sum_t \mathbf{1}[\hat{y}_t\neq c \land y_t=c]
$$

则该类别的精确率和召回率为：

$$
\mathrm{Precision}_c
=
\frac{\mathrm{TP}_c}{\mathrm{TP}_c+\mathrm{FP}_c}
$$

$$
\mathrm{Recall}_c
=
\frac{\mathrm{TP}_c}{\mathrm{TP}_c+\mathrm{FN}_c}
$$

F1 分数为：

$$
\mathrm{F1}_c
=
\frac{
2\cdot\mathrm{Precision}_c\cdot\mathrm{Recall}_c
}{
\mathrm{Precision}_c+\mathrm{Recall}_c
}
$$

由于动作类别不均衡，论文更关心宏平均。对第 $m$ 个子任务，若类别数为 $C_m$，则：

$$
\mathrm{Precision}^{(m)}_{\mathrm{macro}}
=
\frac{1}{C_m}\sum_{c=1}^{C_m}\mathrm{Precision}_c
$$

$$
\mathrm{Recall}^{(m)}_{\mathrm{macro}}
=
\frac{1}{C_m}\sum_{c=1}^{C_m}\mathrm{Recall}_c
$$

$$
\mathrm{F1}^{(m)}_{\mathrm{macro}}
=
\frac{1}{C_m}\sum_{c=1}^{C_m}\mathrm{F1}_c
$$

最后再对所有子任务求平均。若共有 $M$ 个子任务：

$$
\mathrm{F1}_{\mathrm{action}}
=
\frac{1}{M}
\sum_{m=1}^{M}
\mathrm{F1}^{(m)}_{\mathrm{macro}}
$$

Precision 和 Recall 也按同样方式跨任务平均。源码里同时计算 micro 和 macro，最终 `metric_mean_on_task` 会把各子任务的结果再取平均。

**Camera L1**

相机移动是连续动作，因此先把相机的 $x/y$ 方向旋转量离散化为 bin。设真实相机动作为 $c_{t,d}$，IDM 预测相机动作为 $\tilde{c}_{t,d}$，其中 $d\in\{x,y\}$。令 $q(\cdot)$ 表示相机量化函数，则 Camera L1 为：

$$
\mathrm{CameraL1}
=
\frac{1}{2T}
\sum_{t=1}^{T}
\sum_{d\in\{x,y\}}
\left|
q(\tilde{c}_{t,d})-q(c_{t,d})
\right|
$$

源码中的 `camera_loss()` 正是先用 `CameraQuantizer` 将相机动作离散化，再计算预测 bin 和真实 bin 的平均绝对差。Camera L1 越低，说明生成视频对应的视角运动越接近输入动作。

### 8.2 视觉 tokenizer 的重建质量

MineWorld 的最终画质受两部分共同影响：一是 Transformer 是否预测了正确的未来视觉 token，二是 VQ-VAE decoder 是否能把这些 token 清晰地还原成图像。因此，论文附录单独报告了视觉 tokenizer 的重建质量。

微调前后 VQ-VAE 的指标如下：

| 视觉 tokenizer | PSNR | SSIM | LPIPS | FID |
|---|---:|---:|---:|---:|
| AMUSED | 25.91 | 0.758 | 0.238 | 35.05 |
| MineWorld 微调后 | 29.24 | 0.816 | 0.134 | 18.93 |

PSNR、SSIM 越高越好，LPIPS、FID 越低越好。四个指标同时改善，说明通用 VQ-VAE 直接用于 Minecraft 并不够理想，面向 Minecraft 数据进行视觉 tokenizer 适配是必要的。

### 8.3 与 Oasis 的主结果对比

论文主表的关键结果如下：

| 方法 | 参数量 | FPS | P | R | F1 | L1 | FVD | LPIPS | SSIM | PSNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Oasis | 500M | 2.58 | 0.49 | 0.44 | 0.41 | 2.60 | 377 | 0.53 | 0.36 | 14.38 |
| MineWorld | 300M | 5.91 | 0.72 | 0.71 | 0.70 | 1.03 | 246 | 0.45 | 0.38 | 15.13 |
| MineWorld | 700M | 3.18 | 0.72 | 0.71 | 0.70 | 1.04 | 231 | 0.44 | 0.38 | 15.32 |
| MineWorld | 1.2B | 3.01 | 0.76 | 0.73 | 0.73 | 1.02 | 227 | 0.44 | 0.41 | 15.69 |

可以读出几个结论：

1. MineWorld 的动作可控性明显好于 Oasis，尤其 F1 从 $0.41$ 提高到约 $0.70$ 到 $0.73$。
2. MineWorld 的视频质量也更好，FVD 更低，PSNR 更高。
3. 300M 模型最快，达到 $5.91$ FPS。
4. 1.2B 模型质量最好，但速度低于 300M。
5. 模型规模变大后，质量和可控性提升，但速度下降。

这里的“实时”不能理解成传统游戏引擎的 $60$ FPS。论文把实时交互和 APM 联系起来：$2$ FPS 大致可以跟上业余玩家，$5$ FPS 可接近职业玩家的高频操作。因此 MineWorld 的实时性是“低帧率交互实时”，不是完整游戏渲染实时。

### 8.4 并行解码实验

论文比较了普通自回归解码和并行解码：

| 参数量 | 解码方式 | FPS | F1 | PSNR | FVD |
|---|---|---:|---:|---:|---:|
| 300M | AT | 2.00 | 0.70 | 15.63 | 223 |
| 300M | 并行 w/ FT | 5.91 | 0.70 | 15.13 | 246 |
| 300M | 并行 w/o FT | 5.91 | 0.69 | 14.98 | 275 |
| 700M | AT | 1.08 | 0.73 | 15.74 | 210 |
| 700M | 并行 w/ FT | 3.18 | 0.71 | 15.32 | 231 |
| 700M | 并行 w/o FT | 3.18 | 0.70 | 15.27 | 247 |
| 1.2B | AT | 0.89 | 0.72 | 16.06 | 203 |
| 1.2B | 并行 w/ FT | 3.01 | 0.73 | 15.69 | 227 |
| 1.2B | 并行 w/o FT | 3.01 | 0.70 | 15.30 | 258 |

这张表的重点不是“并行解码全指标更好”，而是：

- 并行解码用少量质量损失换取明显速度提升。
- 使用 parallel attention mask 微调后，质量损失更小。
- 1.2B 模型在并行解码下仍保持较好的 F1，说明更大模型对解码方式变化更稳健。

### 8.5 人类评估和自动指标相关性

论文还用人类评分验证自动可控性指标。实验抽取 $20$ 个测试片段，邀请 $5$ 名有经验的玩家评分，计算自动 F1 与人类评分的相关性：

- 平均 F1：$0.81$
- 人类评分：$4.21$
- 皮尔逊相关系数：$r=0.56$
- p-value：$0.01$

这说明基于 IDM 的可控性指标和人类主观判断有一定正相关。它不是完美指标，但比只看 FVD/PSNR 更接近交互世界模型的核心需求。

## 9. 源码和论文模块对应关系

| 论文内容 | 源码位置 | 作用 |
|---|---|---|
| 项目说明、推理命令、checkpoint 结构 | `README.md` | 说明安装、推理、评估流程 |
| 模型配置 | `configs/*.yaml` | 记录模型规模、词表大小、最大序列长度、VQ-VAE checkpoint 路径 |
| 视觉 tokenizer / VQ-VAE | `vae.py`, `configs/*.yaml` | 将图像编码为 $14\times24$ 个视觉 token，并将生成 token 解码回图像 |
| 动作 tokenizer 与数据读取 | `mcdataset.py` | jsonl 动作转 11 个 action token |
| Transformer 主体 | `lvm.py` | LLaMA 风格自回归模型和生成函数 |
| Diagonal Decoding | `diagonal_decoding.py` | 并行解码实现 |
| 离线推理 | `inference.py` | 读取视频和动作，生成输出视频 |
| Web demo | `mineworld.py` | 交互式网页 demo |
| 视频质量指标 | `metrics/common_metrics.py` | FVD、LPIPS、SSIM、PSNR |
| 动作可控性指标 | `metrics/IDM/` | IDM 反推动作，计算分类指标和 camera loss |
| 批量推理脚本 | `scripts/inference_16f_models.sh` | 复现实验推理命令示例 |
| 指标计算脚本 | `scripts/compute_metrics.sh` | 复现实验指标计算 |

## 10. 复现角度的关键信息

源码 README 推荐 Python 3.10，主要依赖包括：

- `torch==2.6.0`
- `torchvision==0.21.0`
- `transformers==4.48.1`
- `diffusers==0.32.2`
- `gradio==5.24.0`
- `opencv-python==4.11.0.86`
- `scikit-learn==1.6.1`

README 明确说开发和测试使用 A100/H100。对于个人设备，建议分层理解复现难度：

1. 阅读代码和跑通环境：可行。
2. 使用已有 checkpoint 做少量推理：取决于 checkpoint 是否能下载以及本地 GPU 显存。
3. 复现实验表格：需要验证集、IDM 权重、MineWorld checkpoint 和较强 GPU。
4. 重新训练 300M/700M/1.2B 模型：个人设备基本不现实，因为训练数据约 $55$B token，论文使用 $32$ 张 40G A100 训练 $200$k 步。

另一个现实问题是 README 的 News 提到模型 checkpoint 曾在 Hugging Face 仓库临时下架。因此实际复现时要先确认 checkpoint 是否可用。

## 11. 局限性和研究启发

### 11.1 局限性

MineWorld 的局限主要有：

- 只在 Minecraft 域训练，不能直接泛化到其他游戏或互联网视频。
- 分辨率固定为 $224\times384$，细节有限。
- 上下文长度有限，16 帧模型最大序列长度约 $5552$ token。
- 长程一致性没有彻底解决，例如长时间返回同一地点、库存状态、实体状态可能漂移。
- 生成速度离传统游戏引擎仍有距离。
- 可控性评估依赖 IDM，IDM 自身错误会影响指标可靠性。
- 模型训练成本高，个人设备很难完整复现。

### 11.2 对 game world model 研究的启发

如果把 MineWorld 放到 game world model 方向里，它最有价值的启发有四点：

1. **动作表示很重要。**  
   不是所有控制信号都应该简单拼成一个向量。把动作结构化为 token，有利于生成和评估。

2. **视频质量指标不够。**  
   Game world model 必须评价动作响应、可控性、长程一致性和可玩性。

3. **实时性是核心约束。**  
   自回归 Transformer 质量不错，但推理慢。Diagonal decoding 说明模型结构之外的解码策略也能成为创新点。

4. **Minecraft 是很好的中间难度平台。**  
   它比 Atari/DOOM 更开放，比真实机器人或真实世界视频更可控，适合作为 game world model 的研究平台。

## 12. 后续建议的理解顺序

建议后续按下面顺序继续深入：

1. 先彻底理解输入输出：$x_i$、$a_i$、视觉 token、动作 token、序列长度。
2. 再理解训练目标：为什么 next-token prediction 能学习世界动态。
3. 继续看 `mcdataset.py`：动作 token 是如何构造的。
4. 再看 `inference.py`：推理时动作如何插入，视觉 token 如何生成。
5. 再看 `diagonal_decoding.py`：并行解码为什么能提速。
6. 最后看 `metrics/IDM`：可控性指标如何计算。

如果要从研究选题角度继续，可以重点追问：

- MineWorld 的动作 tokenizer 是否还有改进空间？
- Diagonal decoding 是否会破坏长程一致性？
- 是否能设计比 IDM 更直接的可控性评估？
- 如何在个人设备上做一个更小规模的 MineWorld-like 系统？
- 如何把 MineWorld 的 token world model 和 Dreamer/agent training 结合？
- 如何评价 Minecraft 世界模型的长期记忆和空间一致性？
