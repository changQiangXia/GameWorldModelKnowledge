# 个人设备上的 Mini MineWorld-like 系统设计草案

本文档记录一个面向个人设备的小规模 MineWorld-like 系统方案。目标不是复刻 MineWorld 的 Minecraft 大模型，而是复刻它的研究闭环：

```text
游戏轨迹数据
-> 视觉 token 化
-> 动作 token 化
-> action-conditioned autoregressive world model
-> 生成未来画面
-> 视频质量 + 动作可控性评估
```

## 1. 核心目标

个人设备版 MineWorld-like 系统建议定义为：

```text
在小型视觉游戏环境中，学习一个动作条件视觉世界模型：
给定当前/历史画面和动作序列，生成未来若干帧，并用视频质量和动作可控性共同评估。
```

对应的建模目标是：

$$
p(v_{t+1}\mid v_{\le t}, a_t)
$$

其中：

- $x_t$ 表示第 $t$ 帧游戏画面。
- $v_t$ 表示 VQ-VAE 编码得到的视觉 token。
- $a_t$ 表示第 $t$ 步玩家动作。
- $p(v_{t+1}\mid v_{\le t}, a_t)$ 表示在历史视觉 token 和当前动作条件下预测下一帧视觉 token。

第一版不追求“能玩 Minecraft 的神经游戏引擎”，而是证明一个更小但明确的命题：

```text
在小型视觉游戏环境中，显式动作 token 能提升未来画面生成的可控性。
```

## 2. 为什么不直接复现 MineWorld

MineWorld 原始系统包含 Minecraft 轨迹、大规模 VPT 数据、VQ-VAE visual tokenizer、自回归 Transformer、diagonal decoding、IDM 评估等模块。完整复现的问题是：

- Minecraft 数据和动作空间复杂。
- 原论文训练数据约 $55$B token。
- 模型规模包含 $300$M、$700$M、$1.2$B。
- 训练使用多张 A100 级 GPU。
- 真实 checkpoint 和数据准备可能存在额外工程障碍。

个人设备上更合理的路线是：

```text
不缩小 MineWorld 的参数量，而是缩小 MineWorld 的研究闭环。
```

也就是说，保留关键思想，降低环境复杂度、分辨率、token 数、模型规模和 rollout 长度。

## 3. 第一版推荐方案

建议第一版使用 ViZDoom，而不是 Minecraft。

| 模块 | 第一版选择 |
|---|---|
| 环境 | ViZDoom |
| 图像分辨率 | $64\times64$ |
| 视觉 tokenizer | 小型 VQ-VAE |
| token grid | $8\times8$ |
| 每帧视觉 token | $64$ |
| codebook size | $512$ |
| 动作空间 | 5 类 |
| 动作 token | 每步 1 个 action token |
| 上下文长度 | 8 帧 |
| token 序列长度 | $8\times(64+1)=520$ |
| world model | 10M 到 30M 参数的小 GPT |
| rollout 长度 | 1 / 5 / 10 / 20 步 |
| 评估 | PSNR、SSIM、LPIPS、IDM Acc、IDM F1 |

5 类动作建议为：

```text
0: NOOP
1: MOVE_FORWARD
2: TURN_LEFT
3: TURN_RIGHT
4: ATTACK
```

后续可扩展为组合动作，例如：

```text
MOVE_FORWARD + TURN_LEFT
MOVE_FORWARD + TURN_RIGHT
MOVE_FORWARD + ATTACK
```

但第一版先保持动作空间小，便于训练 world model 和 IDM。

## 4. 系统总体架构

第一版系统结构如下：

```text
ViZDoom frame
  -> VQ-VAE encoder
  -> visual tokens

ViZDoom action
  -> action tokenizer
  -> action token

visual tokens + action token
  -> small autoregressive Transformer
  -> future visual tokens

future visual tokens
  -> VQ-VAE decoder
  -> generated frame/video

generated video + input actions
  -> video quality metrics + IDM controllability metrics
```

核心模块包括：

1. 数据采集器：从 ViZDoom 中采集 frame-action 轨迹。
2. 视觉 tokenizer：小型 VQ-VAE，将图像压成离散视觉 token。
3. 动作 tokenizer：将离散动作映射为 action token。
4. 自回归 world model：小 GPT，学习动作条件下的视觉 token 动态。
5. rollout 生成器：给定初始帧和动作序列，生成未来视频。
6. IDM evaluator：从生成帧对中反推动作，评估动作可控性。
7. 视频质量 evaluator：计算 PSNR、SSIM、LPIPS 等指标。

