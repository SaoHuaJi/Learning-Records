---
name: "SciAgent: A Unified Multi-Agent System for Generalistic Scientific Reasoning"  
uri: "https://arxiv.org/abs/2511.08151"  
tags: ["多智能体系统", "通用科学推理", "层次化推理", "跨学科推理"]  
type: "paper"  
subjects: ["Artificial Intelligence", "Computation and Language", "Multiagent Systems"] 
authors: ["Xuchen Li", "Ruitao Wu", "Xuanbo Liu", "Xukai Wang", "Jinbo Hu", "Zhixin Bai", "Bohan Zeng", "Hao Liang", "Leheng Chen", "Mingrui Chen", "Haitian Zhong", "Xuanlin Yang", "Xu-Yao Zhang", "Liu Liu", "Jia Li", "Kaiqi Huang", "Jiahao Xu", "Haitao Mi", "Wentao Zhang", "Bin Dong"]  
affiliations: ["Zhongguancun Academy", "Tencent AI Lab", "Chinese Academy of Sciences", "Beihang University", "Peking University", "Nanjing University"]  
year: 2025  
venue: "arXiv"  
language: "en"  
citation: |
  @misc{li2025sciagentunifiedmultiagentgeneralistic,
    title={SciAgent: A Unified Multi-Agent System for Generalistic Scientific Reasoning}, 
    author={Xuchen Li and Ruitao Wu and Xuanbo Liu and Xukai Wang and Jinbo Hu and Zhixin Bai and Bohan Zeng and Hao Liang and Leheng Chen and Mingrui Chen and Haitian Zhong and Xuanlin Yang and Xu-Yao Zhang and Liu Liu and Jia Li and Kaiqi Huang and Jiahao Xu and Haitao Mi and Wentao Zhang and Bin Dong},
    year={2025},
    eprint={2511.08151},
    archivePrefix={arXiv},
    primaryClass={cs.AI},
    url={https://arxiv.org/abs/2511.08151}, 
  }

# 自定义状态与评分（可选）
importance: 3
difficulty: 2
recommend: 2
---

# SciAgent: A Unified Multi-Agent System for Generalistic Scientific Reasoning

## 1. 概览 Overview

### 1.1 个人预览 Personal Preview

> 研究者设计了一个层次化架构的多智能体系统来实现通用科学推理并取得了不错的效果。但是领域扩展仍需人工介入来组织工作系统，自适应性还可以进一步提升。

### 1.2 内容简介 Description

- **研究背景 Research Background：**
大型语言模型的崛起使人工智能在特定科学问题上达到专家水平，但现有系统往往为某一领域手工定制，缺乏跨领域通用性。不同学科的问题（数学推导、物理建模、化学反应等）需要不同的推理策略，如何让一个AI系统灵活适应多种科学推理范式是一个重大挑战。  
- **研究目标 Research Objectives：**
作者旨在研发一个通用科学推理系统，能够根据问题所属的学科领域和复杂程度自适应调整解题策略。该系统应当摆脱预先固定的单一流程，具备在数学、物理、化学乃至综合考试等不同场景下自行组合推理步骤的能力，实现跨学科的一致推理框架。  
- **主要贡献 Main Contributions：**
本文的主要贡献包括：提出了SciAgent层次化多智能体架构，以协调者-工作系统-子智能体三层结构模拟科研团队的分工协作模式，实现控制与执行的分离；设计了动态自适应推理管道，支持子智能体在解题过程中通过反馈循环不断修正和优化中间结果，直到收敛得出正确解答；实证验证了系统的通用性，在数学、物理奥赛等高难度 benchmark 中取得了媲美甚至超越人类顶尖选手的成绩，并且无需为新领域手工打造新的推理流程，只需增添相应的工作智能体即可扩展到化学等领域。

---

## 2. 关键信息 Key Information

### 2.1 核心思想与方法 Main Ideas & Methods

- **层次化架构：**
SciAgent采用三层级的多智能体架构，类似科研团队的组织方式。最顶层是协调者智能体（Coordinator），负责进行元推理：判断问题所属领域（数学、物理、化学或综合）及难度，选择合适的解题策略和调用相应的工作系统（Worker）。中间层的每个工作系统对应一个大类领域的问题求解范式，例如数学工作系统采用符号推导为主的策略，物理工作系统融入了ReAct风格的思考-行动循环以处理图像和实验情景，化学工作系统扩展了工具调用（如分子识别和SMILES验证）以处理化学结构推理等。最底层是多个子智能体（Sub-agents），它们各司其职，负责具体的推理步骤，包括符号推理（公式推导、定理证明）、概念建模（将情景转化为方程或模型）、数值计算（执行计算和代码求解）、验证与总结（检查结果一致性并生成总结）等。这种层次化设计实现了元推理控制与具体执行的解耦，使系统能够在高层面对不同领域进行决策，在低层调用专业模块执行推理。
![SciAgent架构示意图](./Resources/SciAgent%20-%20Framework.png)
- **模块化专业化：**
SciAgent 强调模块化设计，不同学科的推理流程由独立的工作系统封装，实现专业化的子模块协作。例如，数学领域由 “生成-改进-审阅” 三类智能体构成循环，持续生成证明步骤、优化解答并审核正确性；物理领域则包含 “生成-图像分析-总结-审阅” 等子智能体，通过交互式多模态推理逐步解决问题。化学领域增加了分子结构识别和化学知识子智能体，以处理化学反应机制推理。这种模块化让每个工作系统专注于本领域的推理范式，同时通过统一的协调者接口，使新增领域的支持变得相对容易——添加一个新的工作系统即可扩展到新的学科，而无需改动其他模块。模块化与专业化保证了可扩展性和领域泛化能力：SciAgent 能够集成多种推理风格，同时保持整体架构的一致性和稳定性。  
- **自适应推理管道：**
在具体求解过程中，SciAgent并非使用固定脚本，而是采用动态管道组装与反馈循环。当协调者将问题分配给相应工作系统后，工作系统会根据高层策略实例化一系列子智能体组成初始解题流程。接下来各子智能体按照顺序对共享状态进行操作（例如提出解答、改进方案、检查错误），循环迭代。每一轮迭代结束后，系统根据当前解答的反馈动态调整管道：如果发现新的需求（比如需要额外计算或验证），可以临时插入新的子智能体（如引入验证者或模型分析器）；如果解答已收敛满足要求，则终止循环输出结果。以数学工作系统为例，其执行流程为：生成器提出初步解答，改进器细化推理，审阅者检查证明是否成立；若审阅未通过，则根据审阅反馈由生成器针对性纠错，进入下一循环。这种循环一直持续，直到审阅者多次通过验证或达到收敛条件为止。通过持续的自我反馈与纠错机制，SciAgent能够纠正中间推理中的漏洞（例如漏乘常数或逻辑跳步），显著提高最终答案的正确性和稳健性。自适应管道组装使系统具备推理适应性：能针对不同问题动态优化解题步骤，而不是一成不变地套用预定流程。这种灵活性对于应对跨领域、不同难度的问题至关重要，也是SciAgent能够通用适应多种科学任务的关键。  

### 2.2 实验设置与结果 Experimental Settings & Results

- **实验设置 Experimental Settings：**
作者在多个高难度科学推理基准上评估了SciAgent的性能，主要包括数学与自然科学领域的奥林匹克竞赛难题以及一个综合性的跨学科测试集。具体测试集包括：国际数学奥林匹克（IMO 2025）及国际数学竞赛（IMC 2025）题目、国际物理奥林匹克（IPhO 2024 / 2025）和中国物理奥赛（CPhO 2025）题目、国际化学奥林匹克（IChO 2025）部分题目，以及 *Humanity’s Last Exam (HLE)* 基准中的精选题目。这些题目涵盖了纯数学证明、物理建模与计算、化学反应机理推断、综合常识推理等不同类型，难度接近人类顶尖高中生乃至本科生水平。实验通过让SciAgent在无需人工干预下独立求解这些题目，并将其解题表现与人类金牌选手的成绩进行对比。在部分基准中，还比较了标准LLM直接求解的情况，以评估SciAgent相对于单一LLM策略的优势。此外，作者进行了消融实验来探究架构中各组件的重要性：分别移除协调者智能体（将所有子智能体置于同一层）或关闭验证子智能体等，观察对整体成绩的影响。
- **实验结果 Experimental Results：**
SciAgent在所有测试基准上均取得了优异的成绩，达到了人类顶尖水平。在数学方面，SciAgent在IMO 2025中得分36分（满分42，与金牌平均35.94相当），在IMC 2025中更是取得满分100分（金牌平均89.08）。物理方面，SciAgent在IPhO 2025中得分25.0 / 30，接近最高得分29.2，超过金牌平均23.4；在CPhO 2025（满分320）中得分264，远高于历史金牌平均199，接近最高纪录。这些结果表明SciAgent的解题能力已接近或超越人类金牌选手。在化学领域，SciAgent能够给出正确的反应机制、SMILES分子式和化学计量比等答案，展示了一定的化学推理能力，但由于IChO目前缺乏官方汇总评分，尚无法直接与人类总体水平比较。对于综合性的HLE基准，SciAgent也能够稳定地给出正确解答，而标准的大型语言模型在许多此类跨领域难题上往往失败——这进一步证明了SciAgent在跨学科推理上的优势。  
值得关注的是，SciAgent在不同领域中使用的是相同的一套核心框架和协议，只在扩展时新增了针对化学和综合考试的工作智能体，而无需为每种比赛单独设计解题流程。这体现了其架构的通用性：一个统一的系统就能胜任多种类型的科学推理任务。消融实验的结果揭示了架构各部分对性能的贡献：如果拿掉顶层协调者（即不进行分层调度），在混合数学-物理题目的测试中总分会下降约10–15%，这表明元规划与路线选择对于综合问题求解是不可或缺的；而关闭验证子智能体的功能后，数值计算类问题的错误率大约翻倍，凸显了持续自检机制对保障推理正确性的必要性。综上，实验充分证明了SciAgent架构在提高科学难题求解能力和跨领域适应性方面的有效性，为迈向通用科学智能提供了实证支持。

---

## 3. 分析思考 Analysis & Thoughts

### 3.1 文章结论 Conclusions

- **总结：**
该文章提出了 SciAgent，一个旨在跨学科和不同难度级别进行通用科学推理的统一多智能体系统。与先前的特定领域方法不同，SciAgent 将科学问题解决实现为专业推理智能体之间的自适应协调过程，在分层 “协调者智能体–工作系统–子智能体” 框架下组织。通过这种架构，系统动态识别问题领域，组装多阶段推理管道，并在单一框架内整合符号演绎、概念建模和定量计算。

- **展望：**
(1) 扩展到其他科学领域。
(2) 多模态科学推理。
(3) 协同与自我进化的智能体。
(4) 与真实科学工作流程的集成。

### 3.2 个人思考 Personal Thoughts

感觉就是完善的 ACPs 能包含的示例，里面的协调者对应 Leader，工作系统对应群组环境（不过它这个系统是预定义的，而完善的 ACPs 里的群组应该是动态自组织的），子智能体对应 Partner（包含 Tool Agent）。它的实现是可以参考一下的。

---

## 4. 关联文章 Related Works

- HuggingGPT
- Reflexion
- ReAct
