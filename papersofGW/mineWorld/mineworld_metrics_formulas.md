# MineWorld 指标公式补充

本文档单独整理 MineWorld 中“视频质量指标”和“动作可控性指标”的计算方式，便于后续复现和阅读论文时对照。内容主要对应：

- 论文 `mineWorld.pdf` 的 Section 3.2 Evaluation Metrics 与 Appendix A.1。
- 源码 `mineworld-main/metrics/common_metrics.py`。
- 源码 `mineworld-main/metrics/IDM/inverse_dynamics_model.py`。
- 源码 `mineworld-main/metrics/IDM/lib/actions.py`。

## 1. 评估数据与符号

设真实视频集合为：

$$
\mathcal{D}_r=\{X_i\}_{i=1}^{N}
$$

生成视频集合为：

$$
\mathcal{D}_g=\{\hat{X}_i\}_{i=1}^{N}
$$

其中第 $i$ 个真实视频和生成视频分别为：

$$
X_i=(x_{i,1},x_{i,2},\cdots,x_{i,T})
$$

$$
\hat{X}_i=(\hat{x}_{i,1},\hat{x}_{i,2},\cdots,\hat{x}_{i,T})
$$

$x_{i,t}$ 表示真实第 $t$ 帧，$\hat{x}_{i,t}$ 表示生成第 $t$ 帧。MineWorld 的源码评估中，`common_metrics.py` 默认最多取 $500$ 个视频，每个视频取 $15$ 帧，图像尺寸调整为 $224\times384$，并把像素归一化到 $[0,1]$。

因此，视频质量评估可以理解为比较：

$$
X_i \quad \text{vs.} \quad \hat{X}_i
$$

动作可控性评估可以理解为比较：

$$
a_{i,t} \quad \text{vs.} \quad \tilde{a}_{i,t}
$$

其中 $a_{i,t}$ 是 jsonl 文件中记录的真实输入动作，$\tilde{a}_{i,t}$ 是 IDM 从生成视频中反推出的动作。

## 2. 视频质量指标

MineWorld 使用的主要视频质量指标包括 FVD、PSNR、SSIM 和 LPIPS。这些指标衡量“生成视频是否像真实视频”，但不能直接说明“输入动作是否被正确执行”。

### 2.1 PSNR

PSNR 基于像素级均方误差。对第 $i$ 个视频的第 $t$ 帧，先计算 MSE：

$$
\mathrm{MSE}_{i,t}
=
\frac{1}{HWC}
\sum_{h=1}^{H}
\sum_{w=1}^{W}
\sum_{c=1}^{C}
\left(
x_{i,t,h,w,c}
-
\hat{x}_{i,t,h,w,c}
\right)^2
$$

其中 $H$、$W$、$C$ 分别是图像高度、宽度和通道数。

然后计算单帧 PSNR：

$$
\mathrm{PSNR}_{i,t}
=
10\log_{10}
\frac{\mathrm{MAX}^2}{\mathrm{MSE}_{i,t}}
$$

$\mathrm{MAX}$ 是像素最大值。如果图像已经归一化到 $[0,1]$，则 $\mathrm{MAX}=1$；如果使用 $0$ 到 $255$ 的像素值，则 $\mathrm{MAX}=255$。

数据集级 PSNR 通常对所有视频、所有帧取平均：

$$
\mathrm{PSNR}
=
\frac{1}{NT}
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathrm{PSNR}_{i,t}
$$

PSNR 越高，表示像素级误差越小。它对模糊、细节缺失、轻微错位比较敏感，但不一定符合人的主观感知。

### 2.2 SSIM

SSIM 衡量两张图像在亮度、对比度和结构上的相似性。对局部窗口中的真实图像 $x$ 和生成图像 $\hat{x}$，SSIM 可写为：

$$
\mathrm{SSIM}(x,\hat{x})
=
\frac{
(2\mu_x\mu_{\hat{x}}+C_1)
(2\sigma_{x\hat{x}}+C_2)
}{
(\mu_x^2+\mu_{\hat{x}}^2+C_1)
(\sigma_x^2+\sigma_{\hat{x}}^2+C_2)
}
$$