## 5. 数据采集方案

数据格式建议为：

```text
episode_000/
  frames.npy
  actions.npy

episode_001/
  frames.npy
  actions.npy
```

每条轨迹包含：

$$
(x_1,a_1,x_2,a_2,\cdots,x_T,a_T)
$$

采集策略不建议完全随机。完全随机轨迹容易出现大量撞墙、原地旋转或无意义动作。建议使用带规则的随机策略：

```text
大概率前进
小概率转向
看到敌人时提高攻击概率
卡住时增加转向概率
```

数据规模分阶段推进：

| 阶段 | 帧数 | 用途 |
|---|---:|---|
| smoke test | 5k 到 10k | 检查环境、保存格式、回放和动作对齐 |
| 小实验 | 50k 到 100k | 初步训练 VQ-VAE 和 world model |
| 正式第一版 | 300k 到 500k | 跑完整指标和对照实验 |
| 扩展版 | 1M+ | 做更多 ablation 和稳定性分析 |

数据划分应按 episode 进行：

```text
train episodes
val episodes
test episodes
```

不要按帧随机划分。否则相邻帧可能同时出现在训练集和测试集，导致评估虚高。

## 6. 视觉 tokenizer：小型 VQ-VAE

第一版 VQ-VAE 规格建议：

```text
输入分辨率：64×64
token grid：8×8
每帧 token 数：64
codebook size：512
embedding dim：64 或 128
encoder/decoder：小 CNN
```

VQ-VAE 的作用是：

```text
frame x_t -> visual tokens v_t
visual tokens v_t -> reconstructed frame x_hat_t
```

VQ-VAE 训练目标通常包含：

$$
\mathcal{L}_{\mathrm{VQ}}
=
\|x-\hat{x}\|^2
+
\|\mathrm{sg}[z_e(x)]-e\|^2
+
\beta\|z_e(x)-\mathrm{sg}[e]\|^2
$$

其中：

- $\|x-\hat{x}\|^2$ 是重建损失。
- $\|\mathrm{sg}[z_e(x)]-e\|^2$ 用于更新 codebook。
- $\beta\|z_e(x)-\mathrm{sg}[e]\|^2$ 是 commitment loss。
- $\mathrm{sg}[\cdot]$ 表示 stop-gradient。

VQ-VAE 验收标准：

```text
重建图像能看出墙、敌人、武器、方向。
连续帧重建不严重闪烁。
codebook usage 不严重塌缩。
token grid 解码后不全是平均色块。
```

codebook usage 可定义为：

$$
\mathrm{usage}
=
\frac{|\{k: k\ \text{被至少使用过}\}|}{K}
$$

其中 $K$ 是 codebook size。若 $K=512$，但实际只用了几十个 code，则说明可能存在 codebook collapse。

## 7. 动作 tokenizer

第一版不需要复刻 MineWorld 复杂的键鼠动作 tokenizer。若动作空间为：

$$
\mathcal{A}
=
\{\mathrm{NOOP},\mathrm{FORWARD},\mathrm{LEFT},\mathrm{RIGHT},\mathrm{ATTACK}\}
$$

则动作 tokenizer 可以直接写成：

$$
g(a_t)=|\mathcal{V}|+\mathrm{id}(a_t)
$$

其中：

- $|\mathcal{V}|$ 是视觉 codebook size，例如 $512$。
- $\mathrm{id}(a_t)$ 是动作类别编号。
- $g(a_t)$ 是动作 token id。

这样总词表大小为：

$$
|\mathcal{V}|+|\mathcal{A}|=512+5=517
$$

序列格式建议贴近 MineWorld：

```text
v_1 tokens, a_1,
v_2 tokens, a_2,
...
v_t tokens, a_t
```

如果每帧 64 个视觉 token，每个动作 1 个 token，则每个状态-动作对长度为：

$$
64+1=65
$$

8 帧上下文长度为：

$$
8\times65=520
$$

## 8. World Model：小型自回归 Transformer

第一版 world model 使用小 GPT 即可。推荐配置：

```yaml
vocab_size: 517
context_length: 520
n_layer: 6
n_head: 8
n_embd: 384
dropout: 0.1
```

更保守的配置：

