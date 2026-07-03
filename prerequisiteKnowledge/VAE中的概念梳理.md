# VAE中的概念梳理

这篇笔记以 VAE 为主线，梳理最大似然、KL 散度、ELBO 和 Jensen 不等式之间的关系。这几个概念也经常出现在变分推断、扩散模型、世界模型和强化学习论文中。

> 最大似然是我们真正想优化的目标；KL 散度衡量两个分布的差异；ELBO 是潜变量模型中可优化的似然下界；Jensen 不等式是推导这个下界的关键数学工具。

如果按 VAE 的建模流程来看，它们的关系是：

1. 我们希望模型给真实数据更高概率，因此使用最大似然。
2. VAE 含有潜变量 $z$，真实似然需要对 $z$ 积分，直接优化很难。
3. VAE 引入一个近似后验分布 $q_\phi(z\mid x)$，把难算的积分转成期望形式。
4. 利用 Jensen 不等式，把 $\log \mathbb E[\cdot]$ 变成一个可优化的下界。
5. 这个下界就是 ELBO。
6. ELBO 和真实 log likelihood 之间的差距正好可以写成一个 KL 散度。

---

## 1. 最大似然

最大似然估计，Maximum Likelihood Estimation，简称 MLE。它的核心问题是：

> 已经观察到一批真实数据，应该选择怎样的模型参数，才能让这些数据在模型下出现的概率尽可能大？

对于单个样本 $x$，最大似然目标是：

$$
\max_\theta \log p_\theta(x)
$$

对于数据集 $\mathcal D=\{x_i\}_{i=1}^N$，目标是：

$$
\max_\theta \sum_{i=1}^{N}\log p_\theta(x_i)
$$

这里：

- $x_i$：第 $i$ 个训练样本。
- $\theta$：模型参数。
- $p_\theta(x_i)$：模型在参数 $\theta$ 下给样本 $x_i$ 分配的概率。
- $\log p_\theta(x_i)$：对数似然。取对数是为了把连乘变成求和，也让优化更稳定。

---

## 2. 潜变量的难点

很多生成模型会引入潜变量 $z$。例如 VAE 假设数据生成过程是：

$$
z \sim p(z)
$$

$$
x \sim p_\theta(x\mid z)
$$

也就是说，模型先采样一个隐藏原因 $z$，再由 $z$ 生成观测数据 $x$。

联合分布可以写成：

$$
p_\theta(x,z)=p(z)p_\theta(x\mid z)
$$

这里右边的两个 $p$ 虽然都表示概率分布，但是否带下标取决于这个分布是否由可学习参数控制。

$p(z)$ 表示潜变量 $z$ 的先验分布。在最基础的 VAE 中，它通常被人为固定为标准高斯：

$$
p(z)=\mathcal N(0,I)
$$

**这个先验不需要通过训练学习**，所以不写参数下标。

$p_\theta(x\mid z)$ 表示给定潜变量 $z$ 后生成观测 $x$ 的条件分布。这个分布通常由解码器神经网络定义，解码器有可学习参数 $\theta$，所以写成 $p_\theta(x\mid z)$。

因此，右边可以理解成：

$$
\text{生成 } z \text{ 的概率} \times \text{从 } z \text{ 生成 } x \text{ 的概率}
$$

前半部分 $p(z)$ 是固定先验，后半部分 $p_\theta(x\mid z)$ 是**可学习的**生成机制。

左边写成 $p_\theta(x,z)$，是因为整个联合分布中虽然 $p(z)$ 不含参数，但 $p_\theta(x\mid z)$ 含有参数 $\theta$。只要解码器参数变化，联合分布整体也会变化，**所以联合分布整体带下标 $\theta$**。

**如果先验本身也是可学习的，例如写成 $p_\alpha(z)$，那么联合分布也可以写成：**
$$
p_{\theta,\alpha}(x,z)=p_\alpha(z)p_\theta(x\mid z)
$$

**但基础 VAE 通常使用固定标准高斯先验，所以常见写法就是带一个参数$\theta$的。**

但训练时我们通常只能看到 $x$，看不到 $z$。因此真正的似然是边缘似然：

$$
p_\theta(x)=\int p_\theta(x,z)\,dz
$$

两边同时取对数：

$$
\log p_\theta(x)
=
\log \int p_\theta(x,z)\,dz
$$

此处积分很棘手。