其中：

- $\mu_x$ 和 $\mu_{\hat{x}}$ 是局部均值，反映亮度。
- $\sigma_x^2$ 和 $\sigma_{\hat{x}}^2$ 是局部方差，反映对比度。
- $\sigma_{x\hat{x}}$ 是局部协方差，反映结构相似性。
- $C_1$ 和 $C_2$ 是稳定项，用于避免分母接近 $0$。

对第 $i$ 个视频第 $t$ 帧，可以写作：

$$
\mathrm{SSIM}_{i,t}
=
\mathrm{SSIM}(x_{i,t},\hat{x}_{i,t})
$$

数据集级 SSIM 通常为：

$$
\mathrm{SSIM}
=
\frac{1}{NT}
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathrm{SSIM}_{i,t}
$$

SSIM 越高，表示结构越接近真实图像。相比 PSNR，SSIM 更关心局部结构，而不是单纯的像素误差。

### 2.3 LPIPS

LPIPS 是感知距离指标。它不直接比较像素，而是把真实图像和生成图像送入预训练视觉网络，比较多层特征差异。

设第 $l$ 层特征为 $\phi_l(x)$，归一化后的特征为 $\hat{\phi}_l(x)$，第 $l$ 层的空间尺寸为 $H_l\times W_l$，则单帧 LPIPS 可写为：

$$
\mathrm{LPIPS}(x,\hat{x})
=
\sum_l
\frac{1}{H_lW_l}
\sum_{h=1}^{H_l}
\sum_{w=1}^{W_l}
\left\|
w_l\odot
\left(
\hat{\phi}_l(x)_{h,w}
-
\hat{\phi}_l(\hat{x})_{h,w}
\right)
\right\|_2^2
$$

其中：

- $\phi_l(\cdot)$ 表示预训练网络第 $l$ 层的特征。
- $\hat{\phi}_l(\cdot)$ 表示通道归一化后的特征。
- $w_l$ 是 LPIPS 中学习得到的通道权重。
- $\odot$ 表示逐通道加权。

对视频集合，通常先逐帧计算 LPIPS，再求平均：

$$
\mathrm{LPIPS}
=
\frac{1}{NT}
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathrm{LPIPS}(x_{i,t},\hat{x}_{i,t})
$$

LPIPS 越低，表示感知特征越接近真实图像。它通常比 PSNR 更接近人的视觉判断，但仍然只衡量图像或帧级感知距离，不能直接评价动作执行是否正确。

### 2.4 FVD

FVD 的全称是 Fréchet Video Distance，用于比较真实视频分布和生成视频分布之间的距离。它不是逐帧比较，而是先用视频特征提取器把整段视频映射为特征向量。

设视频特征提取器为 $\Phi(\cdot)$，则：

$$
f_i=\Phi(X_i)
$$

$$
\hat{f}_i=\Phi(\hat{X}_i)
$$

对真实视频特征集合 $\{f_i\}_{i=1}^{N}$，估计均值和协方差：

$$
\mu_r
=
\frac{1}{N}
\sum_{i=1}^{N}
f_i
$$

$$
\Sigma_r
=
\frac{1}{N-1}
\sum_{i=1}^{N}
(f_i-\mu_r)(f_i-\mu_r)^\top
$$

对生成视频特征集合 $\{\hat{f}_i\}_{i=1}^{N}$，估计均值和协方差：

$$
\mu_g
=
\frac{1}{N}
\sum_{i=1}^{N}
\hat{f}_i
$$

$$
\Sigma_g
=
\frac{1}{N-1}
\sum_{i=1}^{N}
(\hat{f}_i-\mu_g)(\hat{f}_i-\mu_g)^\top
$$

FVD 计算为：

$$
\mathrm{FVD}
=
\|\mu_r-\mu_g\|_2^2
+
\mathrm{Tr}
\left(
\Sigma_r+\Sigma_g
-
2(\Sigma_r\Sigma_g)^{1/2}
\right)
$$