```yaml
vocab_size: 517
context_length: 520
n_layer: 4
n_head: 4
n_embd: 256
dropout: 0.1
```

训练序列：

$$
T=[v_1,g(a_1),v_2,g(a_2),\cdots,v_n,g(a_n)]
$$

标准自回归目标为：

$$
p_\theta(T)
=
\prod_i p_\theta(t_i\mid t_{<i})
$$

但第一版建议只对 visual token 计算 loss，动作 token 只作为条件：

$$
\mathcal{L}_{\mathrm{WM}}
=
-
\sum_{i\in\mathcal{V}_{pos}}
\log p_\theta(t_i\mid t_{<i})
$$

其中 $\mathcal{V}_{pos}$ 表示视觉 token 的位置集合。

这样第一版目标更清晰：

```text
根据历史画面和动作预测未来画面。
```

等系统跑通后，再尝试对 action token 也计算 loss，让模型同时具备 policy-like 预测能力。

## 9. 推理与 rollout

推理输入：

```text
初始真实帧 x_1
动作序列 a_1, a_2, ..., a_K
```

推理流程：

```text
x_1 -> VQ-VAE encoder -> v_1
拼接 v_1, a_1
Transformer 生成 v_2
拼接 v_2, a_2
Transformer 生成 v_3
...
VQ-VAE decoder 解码所有生成 token
输出视频
```

公式上可以写为：

$$
\hat{v}_{t+1}
\sim
p_\theta(v_{t+1}\mid v_{\le t}, g(a_t))
$$

rollout 长度建议分开评估：

```text
1-step
5-step
10-step
20-step
```

不要只报一个平均结果。自回归 world model 的误差会随 rollout 长度累积，分长度评估可以展示模型稳定性。

## 10. 视频质量评估

第一版至少保留：

- PSNR
- SSIM
- LPIPS

如果工程允许，再加入 FVD。

PSNR 衡量像素级误差：

$$
\mathrm{PSNR}(x,\hat{x})
=
10\log_{10}
\frac{\mathrm{MAX}^2}{\mathrm{MSE}(x,\hat{x})}
$$

SSIM 衡量结构相似性：

$$
\mathrm{SSIM}(x,\hat{x})
=
\frac{
(2\mu_x\mu_{\hat{x}}+C_1)(2\sigma_{x\hat{x}}+C_2)
}{
(\mu_x^2+\mu_{\hat{x}}^2+C_1)(\sigma_x^2+\sigma_{\hat{x}}^2+C_2)
}
$$

LPIPS 衡量感知特征距离：

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

这些指标能衡量画面是否接近真实视频，但不能说明模型是否正确响应动作。因此必须加入动作可控性评估。

## 11. 动作可控性评估：小型 IDM

训练一个小型 inverse dynamics model：

$$
\mathrm{IDM}(x_t,x_{t+1})\to a_t
$$

可以用简单 CNN 实现：

```text
concat(frame_t, frame_{t+1})
-> Small CNN
-> MLP
-> action logits
```

如果输入两帧 RGB 图像，可以直接拼成 6 通道输入：

```text
[RGB_t, RGB_{t+1}]
```

IDM 训练目标：

$$
\mathcal{L}_{\mathrm{IDM}}
=
-
\sum_t
\log p_\psi(a_t\mid x_t,x_{t+1})
$$

对生成视频，先由 IDM 反推动作：

$$
\tilde{a}_t
=
\mathrm{IDM}(\hat{x}_t,\hat{x}_{t+1})
$$

再与输入动作 $a_t$ 比较，计算：

- Accuracy
- Precision
- Recall
- F1
- confusion matrix

IDM 必须先在真实测试视频上验证。建议门槛：

```text
IDM 在真实 test split 上 accuracy > 80%
```

如果达不到，说明动作空间太复杂、数据不足或 IDM 太弱，此时不应直接用它评价生成视频。

## 12. 必做 baseline

为了证明系统不是普通视频预测，必须做对照实验。

### 12.1 Copy-last-frame

直接复制上一帧：

$$
\hat{x}_{t+1}=x_t
$$

这个 baseline 很重要，因为短期视频预测中复制上一帧可能得到不错的 PSNR/SSIM。

### 12.2 No-action Transformer

不输入动作：

$$
p(v_{t+1}\mid v_{\le t})
$$

它用于检验动作 token 是否真的有帮助。

### 12.3 Action-conditioned Transformer

