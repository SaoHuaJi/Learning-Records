---
name: "Large Language Models are Zero-Shot Reasoners"
uri: "https://arxiv.org/abs/2205.11916"
tags: ["LLM", "Chain-of-Thought", "Prompt Engineering", "Zero-shot Reasoning"]
type: "paper"
subjects: ["Artificial Intelligence", "Computation and Language"]
authors: ["Takeshi Kojima", "Shixiang Shane Gu", "Machel Reid", "Yutaka Matsuo", "Yusuke Iwasawa"]
affiliations: ["The University of Tokyo", "Google Research"]
year: 2022
venue: "NeurIPS 2022"
language: "en"
citation: |
    @article{kojima2022large,
        title={Large language models are zero-shot reasoners},
        author={Kojima, Takeshi and Gu, Shixiang Shane and Reid, Machel and Matsuo, Yutaka and Iwasawa, Yusuke},
        journal={Advances in neural information processing systems},
        volume={35},
        pages={22199--22213},
        year={2022}
    }

importance: 5
difficulty: 2
recommend: 3
---

# Large Language Models are Zero-Shot Reasoners

## 1. 概览 Overview

### 1.1 个人预览 Personal Preview

> 以往研究普遍认为，LLM 在零样本（zero-shot）条件下难以完成需要多步逻辑或算术推理的任务，通常必须依赖少样本（few-shot）示例，尤其是带有思维链（Chain-of-Thought）的示例。
> 文章提出了一种极其简单却有效的方法：在零样本提问中加入一句通用提示（如  “Let’s think step by step”），引导模型自行生成推理步骤。
> 该方法在多个推理基准上显著提升了零样本性能，在部分任务中甚至接近或超过传统 few-shot 方法。
> 这篇论文清楚地表明，大模型的推理能力并不完全依赖示例，而是可以通过合适的语言提示被 “激活” ，这极大拓展了提示词工程（Prompt Engineering）的边界。

### 1.2 内容简介 Description

- **研究背景 Research Background：**
  虽然 LLM 在语言理解和生成方面表现突出，但在数学推理、符号操作等需要系统化思考的任务上，零样本表现一直较差。此前的 CoT Prompting 证明了 “展示推理过程” 能提升模型能力，但仍依赖人工构造示例。

- **研究目标 Research Objectives：**
  文章旨在探索 LLM 在零样本情境下的潜在推理能力。作者希望证明无需任何示例，只需一个统一的提示就能引导模型进行多步推理，从而显著改善在算术、逻辑等推理任务上的表现。为此，论文设计了一个通用的零样本思维链提示模板（两阶段提示），并在多个基准任务上评估其有效性，分析模型规模和提示语句对推理表现的影响。

- **主要贡献 Main Contributions：**
&emsp;&emsp;(1) 提出了零样本思维链提示方法（Zero-shot-CoT）：只需在问题后添加一句提示 “让我们逐步思考” ，即可引导大型语言模型在不提供示例的情况下产出生步的推理过程，并得出正确答案。这一方法开创性地将思维链从少样本拓展到零样本场景，减少了人为设计示例的需求。
&emsp;&emsp;(2) 大幅提升了推理任务的零样本性能：在多项算术和逻辑推理基准上，Zero-shot-CoT 相比原始零样本提示取得了数量级的精度提升。例如，在算术推理数据集 MultiArith 上准确率从 17.7% 飙升至 78.7%，GSM8K 从 10.4% 提升到 40.7%。类似的提升在另一个 540B 参数模型 PaLM 上也同样显著。这些结果使其成为复杂推理基准新的最强零样本方法基线。
&emsp;&emsp;(3) 证明了单一通用提示的广泛适用性：与以往需为不同任务定制提示或示例的方法不同，Zero-shot-CoT 使用完全相同的提示模板在算术、符号、常识推理等 9+ 种任务上一律奏效，展现出出色的任务无关性。作者进一步发现，模型规模越大，零样本思维链带来的收益越明显；而小模型即使加入思维链推理，效果提升也很有限。这一现象表明复杂推理能力是一种在大型模型中涌现的能力维度，提示未来应更关注发掘和利用模型蕴含的零样本认知潜能。

---

## 2. 关键信息 Key Information

### 2.1 核心思想与方法 Main Ideas & Methods