FVD 越低，说明生成视频的整体分布越接近真实视频。相较 PSNR、SSIM、LPIPS，FVD 更关注视频级分布和时序特征。但 FVD 仍然不是动作可控性指标：一个视频可以看起来像 Minecraft，却没有严格响应给定动作。

## 3. 动作可控性指标

MineWorld 的关键点是：世界模型不只要生成“像游戏”的画面，还要生成“跟随动作变化”的画面。因此论文额外设计了基于 IDM 的动作可控性评估。

### 3.1 IDM 的基本思想

IDM 是 inverse dynamics model，即逆动力学模型。普通动力学模型学习：

$$
(x_t,a_t)\mapsto x_{t+1}
$$

IDM 反过来，从相邻状态估计中间发生的动作：

$$
(x_t,x_{t+1})\mapsto a_t
$$

在 MineWorld 评估中，输入给 IDM 的是生成视频中的相邻帧：

$$
\tilde{a}_{i,t}
=
\mathrm{IDM}(\hat{x}_{i,t},\hat{x}_{i,t+1})
$$

然后将 IDM 预测动作 $\tilde{a}_{i,t}$ 与原始条件动作 $a_{i,t}$ 比较。

如果生成视频确实执行了输入动作，那么 IDM 从生成帧中反推出来的动作应当接近 $a_{i,t}$。因此：

$$
\tilde{a}_{i,t}\approx a_{i,t}
$$

动作可控性评估的核心就是衡量这种一致性。

### 3.2 离散动作分组

Minecraft 动作空间比较复杂，既有键盘/鼠标按键动作，也有连续相机旋转动作。MineWorld 对离散动作采用分组分类的方式。

论文 Appendix A.1 中的离散动作分类任务如下：

| 任务类型 | 动作 | 标签 |
|---|---|---|
| 三分类 | `forward`, `backward` | `forward`, `backward`, `null` |
| 三分类 | `left`, `right` | `left`, `right`, `null` |
| 三分类 | `sprint`, `sneak` | `sprint`, `sneak`, `null` |
| 二分类 | `use` | `use`, `null` |
| 二分类 | `attack` | `attack`, `null` |
| 二分类 | `jump` | `jump`, `null` |
| 二分类 | `drop` | `drop`, `null` |

设第 $m$ 个子任务的标签集合为：

$$
\mathcal{C}^{(m)}
=
\{0,1,\cdots,C_m-1\}
$$

其中 $0$ 通常表示 `null`，其余类别表示具体动作。

对真实动作 $a_{i,t}$，可得到第 $m$ 个子任务的真实标签：

$$
y_{i,t}^{(m)}
=
g_m(a_{i,t})
$$

对 IDM 预测动作 $\tilde{a}_{i,t}$，可得到预测标签：

$$
\hat{y}_{i,t}^{(m)}
=
g_m(\tilde{a}_{i,t})
$$

$g_m(\cdot)$ 是第 $m$ 个子任务的动作到类别标签的映射函数。

对于三分类任务，例如 `forward/backward/null`，可以理解为：

$$
g_m(a)=
\begin{cases}
1, & \text{if } a \text{ contains forward} \\
2, & \text{if } a \text{ contains backward} \\
0, & \text{otherwise}
\end{cases}
$$

如果出现互斥动作同时为真的冲突情况，例如 `forward` 和 `backward` 同时被预测为 $1$，MineWorld 的处理方式是归入 `null`。源码 `construct_classification_labels()` 中也体现了这个规则。

### 3.3 Precision、Recall、F1

对第 $m$ 个动作子任务和类别 $c$，定义：

$$
\mathrm{TP}_c^{(m)}
=
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathbf{1}
[
\hat{y}_{i,t}^{(m)}=c
\land
y_{i,t}^{(m)}=c
]
$$

$$
\mathrm{FP}_c^{(m)}
=
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathbf{1}
[
\hat{y}_{i,t}^{(m)}=c
\land
y_{i,t}^{(m)}\neq c
]
$$

$$
\mathrm{FN}_c^{(m)}
=
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\mathbf{1}
[
\hat{y}_{i,t}^{(m)}\neq c
\land
y_{i,t}^{(m)}=c
]
$$

