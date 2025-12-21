---
name: "Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks"
uri: "https://arxiv.org/abs/2211.12588"
tags: ["程序化思维", "思维链", "提示工程", "LLM", "数值推理"]
type: "paper"
subjects: ["Artificial Intelligence", "Computation and Language"]
authors: ["Wenhu Chen", "Xueguang Ma", "Xinyi Wang", "William W. Cohen"]
affiliations: ["University of Waterloo", "Vector Institute, Toronto", "University of California, Santa Barbara", "Google Research"]
year: 2023
venue: "TMLR 2023"
language: "en"
citation: |
    @article{chen2022program,
        title={Program of thoughts prompting: Disentangling computation from reasoning for numerical reasoning tasks},
        author={Chen, Wenhu and Ma, Xueguang and Wang, Xinyi and Cohen, William W},
        journal={arXiv preprint arXiv:2211.12588},
        year={2022}
    }

importance: 4
difficulty: 2
recommend: 2
---

# Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks

## 1. 概览 Overview

### 1.1 个人预览 Personal Preview

> 针对复杂数值推理任务，文章提出了 “程序化思维 (Program-of-Thoughts, PoT) 提示”，将多步推理过程表示为可执行程序并交由计算机完成数值计算，从而将计算与逻辑推理解耦。通过在数学文字题和金融问答数据集上的评估，PoT 方法相比传统的思维链提示（CoT）平均性能提升约 12%，结合自洽采样策略后在多项基准上达到新的水平。

### 1.2 内容简介 Description

- **研究背景 Research Background：**
近年来 LLM 在逐步推理复杂问题上取得了显著进展，尤其是思维链提示（CoT）显著提升了模型在数学和常识推理任务上的表现。然而，CoT 依赖模型自身在自然语言思维链中同时完成推理和计算，这使得模型在处理大数算术、复杂方程或多次迭代时容易出错。随着应用需求增长，如何有效利用外部工具提高 LLM 的数值计算准确性成为新的挑战。
- **研究目标 Research Objectives：**
文章旨在通过一种新的提示方法，将复杂计算委托给外部执行，从而提升 LLM 在数值推理任务上的准确性和可靠性。具体目标包括：提出 PoT 提示范式，让模型以生成程序的方式来进行推理；验证该方法在不同类型的数据集（数学问题、金融问答）下的有效性，包括零样本和少样本设置；并通过实验分析这种方法的优劣与影响因素。
- **主要贡献 Main Contributions：**
&emsp;&emsp;(1) 提出了 Program-of-Thoughts (PoT) Prompting 方法，引导语言模型将推理过程表示为可执行的 Python 程序代码，由外部解释器执行计算，从而成功将繁琐计算与逻辑推理相分离。
&emsp;&emsp;(2) 在 5 个数学文字题数据集（GSM8K、AQuA、SVAMP、TabMWP、MultiArith）和 3 个财务问答数据集（FinQA、ConvFinQA、TAT-QA）上进行评估，PoT 在零样本和少样本场景下相对于 CoT 平均准确率提升约 12%，并通过结合自洽性解码进一步将各数据集性能推向新的状态。
&emsp;&emsp;(3) 通过大量对比实验和消融分析深入探讨了 PoT 提示的有效性来源，包括与传统 CoT+计算器辅助、CoT+自洽采样等方法的比较。

---

## 2. 关键信息 Key Information

### 2.1 核心思想与方法 Main Ideas & Methods

- **核心思想：**
针对 LLM 在纯语言推理中易犯的计算错误，作者提出将复杂计算步骤外包给计算机完成。PoT 提示要求模型在推理时生成可执行的代码（如 Python 脚本），利用代码中的循环、库函数等来处理繁琐的算术或方程求解。模型只需负责将问题转化为正确的程序逻辑，从而专注于理解和规划，而将具体数值计算交由 Python 解释器精确完成。通过这种 PoT 方式，LLM 能解决诸如多步累加、求解高次多项式等超出其直接计算能力的任务，大幅降低由长链推理累积误差导致出错的概率。
![Framework](Resources/PoT%20-%20Framework.png)
上图展示了 CoT 与 PoT 在解题流程上的区别：CoT 模型需要在 50 次迭代累加中每一步都正确，而 PoT 模型仅需编写几行循环代码即可精确完成相同计算。
- **实现方法：**
PoT 提示的实现分为少样本与零样本两种方式，如下图所示：
![Prompt](Resources/PoT%20-%20Prompt.png)
并不是所有问题都适合完全用代码解决，因此 PoT 应该和 CoT 结合使用，以获得更好的效果。
![+CoT](Resources/PoT%20-%20Combined%20with%20CoT.png)