输入正确动作：

$$
p(v_{t+1}\mid v_{\le t},a_t)
$$

这是主模型。

### 12.4 Shuffled-action eval

评估时打乱动作：

$$
p(v_{t+1}\mid v_{\le t},a_{\pi(t)})
$$

如果打乱动作后 IDM F1 没有明显下降，说明模型可能没有真正利用动作。

## 13. 关键实验表

### 13.1 动作条件是否有用

最重要的实验表：

| 模型 | 输入动作 | PSNR | SSIM | LPIPS | IDM Acc | IDM F1 |
|---|---|---:|---:|---:|---:|---:|
| Copy last frame | 无 | ? | ? | ? | ? | ? |
| No-action GPT | 无 | ? | ? | ? | ? | ? |
| Action GPT | 正确动作 | ? | ? | ? | ? | ? |
| Action GPT | 打乱动作 | ? | ? | ? | ? | ? |

核心结论应当是：

```text
Action GPT 在 IDM Acc/F1 上明显高于 No-action GPT 和 Shuffled-action。
```

### 13.2 rollout 稳定性

按 rollout 长度分别评估：

| rollout length | PSNR | SSIM | LPIPS | IDM F1 |
|---:|---:|---:|---:|---:|
| 1 | ? | ? | ? | ? |
| 5 | ? | ? | ? | ? |
| 10 | ? | ? | ? | ? |
| 20 | ? | ? | ? | ? |

这张表用于观察误差随生成长度的累积。

### 13.3 视觉 token 粒度

比较不同视觉 tokenizer 设置：

| Token grid | Codebook | 每帧 token | 画质 | 训练成本 | 可控性 |
|---|---:|---:|---|---|---|
| $8\times8$ | 256 | 64 | ? | 低 | ? |
| $8\times8$ | 512 | 64 | ? | 低 | ? |
| $16\times16$ | 512 | 256 | ? | 高 | ? |
| $16\times16$ | 1024 | 256 | ? | 更高 | ? |

这个实验回答：

```text
更细的视觉 token 是否一定带来更好的 world model？
```

不一定。更细 token 可能提升画质，但也会增加序列长度，使 Transformer 更难学习动态。

### 13.4 上下文长度

比较：

```text
context = 2 / 4 / 8 / 16 frames
```

观察：

- 短期生成质量。
- 长期 rollout 漂移。
- IDM F1。
- 推理速度。
- 显存占用。

## 14. 动作敏感性测试

除了 IDM，还可以做一个动作敏感性测试。

给定同一个初始画面，输入不同动作：

```text
x_0 + FORWARD
x_0 + TURN_LEFT
x_0 + TURN_RIGHT
x_0 + ATTACK
```

生成 5 步后比较不同动作生成结果的差异：