其中 $\mathbf{1}[\cdot]$ 是指示函数，条件成立时取 $1$，否则取 $0$。

类别 $c$ 的精确率为：

$$
\mathrm{Precision}_c^{(m)}
=
\frac{
\mathrm{TP}_c^{(m)}
}{
\mathrm{TP}_c^{(m)}+\mathrm{FP}_c^{(m)}
}
$$

类别 $c$ 的召回率为：

$$
\mathrm{Recall}_c^{(m)}
=
\frac{
\mathrm{TP}_c^{(m)}
}{
\mathrm{TP}_c^{(m)}+\mathrm{FN}_c^{(m)}
}
$$

类别 $c$ 的 F1 为：

$$
\mathrm{F1}_c^{(m)}
=
\frac{
2\cdot
\mathrm{Precision}_c^{(m)}
\cdot
\mathrm{Recall}_c^{(m)}
}{
\mathrm{Precision}_c^{(m)}
+
\mathrm{Recall}_c^{(m)}
}
$$

Precision 越高，表示 IDM 预测为某动作时更少误报。Recall 越高，表示真实发生某动作时更少漏报。F1 是二者的调和平均。

### 3.4 Macro 与 Micro

MineWorld 源码同时计算 `precision_micro`、`recall_micro`、`f1_micro`、`precision_macro`、`recall_macro` 和 `f1_macro`。

第 $m$ 个子任务的 macro precision 为：

$$
\mathrm{Precision}_{\mathrm{macro}}^{(m)}
=
\frac{1}{C_m}
\sum_{c=0}^{C_m-1}
\mathrm{Precision}_c^{(m)}
$$

macro recall 为：

$$
\mathrm{Recall}_{\mathrm{macro}}^{(m)}
=
\frac{1}{C_m}
\sum_{c=0}^{C_m-1}
\mathrm{Recall}_c^{(m)}
$$

macro F1 为：

$$
\mathrm{F1}_{\mathrm{macro}}^{(m)}
=
\frac{1}{C_m}
\sum_{c=0}^{C_m-1}
\mathrm{F1}_c^{(m)}
$$

macro 平均对每个类别一视同仁，适合动作标签不均衡的情况。例如 `drop` 比 `forward` 少很多，如果只看总体准确率，模型可能几乎忽略 `drop` 也能得到不错的数值；macro F1 会更明显地反映这种问题。

micro precision、micro recall 和 micro F1 先把所有类别的 TP、FP、FN 汇总，再计算：

$$
\mathrm{Precision}_{\mathrm{micro}}^{(m)}
=
\frac{
\sum_c \mathrm{TP}_c^{(m)}
}{
\sum_c \mathrm{TP}_c^{(m)}
+
\sum_c \mathrm{FP}_c^{(m)}
}
$$

$$
\mathrm{Recall}_{\mathrm{micro}}^{(m)}
=
\frac{
\sum_c \mathrm{TP}_c^{(m)}
}{
\sum_c \mathrm{TP}_c^{(m)}
+
\sum_c \mathrm{FN}_c^{(m)}
}
$$

$$
\mathrm{F1}_{\mathrm{micro}}^{(m)}
=
\frac{
2\cdot
\mathrm{Precision}_{\mathrm{micro}}^{(m)}
\cdot
\mathrm{Recall}_{\mathrm{micro}}^{(m)}
}{
\mathrm{Precision}_{\mathrm{micro}}^{(m)}
+
\mathrm{Recall}_{\mathrm{micro}}^{(m)}
}
$$

对单标签多分类任务，micro F1 通常接近总体 accuracy。它更容易被高频类别影响。

### 3.5 跨动作子任务平均

MineWorld 不是只算一个动作分类任务，而是对多个动作子任务分别计算指标，然后再对任务求平均。

设离散动作子任务共有 $M$ 个，在 MineWorld 中通常是：

$$
M=7
$$

也就是 3 个三分类任务加 4 个二分类任务。

跨任务平均的 macro F1 为：