如果 $z$ 是高维连续变量，或者 $p_\theta(x\mid z)$ 由深度神经网络定义，那么**这个积分通常没有解析解**。我们既不知道每个 $x$ 背后对应什么 $z$，也无法穷举所有可能的 $z$。

所以，潜变量模型中的最大似然目标虽然清楚，但直接优化往往不可行。

---

## 3. KL 散度

KL 散度，Kullback-Leibler divergence，用来衡量两个分布之间的差异。它的定义是：

$$
D_{\mathrm{KL}}(q(z)\|p(z))
=
\mathbb E_{q(z)}
\left[
\log \frac{q(z)}{p(z)}
\right]
$$

也可以写成：

$$
D_{\mathrm{KL}}(q\|p)
=
\mathbb E_q[\log q(z)-\log p(z)]
$$

这里的期望是对 $q(z)$ 取的。因此，KL 散度可通俗理解为：

> 如果真实采样来自 $q$，但我们用 $p$ 去描述它，会多付出多少信息代价？

### 3.1 KL 散度的几个性质

第一，KL 散度非负：

$$
D_{\mathrm{KL}}(q\|p)\ge 0
$$

当且仅当 $q=p$ 时：

$$
D_{\mathrm{KL}}(q\|p)=0
$$

第二，KL 散度不是对称的：

$$
D_{\mathrm{KL}}(q\|p)\ne D_{\mathrm{KL}}(p\|q)
$$

这个非对称性非常重要。

$D_{\mathrm{KL}}(q\|p)$ 更关注 $q$ 有概率质量的地方。如果 $q(z)$ 很大但 $p(z)$ 很小，那么：

$$
\log \frac{q(z)}{p(z)}
$$

会很大，惩罚也会很大。

这意味着，如果我们最小化：

$$
D_{\mathrm{KL}}(q\|p)
$$

那么 $p$ 最好覆盖 $q$ 认为重要的区域。

### 3.2 在变分推断中的作用

在潜变量模型里，我们希望知道真实后验：

$$
p_\theta(z\mid x)
$$

它表示：给定观测 $x$，隐藏原因 $z$ 应该是什么样的分布。

根据 Bayes 公式：

$$
p_\theta(z\mid x)
=
\frac{p_\theta(x,z)}{p_\theta(x)}
$$

但分母：

$$
p_\theta(x)=\int p_\theta(x,z)\,dz
$$

正是难算的边缘似然。

因此真实后验 $p_\theta(z\mid x)$ 借助贝叶斯公式也依旧难以计算。变分推断的做法是**引入一个可计算的近似分布**：

$$
q_\phi(z\mid x)
$$

然后希望：

$$
q_\phi(z\mid x)\approx p_\theta(z\mid x)
$$

于是这样就可以避免使用贝叶斯公式从而引入比较难以计算的边缘似然$p_\theta(x)=\int p_\theta(x,z)\,dz$

这个“接近”就可以用 KL 散度表达，同时在后文会提到，这个式子刻画了样本的真实对数似然与ELBO之间的gap：
$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

所以现在的逻辑链是，我们本想用贝叶斯公式去得到真实后验，但又会不可避免地引入比较难计算的边缘似然。于是换个角度，用一个近似分布，借助KL散度去逼近。但是，就算逼近我们也得知道真实后验 $p_\theta(z\mid x)$，最起码得知道范围。所以考虑使用ELBO避开这个问题。

---

## 4. Jensen 不等式

Jensen 不等式描述的是函数和期望之间的关系。

如果 $f$ 是凹函数，那么：

$$
f(\mathbb E[X])\ge \mathbb E[f(X)]
$$

因为 $\log$ 是凹函数，所以有：

$$
\log \mathbb E[X]\ge \mathbb E[\log X]
$$

这正是 ELBO 推导中最关键的一步。

从图像上，$\log$ 函数向下弯，因此“先求平均再取 log”会大于等于“先取 log 再求平均”。

---

## 5. 用 Jensen 不等式推导 ELBO

从最大似然开始：

$$
\log p_\theta(x)
=
\log \int p_\theta(x,z)\,dz
$$

现在引入任意一个合法分布 $q_\phi(z\mid x)$。只要它在相关区域非零，就可以写成（乘以再除以同一个分布 $q_\phi(z\mid x)$）：