### 2.2 实验设置与结果 Experimental Settings & Results

- **实验设置 Experimental Settings：**
作者选取了广泛的数值推理基准进行测试，包括 5 个数学文字题数据集（如 GSM8K）以及 3 个财务表格问答数据集（如 FinQA）。这些数据覆盖了纯文本题目、表格数据、对话式问答等不同形式，验证 PoT 提示的通用性。评估分别在少样本提示和零样本提示下进行。对于 CoT 基线，作者还考虑了一种变体：在 CoT 生成的中间算式由外部计算器执行（记作 CoT+calc），以比较 PoT 直接生成代码与 CoT 加辅助工具的差异。此外，在推理生成答案时，作者引入了自洽性 (self-consistency) 解码策略：即让模型对同一问题采样生成多个不同程序 / 思路，执行得到多个答案，再通过投票选择最一致的答案。

- **实验结果 Experimental Results：**
PoT 提示在各数据集上均显著超越 CoT 基线。在少样本设置下，PoT 对数学问题的平均准确率比 CoT 提高约 8%，对金融数据集提高约 15%；零样本下则对数学类任务平均提升约 12%。相比之下，使用计算器辅助的 CoT+calc 也有一定改进，但仍不及直接让模型产出程序的效果。进一步，结合自洽性策略后，PoT+SC 相较 CoT+SC 平均额外获得约 10% 的准确率提升。具体而言，在 GSM8K 等数学基准上 PoT+SC 刷新了此前最高成绩，在 FinQA 等金融任务上也达到与当前最佳模型相当的水平（除去 GPT-4 等更大型的模型外）。综上，PoT 提示不仅在模型未经微调的 few-shot 场景下效果突出，也展现了与采样融合的强大潜力。

---

## 3 分析思考 Analysis & Thoughts

### 3.1 文章结论 Conclusions

- **计算与推理可解耦：**
文章证明了通过 PoT 提示让模型调用外部计算，可以极大提高数值推理的准确性和可靠性。LLM 不再需要在语言环境中 “心算”，而是扮演规划者角色，将计算任务转交给计算机完成。这一解耦使模型在需要多步迭代或复杂公式推导的问题上表现出色，显著减少了中间计算错误的传播。
- **程序思维具备通用性：**
通过大量实验，PoT 在不同领域的数据集上（数学、金融）均取得了远超 CoT 的效果。特别是在引入自洽采样后，PoT 方法达到了这些任务目前已知的最优或接近最优成绩。这表明将编程能力引入推理流程是一种通用且强大的范式，对于各类需要逻辑推理和精确计算的任务都具备借鉴意义。

### 3.2 个人思考 Personal Thoughts

- 工具增强 LLM：PoT 的成功凸显了工具增强型 LLM 的前景——即让模型善用外部程序、库函数来弥补自身计算或专业能力的不足。未来研究可在更多类型的推理任务上探索类似思想，例如涉及日期计算、逻辑证明等领域，进一步拓展 LLM 解决复杂任务的边界。同时需要注意，在实际应用中集成代码执行模块也带来了安全性和复杂性挑战，如何在保证可靠性的前提下安全地执行模型生成的程序将是重要课题（不直接让 LLM 解决问题而是让 LLM 实现解决问题的代码就有可能带来实现的代码不安全可靠这一问题）。证明了提示词工程的重要性，并给出了思维链提示范例，为后来的研究者指明了方向。
- 方法局限：尽管 PoT 大幅提升了计算类问题的表现，但其应用场景仍局限于有明确程序解法的问题类型。例如，对于纯粹逻辑推理或常识问答，未必存在可供直接调用的现成工具库，此时程序生成未必有优势。此外，PoT 对提示的构造要求更高，需要示例教会模型如何书写合适的代码；对模型本身的编程知识也有一定依赖（尤其在零样本时）。模型生成的代码可能存在错误或低效之处，需要完善的执行监控和异常处理机制来确保最终答案可靠。

---

## 4. 关联文章 Related Works

- Zero-shot CoT
- Auto CoT
- CoT-SC
- Tree of Thoughts Prompting