$$
D_{\mathrm{action}}
=
\frac{1}{|\mathcal{A}|(|\mathcal{A}|-1)}
\sum_{a\neq a'}
d(G(x_0,a),G(x_0,a'))
$$

其中：

- $G(x_0,a)$ 表示从同一初始画面 $x_0$ 出发，在动作 $a$ 条件下生成的结果。
- $d(\cdot,\cdot)$ 可以使用 LPIPS 或特征距离。

这个指标不能说明动作响应是否正确，但能说明模型是否对动作敏感。如果 $D_{\mathrm{action}}$ 很低，说明不同动作生成结果几乎一样，模型可能忽略了 action token。

## 15. 项目目录建议

建议从零写一个轻量版，不要直接改 MineWorld 源码。目录结构可以设计为：

```text
mini_mineworld/
  configs/
    vqvae_64.yaml
    wm_20m.yaml
    idm_small.yaml

  data/
    raw/
    processed/
    splits/

  scripts/
    collect_data.py
    train_vqvae.py
    encode_dataset.py
    train_world_model.py
    rollout.py
    train_idm.py
    evaluate.py

  miniwm/
    envs/
    datasets/
    models/
      vqvae.py
      transformer.py
      idm.py
    tokenizers/
      action_tokenizer.py
    metrics/
      video_quality.py
      controllability.py
    utils/

  outputs/
    reconstructions/
    rollouts/
    metrics/
    checkpoints/
```

最小命令链：

```bash
python scripts/collect_data.py
python scripts/train_vqvae.py
python scripts/encode_dataset.py
python scripts/train_world_model.py
python scripts/rollout.py
python scripts/train_idm.py
python scripts/evaluate.py
```

每一步产物：

| 步骤 | 产物 |
|---|---|
| collect_data | frames/actions |
| train_vqvae | vqvae.ckpt + reconstruction samples |
| encode_dataset | token dataset |
| train_world_model | world_model.ckpt |
| rollout | generated videos |
| train_idm | idm.ckpt |
| evaluate | metrics.csv |

## 16. 时间安排

如果目标是做出第一个可展示版本，可以按 4 到 6 周安排。

### 第 1 周：环境和数据

```text
搭 ViZDoom
定义动作空间
采集 10k/100k 帧
写回放脚本
检查动作分布
```

### 第 2 周：VQ-VAE

```text
训练 64×64 VQ-VAE
看 reconstruction
监控 codebook usage
导出 token dataset
```

### 第 3 周：World Model

```text
训练小 GPT
先做 teacher forcing validation loss
再做 1-step/5-step rollout
```

### 第 4 周：IDM 和评估

```text
训练 IDM
计算 PSNR/SSIM/LPIPS
计算 IDM Acc/F1
做 action/no-action baseline
```

### 第 5 到 6 周：改进和实验表

```text
调 codebook size
调 context length
调 model size
补 rollout length 曲线
整理失败案例
```

## 17. 风险和应对

| 风险 | 表现 | 应对 |
|---|---|---|
| VQ-VAE 重建差 | 画面糊、主体不可辨认 | 先调 VQ-VAE，不急着训 world model |
| codebook collapse | 只使用少量 code | 监控 usage，调 codebook loss、commitment loss、学习率 |
| 动作分布不均衡 | 大量 NOOP/FORWARD | 采集时控制动作比例或重采样 |
| 模型忽略动作 | 换动作生成差别小 | 做 no-action 和 shuffled-action baseline |
| rollout 快速漂移 | 10-step 后崩坏 | 分 1/5/10/20 step 评估，先优化短 rollout |
| IDM 不准 | 真实视频上动作识别差 | 简化动作空间或增强 IDM |
| 只看画质 | PSNR 高但不可控 | 必须保留 IDM Acc/F1 |

## 18. 第一版成败标准

第一版成功不等于生成高清游戏画面，而是满足：

```text
VQ-VAE 能重建出可辨认游戏画面。
codebook 没有严重 collapse。
IDM 在真实测试集上动作识别准确率 > 80%。
Action GPT 的 IDM F1 明显高于 No-action GPT。
打乱动作后 IDM F1 明显下降。
10-step rollout 还能保持基本场景结构。
同一初始帧输入不同动作，生成结果有可见差异。
```

满足这些，就可以说个人设备版 MineWorld-like 系统成立。

## 19. 后续升级路线

第一版跑通后，再按顺序升级：

```text
ViZDoom 64×64
-> ViZDoom 128×128
-> 更细 token grid：8×8 -> 16×16
-> 更复杂动作 tokenizer
-> 更长上下文：8 -> 16 帧
-> 加 FVD 和动作敏感性指标
-> Crafter
-> Minecraft 小子集
-> diagonal/block decoding
```

不要反过来。先上 Minecraft、长上下文、大模型、diagonal decoding，工程风险会太高。

## 20. 可能形成的研究题目

建议将研究问题凝练为：

```text
视觉 token 粒度和动作条件如何影响小型 game world model 的可控性与 rollout 稳定性？
```

可实验变量：

| 变量 | 可选值 |
|---|---|
| token grid | $8\times8$ vs $16\times16$ |
| codebook size | 256 / 512 / 1024 |
| context length | 4 / 8 / 16 |
| action conditioning | no-action / correct-action / shuffled-action |
| rollout length | 1 / 5 / 10 / 20 |

观察指标：

```text
PSNR
SSIM
LPIPS
IDM Acc
IDM F1
rollout FPS
codebook usage
```

更进一步的研究方向：

```text
1. 小数据条件下的 action-conditioned game world model
2. 面向个人设备的轻量级视觉 tokenizer
3. game world model 的动作可控性评估
4. 长程 rollout 中的空间一致性保持
5. structured action tokenizer 对交互式世界模型的影响
6. VQ token 粒度对游戏世界建模的影响
```

最适合第一阶段切入的是：

```text
VQ token 粒度 + action conditioning + controllability evaluation
```

这三个点既贴近 MineWorld，又能在个人设备上做实验。