$$
\log p_\theta(x)
=
\log \int q_\phi(z\mid x)
\frac{p_\theta(x,z)}{q_\phi(z\mid x)}
\,dz
$$



上式可以看成对 $q_\phi(z\mid x)$ 的期望：

$$
\log p_\theta(x)
=
\log
\mathbb E_{q_\phi(z\mid x)}
\left[
\frac{p_\theta(x,z)}{q_\phi(z\mid x)}
\right]
$$

然后用 Jensen 不等式：

$$
\log
\mathbb E_{q_\phi(z\mid x)}
\left[
\frac{p_\theta(x,z)}{q_\phi(z\mid x)}
\right]
\ge
\mathbb E_{q_\phi(z\mid x)}
\left[
\log
\frac{p_\theta(x,z)}{q_\phi(z\mid x)}
\right]
$$

于是得到：

$$
\log p_\theta(x)
\ge
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x,z)-\log q_\phi(z\mid x)
\right]
$$

**右边就是 ELBO：**
$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x,z)-\log q_\phi(z\mid x)
\right]
$$

因为：

$$
\log p_\theta(x)\ge \mathcal L_{\mathrm{ELBO}}(x)
$$

所以它叫 Evidence Lower Bound，证据下界。

这里的 evidence 指的就是观测数据的边缘似然：

$$
p_\theta(x)
$$

---

## 6. ELBO 的常见展开形式

如果联合分布满足：

$$
p_\theta(x,z)=p(z)p_\theta(x\mid z)
$$

则 ELBO 可以展开：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p(z)+\log p_\theta(x\mid z)-\log q_\phi(z\mid x)
\right]
$$

把重建项单独拿出来：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x\mid z)
\right]
+
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p(z)-\log q_\phi(z\mid x)
\right]
$$

第二项可以写成负 KL：

$$
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p(z)-\log q_\phi(z\mid x)
\right]
=
-
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

所以：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x\mid z)
\right]
-
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

这就是 VAE 里最常见的 ELBO 形式。

---

## 7. 对 ELBO 的理解

ELBO 可以理解成两个目标的平衡：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\text{重建项}
-
\text{KL 正则项}
$$

### 7.1 重建项

重建项是：

$$
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x\mid z)
\right]
$$

它要求潜变量 $z$ 能解释观测 $x$。

如果是图像模型，它要求从 $z$ 能重建图像。

如果是文本模型，它要求从隐藏表示能生成原文本或目标文本。

**如果是世界模型，它要求 latent state 能预测观测、奖励、终止信号或下一步状态。**

重建项越大，说明模型越能用 $z$ 解释数据。

### 7.2 KL 正则项

KL 正则项是：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

它要求编码器给出的后验分布不要离先验太远。

常见先验是标准高斯：

$$
p(z)=\mathcal N(0,I)
$$

这项的作用是让潜空间更规整。否则，编码器可能把每个样本映射到彼此很远、结构杂乱的位置，虽然重建很好，但生成时很难从先验中采样到有效的 $z$。

所以 VAE 的目标不是只追求重建，而是在两个要求之间折中。重建项和KL正则项分别解决了这两个问题：

1. $z$ 要保留足够信息，能解释 $x$。
2. $z$ 的分布要规整，方便采样和生成。

---

## 8. ELBO 与 MLE

ELBO 和真实 log likelihood 有精确分解关系：

$$
\log p_\theta(x)
=
\mathcal L_{\mathrm{ELBO}}(x)
+
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

由于 KL 散度非负：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
\ge 0
$$

所以：

$$
\log p_\theta(x)\ge \mathcal L_{\mathrm{ELBO}}(x)
$$

这说明 ELBO 是 $\log p_\theta(x)$ 的下界。

如果：

$$
q_\phi(z\mid x)=p_\theta(z\mid x)
$$

那么：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)=0
$$

于是：

$$
\log p_\theta(x)=\mathcal L_{\mathrm{ELBO}}(x)
$$

这时下界变紧，ELBO 等于真实 log likelihood。

---

## 9. 分解推导

从 KL 散度开始：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log q_\phi(z\mid x)-\log p_\theta(z\mid x)
\right]
$$

根据 Bayes 公式：

$$
p_\theta(z\mid x)
=
\frac{p_\theta(x,z)}{p_\theta(x)}
$$

取 log：

$$
\log p_\theta(z\mid x)
=
\log p_\theta(x,z)-\log p_\theta(x)
$$