$$
\mathrm{F1}_{\mathrm{action}}
=
\frac{1}{M}
\sum_{m=1}^{M}
\mathrm{F1}_{\mathrm{macro}}^{(m)}
$$

同理：

$$
\mathrm{Precision}_{\mathrm{action}}
=
\frac{1}{M}
\sum_{m=1}^{M}
\mathrm{Precision}_{\mathrm{macro}}^{(m)}
$$

$$
\mathrm{Recall}_{\mathrm{action}}
=
\frac{1}{M}
\sum_{m=1}^{M}
\mathrm{Recall}_{\mathrm{macro}}^{(m)}
$$

源码 `evaluate_IDM_quality()` 中的 `metric_mean_on_task` 采用这个思路：先得到每个子任务的分类指标，再对所有子任务取平均。论文主表中的 P、R、F1 可以按这个聚合指标理解。

## 4. 相机动作 L1

Minecraft 视角移动是连续值，通常包含 yaw 和 pitch 两个方向。MineWorld 没有直接用连续角度计算误差，而是沿用 VPT 风格，把相机旋转离散成 bin 后再比较。

### 4.1 相机动作量化

设某一维相机动作为 $u$，例如 yaw 或 pitch。源码中的评估配置为：

$$
u_{\max}=10
$$

$$
b=2
$$

$$
\mu=10
$$

其中 $u_{\max}$ 是裁剪范围，$b$ 是 bin size，$\mu$ 是 mu-law 压缩参数。

先裁剪：

$$
u'
=
\mathrm{clip}(u,-u_{\max},u_{\max})
$$

如果使用 mu-law 量化，先做非线性压缩：