**核心思想：**
LLM 本身已经学习了推理模式，只是默认不会显式展开。CoT 通过少样本示例的方式激活了推理模式，而 Zero-shot CoT 则通过加入一句 “让我们一步步思考” 来使模型自发生成中间推理步骤，再得出最终答案。
![Prompt](Resources/Zero-shot%20CoT%20-%20Prompt.png)
这种方法无需任何示例，且提示语在不同任务中保持一致，具有极强的通用性。

- **实现方法：**
Zero-shot CoT 使用两次提示来提取推理和答案。

第一次提示引导模型生成推理步骤。

```text
Request messages: [
    {role: user, content: [输入问题]}, 
    {role: assistant, content: [思维链推理触发句]}
]
Response content: [推理步骤]
```

第二次提示提取最终答案。

```text
Request messages: [
  {role: user, content: [推理步骤]},
  {role: assistant, content: [思维链推理触发句]+[推理步骤]+[答案提取触发句]}
]
Response content: [最终答案]
```

![Steps](Resources/Zero-shot%20CoT%20-%20Steps.png)
实际情况中第一步产生的推理步骤往往就能包含答案，因此第二步提示有时可以省略。

### 2.2 实验设置与结果 Experimental Settings & Results

- **实验设置 Experimental Settings：**  
作者使用 GPT-3 与 PaLM 等大模型在算术推理（GSM8K、MultiArith）、符号推理（Last Letter、Coin Flip）、常识推理（StrategyQA）等多个基准上测试 Zero-shot-CoT。比较基线包括：标准零样本（不加思维链提示，直接回答）、标准 few-shot（提供若干问答示例但无思维链）、few-shot-CoT 等。

- **实验结果 Experimental Results：**  
零样本思维链提示在各类任务上都取得了压倒性的性能提升。
以算术任务为例，GPT-3 模型在 MultiArith 上零样本直接答题仅 17.7% 正确率，加入 “让我们逐步思考” 后猛增到 78.7%；同一模型在 GSM8K 难题集上从 10.4% 提升到 40.7%，表现出跨任务的一贯提升趋势。
对于 PaLM 540B 等超大模型，Zero-shot-CoT 同样将 GSM8K 准确率从不到 20% 提高到约 80%，凸显大型模型配合思维链提示所迸发的强大推理能力。
在某些基准上，Zero-shot-CoT 超越了传统提供 8 个示例的 few-shot 提示效果，甚至逼近少样本思维链提示的水平。
few-shot-CoT 凭借人工设计的高质量示例依然是最强方案，但其需要针对每个任务定制示例，而 Zero-shot-CoT 一个通用提示走天下，大大降低了使用门槛。
实验还发现，模型规模是影响零样本思维链效果的关键因素：小型模型（如 GPT-3 Ada / Babbage 等数亿参数量级）几乎无法从这种提示中受益，推理正确率提升很小；而模型参数达到数十亿以上后，随规模增加，Zero-shot-CoT 带来的性能曲线显著上扬（对应一种能力涌现现象）。这与 few-shot 思维链在更大模型上效果激增的观察相一致。
最后，作者通过对生成结果的分析发现，Zero-shot-CoT 生成的推理过程即使在模型最终答案错误时往往也是合情合理的，体现出模型对问题的深入理解。此外，不同提示措辞的对比显示，只要提示短语包含让模型 “逐步思考” 的意图（如 “逐步推理”  “分步骤解决” 等），都能在一定程度上触发推理能力；但如果提示内容无关或误导，则难以奏效。这说明提示的语义恰当性对激发模型推理非常重要。
总的来说，实验结果充分证明了大型语言模型中潜藏的零样本推理能力，只需通过简单的提示即可被激活并服务于解决复杂任务。

---

## 3. 分析思考 Analysis & Thoughts

### 3.1 文章结论 Conclusions

LLM 具备被低估的零样本推理能力，只需极小的 Prompt 改动即可释放。这一发现重新定义了 “零样本能力” 的上限，并为后续推理类 Prompt 研究奠定基础。

### 3.2 个人思考 Personal Thoughts

Zero-shot CoT 以极简的方式带来了 LLM 性能的显著提升，但仍存在以下不足：

- Zero-shot CoT 强烈依赖模型规模，小模型难以受益。
- 推理过程并非总是严格正确，仍需验证机制。
- 该工作直接催生了 CoT-SC、Auto-CoT 等后续研究方向。

---

## 4. 关联文章 Related Works

- Chain of Thought Prompting
- CoT-SC
- Auto-CoT
- Tree of Thoughts Prompting