代入 KL：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
=
\mathbb E_q
\left[
\log q_\phi(z\mid x)
-
\log p_\theta(x,z)
+
\log p_\theta(x)
\right]
$$

因为 $\log p_\theta(x)$ 与 $z$ 无关，可以从期望中拿出来，有：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
=
\mathbb E_q
\left[
\log q_\phi(z\mid x)
-
\log p_\theta(x,z)
\right]
+
\log p_\theta(x)
$$

移项：

$$
\log p_\theta(x)
=
\mathbb E_q
\left[
\log p_\theta(x,z)
-
\log q_\phi(z\mid x)
\right]
+
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

其中：

$$
\mathbb E_q
\left[
\log p_\theta(x,z)
-
\log q_\phi(z\mid x)
\right]
=
\mathcal L_{\mathrm{ELBO}}(x)
$$

于是：

$$
\log p_\theta(x)
=
\mathcal L_{\mathrm{ELBO}}(x)
+
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

这个分解也解释了为什么最大化 ELBO 是合理的：我们虽然不能直接算真实后验，也不能直接算真实 log likelihood，但可以最大化一个下界，同时让近似后验向真实后验靠近。

---

## 10. VAE 中的训练目标

VAE 中通常有两个网络：

- 编码器：给出近似后验 $q_\phi(z\mid x)$。
- 解码器：给出生成分布 $p_\theta(x\mid z)$。

这里的下标 $\phi$ 和 $\theta$ 都表示可学习参数，但它们通常对应不同模块。

### 10.1 符号下标

在 $q_\phi(z\mid x)$ 中，$\phi$ 表示近似后验模型的参数，通常就是编码器网络的权重。

即：给定观测 $x$，编码器根据参数 $\phi$ 输出潜变量 $z$ 的分布。

例如编码器可以输出均值和标准差：

$$
\mu_\phi(x), \quad \sigma_\phi(x)
$$

于是近似后验可以写成：

$$
q_\phi(z\mid x)
=
\mathcal N\left(z;\mu_\phi(x),\mathrm{diag}(\sigma_\phi^2(x))\right)
$$

这里的 $\mu_\phi(x)$ 和 $\sigma_\phi(x)$ 是编码器神经网络对输入 $x$ 的输出。

在 $p_\theta(x\mid z)$ 或 $p_\theta(x,z)$ 中，$\theta$ 表示生成模型的参数，通常对应解码器、先验模型或动力学模型的权重。

这个分布读作：给定潜变量 $z$，生成模型根据参数 $\theta$ 生成或解释观测 $x$。也就是说，$\theta$ 控制的是“隐藏变量怎样生成数据”。

在 VAE 的最简单形式中，可以把两个方向这样区分：

| 符号 | 常见名称 | 参数含义 | 负责的问题 |
|---|---|---|---|
| $q_\phi(z\mid x)$ | 近似后验 / inference model / encoder | $\phi$ 是编码器参数 | 看到 $x$ 后，推断 $z$ 可能在哪里 |
| $p_\theta(x\mid z)$ | 生成分布 / generative model / decoder | $\theta$ 是解码器参数 | 给定 $z$ 后，生成或重建 $x$ |
| $p(z)$ | 先验分布 | 通常没有可学习参数，常取 $\mathcal N(0,I)$ | 在没有观测时，规定 $z$ 大致应落在哪里 |

因此，$q_\phi(z\mid x)$ 和 $p_\theta(x\mid z)$ 是两个方向相反的模型。

前者从数据到潜变量：

$$
x \rightarrow z
$$

后者从潜变量到数据：

$$
z \rightarrow x
$$

这也是为什么论文里常用不同希腊字母区分参数：$\phi$ 多用于推断模型，$\theta$ 多用于生成模型。

常见先验是：

$$
p(z)=\mathcal N(0,I)
$$

VAE 最大化：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x\mid z)
\right]
-
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

在实现里，很多代码会写成最小化 loss：

$$
\mathcal L_{\mathrm{loss}}
=
-
\mathbb E_{q_\phi(z\mid x)}
\left[
\log p_\theta(x\mid z)
\right]
+
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

也就是：

$$
\mathcal L_{\mathrm{loss}}
=
\text{重建损失}
+
\text{KL 正则}
$$

如果 $p_\theta(x\mid z)$ 选成高斯分布，重建损失常常对应均方误差。