$$
e(u')
=
\mathrm{sign}(u')
\cdot
\frac{
\log\left(1+\mu\left|u'\right|/u_{\max}\right)
}{
\log(1+\mu)
}
\cdot
u_{\max}
$$

然后映射到离散 bin：

$$
q(u)
=
\mathrm{round}
\left(
\frac{e(u')+u_{\max}}{b}
\right)
$$

在 $u_{\max}=10$、$b=2$ 时，bin 编号范围是：

$$
q(u)\in\{0,1,\cdots,10\}
$$

因此每个方向有 $11$ 个离散 bin。mu-law 的作用是让接近 $0$ 的小幅视角变化有更细粒度，大幅旋转则使用更粗粒度。

如果不使用 mu-law，直接令：

$$
e(u')=u'
$$

即可得到线性量化。

### 4.2 Camera L1 计算

设真实相机动作为 $c_{i,t,d}$，IDM 预测相机动作为 $\tilde{c}_{i,t,d}$，其中 $d\in\{x,y\}$ 表示两个相机轴。量化后：

$$
z_{i,t,d}=q(c_{i,t,d})
$$

$$
\tilde{z}_{i,t,d}=q(\tilde{c}_{i,t,d})
$$

Camera L1 定义为预测 bin 与真实 bin 的平均绝对差：

$$
\mathrm{L1}_{\mathrm{camera}}
=
\frac{1}{2NT}
\sum_{i=1}^{N}
\sum_{t=1}^{T}
\sum_{d\in\{x,y\}}
\left|
\tilde{z}_{i,t,d}
-
z_{i,t,d}
\right|
$$

Camera L1 越低，表示生成视频中体现出来的视角变化越接近输入相机动作。论文主表中的 `L1` 就是这个相机控制误差，越低越好。

## 5. 指标汇总方式

完整评估可以概括为下面的流程：

```text
生成视频目录 + 真实视频目录
-> common_metrics.py
-> FVD / LPIPS / SSIM / PSNR

生成视频目录 + 原始动作 jsonl
-> inverse_dynamics_model.py
-> IDM 预测动作
-> 离散动作 P / R / F1
-> 相机动作 L1

FVD 指标文件 + IDM 指标文件
-> tabulate_all_results.py
-> 汇总 CSV
```

在 MineWorld 源码中，视频质量指标输出到类似：

```text
fvd_xxx.json
```

动作可控性指标输出到类似：

```text
idm_xxx.json
```

最后 `tabulate_all_results.py` 会合并两类 json，并生成整体实验表。

论文主表中的方向如下：

| 指标 | 含义 | 越大越好/越小越好 |
|---|---|---|
| FPS | 每秒生成帧数 | 越大越好 |
| P | IDM 离散动作 precision | 越大越好 |
| R | IDM 离散动作 recall | 越大越好 |
| F1 | IDM 离散动作 F1 | 越大越好 |
| L1 | 相机动作 bin 误差 | 越小越好 |
| FVD | 视频分布距离 | 越小越好 |
| LPIPS | 感知特征距离 | 越小越好 |
| SSIM | 结构相似性 | 越大越好 |
| PSNR | 像素级峰值信噪比 | 越大越好 |

## 6. 复现时的注意点

### 6.1 不能只看视频质量

Game world model 和普通 video generation 的关键区别在于动作条件。一个模型可能生成很像 Minecraft 的画面，但对 `forward`、`attack`、`jump` 等动作没有真实响应。因此 MineWorld 同时报告视频质量和动作可控性。

如果只报告：

$$
\mathrm{FVD},\mathrm{PSNR},\mathrm{SSIM},\mathrm{LPIPS}
$$

只能说明画面质量，不能证明模型学会了动作条件动态。

### 6.2 IDM 自身必须可靠

IDM 指标成立的前提是 IDM 在真实视频上足够准确。否则，IDM 预测错了动作，生成模型会被错误评价。

实践中建议先在真实测试集上评估 IDM：

$$
\tilde{a}_{i,t}^{real}
=
\mathrm{IDM}(x_{i,t},x_{i,t+1})
$$

然后计算：

$$
\tilde{a}_{i,t}^{real}
\quad \text{vs.} \quad
a_{i,t}
$$

如果 IDM 在真实视频上的 F1 或 accuracy 太低，就不适合作为生成视频的可控性评价器。

### 6.3 需要加入动作对照实验

为了证明模型确实使用了动作条件，建议至少比较三种设置：

| 设置 | 输入动作 | 目的 |
|---|---|---|
| No-action | 不输入动作 | 检查模型只靠历史帧能做到什么程度 |
| Correct-action | 输入正确动作 | 主模型结果 |
| Shuffled-action | 输入打乱动作 | 检查模型是否真的依赖动作 |

如果模型真正利用动作，通常应看到：

$$
\mathrm{F1}_{\mathrm{correct}}
>
\mathrm{F1}_{\mathrm{no-action}}
$$

并且：

$$
\mathrm{F1}_{\mathrm{correct}}
>
\mathrm{F1}_{\mathrm{shuffled}}
$$

如果打乱动作后 F1 几乎不下降，说明模型可能主要依赖历史画面惯性，并没有充分使用 action token。

### 6.4 可以补充动作敏感性指标

除 MineWorld 原始指标外，个人复现时还可以增加动作敏感性测试。给定同一个初始状态 $x_0$，输入不同动作 $a$，得到生成结果：

$$
G(x_0,a)
$$

动作敏感性可以定义为：

$$
D_{\mathrm{action}}
=
\frac{1}{|\mathcal{A}|(|\mathcal{A}|-1)}
\sum_{a\neq a'}
d
\left(
G(x_0,a),
G(x_0,a')
\right)
$$

其中 $d(\cdot,\cdot)$ 可以取 LPIPS、DINO 特征距离，或者某个游戏状态识别器的特征距离。

这个指标只能说明模型对不同动作是否敏感，不能单独证明动作响应是否正确。因此它适合作为 IDM 指标的补充，而不是替代。

## 7. 一句话总结

MineWorld 的视频质量指标回答：

```text
生成的视频像不像真实 Minecraft 视频？
```

动作可控性指标回答：

```text
生成的视频是否真的执行了输入动作？
```

前者用 FVD、PSNR、SSIM、LPIPS；后者用 IDM 反推动作，再计算离散动作的 P/R/F1 和相机动作的 L1。对 game world model 来说，后者尤其关键，因为可交互性本质上依赖动作响应，而不是单帧画面是否好看。