如果 $p_\theta(x\mid z)$ 选成 Bernoulli 分布，重建损失常常对应二元交叉熵。

这取决于模型如何定义 $x\mid z$ 的观测分布。

---

## 11. 两个 KL 项

这里最容易混淆的是两个 KL。

### 11.1 ELBO 内部的 KL

VAE 训练时常见的 KL 是：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p(z)
\right)
$$

它是可计算的，因为 $q_\phi(z\mid x)$ 和 $p(z)$ 都是我们定义的分布。

它的作用是约束近似后验不要离先验太远，让潜空间更规整。

### 11.2 ELBO 和真实似然之间的 gap

理论分解里的 KL 是：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

它表示 ELBO 和真实 log likelihood 之间的差距：

$$
\log p_\theta(x)-\mathcal L_{\mathrm{ELBO}}(x)
=
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)
$$

这个 KL 通常不能直接算，因为真实后验 $p_\theta(z\mid x)$ 依赖难算的 $p_\theta(x)$。

所以：

- $D_{\mathrm{KL}}(q_\phi(z\mid x)\|p(z))$：训练目标里可计算的正则项。
- $D_{\mathrm{KL}}(q_\phi(z\mid x)\|p_\theta(z\mid x))$：理论上刻画 ELBO gap 的项，通常不可直接计算。

---

## 12. 计算

假设某个样本 $x$ 的真实 log likelihood 是：

$$
\log p_\theta(x)=-10
$$

如果当前近似后验和真实后验之间的 KL gap 是：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z\mid x)\|p_\theta(z\mid x)
\right)=3
$$

那么：

$$
\mathcal L_{\mathrm{ELBO}}(x)
=
\log p_\theta(x)-3
=
-13
$$

也就是说，ELBO 是 $-10$ 的下界。

如果训练让 gap 从 $3$ 降到 $1$，并且真实似然不变，那么 ELBO 会从 $-13$ 升到 $-11$。

如果训练同时提高了真实似然，并让 gap 变小，那么 ELBO 就会进一步上升。

这就是 ELBO 的意义：它一方面推动模型更好解释数据，另一方面推动近似后验更接近真实后验。

---

## 13. 与世界模型的关系

在世界模型里，我们经常也会遇到类似结构。

例如 RSSM 或 VAE-style latent dynamics 里，模型可能维护：

- 后验分布：$q_\phi(z_t\mid h_t,o_t)$，训练时看见当前观测。
- 先验分布：$p_\theta(z_t\mid h_t)$，想象 rollout 时只依赖历史。

训练时常见目标包括：

1. 观测重建或预测：

$$
\log p_\theta(o_t\mid h_t,z_t)
$$

2. 奖励预测：

$$
\log p_\theta(r_t\mid h_t,z_t)
$$

3. 终止或 continue 信号预测：

$$
\log p_\theta(c_t\mid h_t,z_t)
$$

4. 后验和先验的 KL 对齐：

$$
D_{\mathrm{KL}}
\left(
q_\phi(z_t\mid h_t,o_t)\|p_\theta(z_t\mid h_t)
\right)
$$

这个结构和 VAE 很像：训练时后验看见真实观测，负责校准当前 latent；想象时先验看不见未来观测，只能根据历史往前生成。因此，KL 项会把先验拉向后验，让模型在没有真实观测的 imagination rollout 中也能保持稳定。

---

## 14. 总结

四个概念可以这样记：

$$
\text{最大似然：}
\quad
\max_\theta \log p_\theta(x)
$$

它是原始目标。

$$
\text{Jensen：}
\quad
\log \mathbb E[X]\ge \mathbb E[\log X]
$$

它把难算的 log 积分变成下界。

$$
\text{ELBO：}
\quad
\mathbb E_q[\log p_\theta(x,z)-\log q(z\mid x)]
$$

它是可优化的似然下界。

$$
\text{KL gap：}
\quad
\log p_\theta(x)-\mathcal L_{\mathrm{ELBO}}(x)
=
D_{\mathrm{KL}}(q(z\mid x)\|p_\theta(z\mid x))
$$

说明下界和真实目标之间的差距。

> 最大似然告诉我们要提高真实数据概率；潜变量让这个概率难以直接计算；Jensen 不等式给出一个可优化下界；这个下界就是 ELBO；ELBO 与真实 log likelihood 之间的差距由 KL 散度刻画。
