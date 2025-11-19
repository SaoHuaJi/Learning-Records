# from __future__ import annotations
import os
import re
import tempfile
from pathlib import Path
from typing import Optional, List
import requests
from fastmcp import FastMCP
from openai import OpenAI
from pypdf import PdfReader


# ========= 1. 基础配置 =========

mcp = FastMCP(name="PaperSummarizerPlus")
default_template = """
---
# 基本信息
name: ""                                    # 论文 / 报告名称
uri: ""                                     # 原文链接 / DOI / 本地路径
tags: ["domain", "method", "task", ...]     # 关键词标签
type: "paper | report | blog ..."           # 文章类型
subjects: ["", ...]                         # 学科领域，比如: ML, CV, NLP, HCI...
authors: ["", ...]                          # 作者列表（可选）
affiliations: ["", ...]                     # 单位（可选）
year: 2000                                  # 发表年份
venue: ""                                   # 期刊 / 会议 / 报告来源
language: "en | zh | ..."                   # 原文语言
citation: ""                                # BibTeX/APA/MLA 等引用信息

# 自定义状态与评分（可选）
importance: 3   # 1-5 主观重要性评分
difficulty: 3   # 1-5 阅读难度评分
recommend: 3    # 1-5 推荐再读评分
---

# 文章名称

## 1. 概览 Overview

### 1.1 个人预览 Personal Preview

> 用自己的话对文章内容进行简要总结（参考如下）
>
> - 问题是什么？
> - 文章做了什么？
> - 结果大概怎样？
> - 对你个人有什么启发？

### 1.2 内容简介 Description

- **研究背景 Research Background：**
- **研究目标 Research Objectives：**
- **主要贡献 Main Contributions：**

---

## 2. 关键信息 Key Information

### 2.1 核心思想与方法 Main Ideas & Methods

- 文章的核心思想是什么？使用的方法是什么？

### 2.2 实验设置与结果 Experimental Settings & Results

- **实验设置 Experimental Settings：**
- **实验结果 Experimental Results：**

---

## 3 分析思考 Analysis & Thoughts

### 3.1 文章结论 Conclusions

- 文章的结论是什么？有什么意义？

### 3.2 个人思考 Personal Thoughts

- 文章有什么不足之处？对你有什么启发？有什么改进的想法？

---

## 4. 关联文章 Related Works

"""


# ========= 2. 读取 Template.md =========

def load_template(template_path: Optional[str] = None) -> str:
    """读取指定文件作为模板。若找不到，则返回回一个默认模板。

    Args:
        template_path (Optional[str]): 模板文件路径

    Returns:
        str: 模板内容
    """
    if not template_path or not Path(template_path).exists():
        return default_template
    else:
        return Path(template_path).read_text(encoding="utf-8", errors="ignore")


# ========= 3. 加载论文文本相关：PDF / 网页 / 本地 =========

def extract_text_from_pdf_bytes(data: bytes) -> str:
    """从 PDF 二进制内容中抽取纯文本。使用临时文件 + pypdf 简单实现。

    Args:
        data (bytes): PDF 二进制内容

    Returns:
        str: 抽取出的纯文本
    """
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(data)
        tmp_path = f.name
    try:
        reader = PdfReader(tmp_path)
        texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            texts.append(text)
        return "\n\n".join(texts)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def load_paper_text_from_uri(uri: str, timeout: Optional[int] = None) -> str:
    """传入“真实可访问”的 URI（http(s)/本地路径），返回论文纯文本。

    Args:
        uri (str): 纯文本文件路径
        timeout (Optional[int]): 请求超时时间

    Returns:
        str: 论文纯文本
    """
    # 远程资源（暂不支持 arXiv 介绍页自动跳转这种功能）
    if uri.startswith("http://") or uri.startswith("https://"):
        resp = requests.get(uri, timeout=timeout)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "").lower()
        if uri.lower().endswith(".pdf") or "application/pdf" in content_type:
            return extract_text_from_pdf_bytes(resp.content)
        else:
            # 对于 arXiv HTML 等，也先当纯文本处理（后面要改）
            return resp.text
    # 本地文件
    path = Path(uri).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")
    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf_bytes(path.read_bytes())
    # 不是 pdf 就当作纯文本文件处理
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


# ========= 4. DOI / arXiv / URI 归一化 =========

ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$", re.IGNORECASE)


def normalize_identifier_to_uri(identifier: str) -> str:
    """将用户传入的 uri 参数“智能识别”成一个真正可访问的 URI：
    - 已经是 http(s)/file:// → 原样返回
    - 本地路径存在          → 认为是本地文件
    - arxiv:2410.12345     → https://arxiv.org/pdf/2410.12345.pdf
    - 2410.12345           → 也当 arXiv 处理
    - 10.1145/...（含 / 且无空格）→ 当作 DOI，映射到 https://doi.org/<DOI>
    - 其他情况              → 尝试原样当作 URI（可能是自定义网关）

    Args:
        identifier (str): 用户传入的 URI 参数

    Returns:
        str: 归一化后的 URI
    """
    s = identifier.strip()
    # 1) 已经是 URL
    if s.startswith(("http://", "https://", "file://")):
        return s
    # 2) 本地文件
    path = Path(s).expanduser()
    if path.exists():
        return str(path.resolve())
    # 3) arXiv
    lower = s.lower()
    if lower.startswith("arxiv:"):
        arxiv_id = lower.split(":", 1)[1].strip()
        return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    if ARXIV_ID_RE.match(s):
        return f"https://arxiv.org/pdf/{s}.pdf"
    # 4) 简单认为是 DOI：包含 / 且没有空格
    if "/" in s and " " not in s:
        return f"https://doi.org/{s}"
    # 5) fallback：直接返回，交给 requests/文件系统去试
    return s


# ========= 5. 分块策略：按标题正则分段 =========

# 常见英文标题列表
COMMON_HEADING_KEYWORDS_EN = {
    "abstract",
    "introduction",
    "background",
    "conclusion",
    "conclusions",
    "discussion",
    "acknowlege",
    "acknowledgment",
    "acknowledgments",
    "acknowledgement",
    "acknowledgements",
    "appendix",
    "appendices",
    "references",
}

# 常见中文标题列表
COMMON_HEADING_KEYWORDS_ZH = {
    "摘要",
    "引言",
    "背景",
    "结论",
    "讨论",
    "致谢",
    "附录",
    "参考文献",
}

# 标题匹配模式
NUMERIC_HEADING_RE = re.compile(
    r"""
    ^\s*                            # 行首的0个或多个空白字符
    (?P<num>(\d{1,2}|[IVX]{1,4}))   # 至多2个数字或4个罗马数字
    [\.\)]?                         # 可选的 '.' 或 ')'
    \s+                             # 1个或多个空白字符
    (?P<title>.+?)                  # 标题主体
    \s*$                            # 行尾的0个或多个空白字符
    """,
    re.VERBOSE | re.IGNORECASE,
)


def is_numeric_heading_line(line: str) -> bool:
    """判断一行是否是“数字前缀 + 标题”的章节标题，例如：
    1 Introduction
    2. Related Work
    III Methods
    4 实验结果

    Args:
        line (str): 待判断的行文本

    Returns:
        bool: 是否是章节标题
    """
    # 匹配行首的数字前缀和标题
    m = NUMERIC_HEADING_RE.match(line)
    if not m:
        return False
    # 提取标题文本部分并检查是否为空
    title = m.group("title").strip()
    if not title:
        return False
    # 限制字数，防止整段文本被误判为标题
    if len(title) < 3 or len(title) > 120:
        return False
    # 检查单词数量，避免段落内容被误识别为标题
    words = title.split()
    if len(words) > 20:  # 超长就不是正常标题了
        return False
    # 字母占比要够高，避免一些“1 2024-01-01 Table 3.1”这种怪东西
    letters = sum(c.isalpha() for c in title)
    if letters < 3 or letters < len(title) * 0.4:
        return False
    return True


def is_common_non_numeric_heading_line(line: str) -> bool:
    """判断一行是否是常见的“无编号标题”，例如：
    ABSTRACT
    摘要
    ACKNOWLEDGMENTS
    致谢
    APPENDIX
    参考文献

    Args:
        line (str): 待判断的行文本

    Returns:
        bool: 是否是章节标题
    """
    # 去掉两端符号，只保留字母 / 数字 / 中文 和空格
    cleaned = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff ]+", "", line).strip()
    if not cleaned:
        return False
    # 过长就当正文，避免误判
    if len(cleaned) > 50:
        return False
    # 中文：看是否包含常见关键词
    if any(kw in cleaned for kw in COMMON_HEADING_KEYWORDS_ZH):
        return True
    lower = cleaned.lower()
    # 英文：完全匹配或以这些关键词构成的短语
    if lower in COMMON_HEADING_KEYWORDS_EN:
        return True
    # 比如 "related work" 这种两词组合
    if " " in lower:
        if any(lower == kw for kw in COMMON_HEADING_KEYWORDS_EN):
            return True
    # 进一步限制：最多 5 个单词
    if len(lower.split()) > 5:
        return False
    # 常见英文关键词前后带少量修饰的情况（不太激进）
    for kw in COMMON_HEADING_KEYWORDS_EN:
        if kw in lower and len(lower) - len(kw) <= 10:
            return True
    return False


def segment_text_by_headings(
    text: str, min_section_chars: int = 200
) -> List[str]:
    """利用“行级标题”对全文分段：
    1. 先按行 split，识别哪些行是“章节起始行”：
       - 数字 + 空格 + 标题（可带 '.' 或 ')'）
       - 常见无编号标题（ABSTRACT/摘要/致谢/附录/参考文献 等）
    2. 每个标题行到下一个标题行之间视为一段，标题行保留在这一段里。
    3. 标题之前的头部（例如论文名、作者列表）视为单独一段（preface）。
    4. 对过短的段落，与前一个段落合并，减少碎片。
    如果没有识别出任何标题，则返回 [text] 交给上层按长度分块兜底。

    Args:
        text (str): 待分段的文本
        min_section_chars (int): 最小段落长度，小于此长度的段落会与前一段合并

    Returns:
        List[str]: 分段后的文本列表
    """
    lines = text.splitlines(keepends=True)
    n = len(lines)
    heading_indices: List[int] = []
    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        # 空行或过长行跳过
        if not line or len(line) > 50:
            continue
        if is_numeric_heading_line(line) \
                or is_common_non_numeric_heading_line(line):
            heading_indices.append(i)
    # 若完全没命中标题则交给上层处理
    if not heading_indices:
        return [text]
    # 按标题分段
    sections: List[str] = []
    # 0) 标题之前的“前言部分”
    first_idx = heading_indices[0]
    if first_idx > 0:
        preface = "".join(lines[0:first_idx]).strip()
        if preface:
            sections.append(preface)
    # 1) 标题分段
    for idx, h_idx in enumerate(heading_indices):
        start = h_idx
        end = heading_indices[idx + 1] if idx + 1 < len(heading_indices) else n
        chunk = "".join(lines[start:end]).strip()
        if chunk:
            sections.append(chunk)
    # 2) 合并过短 section，避免太碎
    merged: List[str] = []
    for sec in sections:
        if not merged:
            merged.append(sec)
            continue
        if len(sec) < min_section_chars:
            merged[-1] = merged[-1].rstrip() + "\n\n" + sec.lstrip()
        else:
            merged.append(sec)
    return merged


def iter_text_chunks_length(
    text: str,
    chunk_size: int = 12_000,
    overlap: int = 800,
):
    """简单的字符级 sliding window 分块迭代器。仅用作“按标题分段失败时”的兜底策略。

    Args:
        text (str): 待分块的文本
        chunk_size (int): 每块字符数
        overlap (int): 每块重叠字符数

    Yields:
        str: 分块文本
    """
    n = len(text)
    if n <= chunk_size:
        yield text
        return
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        yield text[start:end]
        if end == n:
            break
        start = end - overlap


# ========= 6. LLM 调用：分块总结 + 模板生成 =========

def _note_style_instruction(note_style: str) -> str:
    """根据 note_style 参数返回相应的指令。
    """
    note_style = (note_style or "normal").lower()
    if note_style == "short":
        return "整体偏简洁，抓住主要贡献、核心方法和结论即可，控制篇幅适中，不要过度展开细节。"
    if note_style == "long":
        return "尽量详细，适当展开公式推导思路、实验设置、消融结果和作者讨论，适合深入学习。"
    # normal
    return "信息量适中，既涵盖主要贡献和方法，也保留关键的实验与结论，但不需要面面俱到。"


def _only_sections_instruction(only_sections: Optional[List[str]]) -> str:
    """根据 only_sections 参数返回相应的指令。
    """
    if not only_sections:
        return (
            "请尽量覆盖模板中的所有主要模块，如果内容确实缺失，可以简要说明“原文未提及”。"
        )
    joined = ", ".join(only_sections)
    return (
        "本次重点关注的笔记章节为："
        f"{joined}。在生成时：\n"
        "- 这些章节请写得更完整、更细致；\n"
        "- 模板中其他章节可以简写、留空或简要说明“略”，但标题结构尽量保留。"
    )


def call_llm_with_template(
    paper_representation: str,
    original_uri: str,
    client: OpenAI,
    model: str = "gpt-4.1-mini",
    *,
    template_path: Optional[str] = None,
    language: str = "中文",
    note_style: str = "normal",
    only_sections: Optional[List[str]] = None,
) -> str:
    """
    使用 Template.md + LLM 生成最终学习笔记。

    paper_representation 可以是整篇正文，也可以是分块汇总后的"二级摘要"。
    """
    style_instruction = _note_style_instruction(note_style)
    sections_instruction = _only_sections_instruction(only_sections)
    template = load_template(template_path)
    system_prompt = f"""
你是一个严谨、细致的论文阅读助手。

现在有一篇学术论文的内容（可能已经是分块摘要汇总后的文本），
请你 **只用 Markdown 格式**，严格按照下面给定的模板结构生成一份学习笔记：

----------------- 模板开始 -----------------
{template}
----------------- 模板结束 -----------------

强约束与要求：

1. **必须保留** 所有标题结构与字段名（包括英文 / 中文小标题），只替换其中的内容。
2. `uri` 字段请填入用户原始提供的标识：`{original_uri}`。
3. 如果原文没有明确信息，可以合理写"未知"或留空，但字段要保留。
4. 所有内容请使用 **{language}** 输出（模板中的英文标题可以保留不变）。
5. 笔记长度与详略风格：{style_instruction}
6. 关于重点章节：{sections_instruction}
7. 不要额外增加模板之外的章节（比如"附录""额外说明"等），也不要输出模板外的多余文本。
""".strip()

    user_prompt = f"""
下面是这篇论文的内容表示（可能是原文，也可能是分块摘要的汇总）：

\"\"\"{paper_representation}\"\"\"
""".strip()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    # 处理可能为None的情况
    content = resp.choices[0].message.content
    return content.strip() if content else ""


def summarize_chunk(
    chunk_text: str,
    client: OpenAI,
    model: str = "gpt-4.1-mini",
    *,
    language: str = "中文",
    note_style: str = "normal",
) -> str:
    """对单个文本块做"中间层摘要"，供后续汇总成整篇笔记使用。

    Args:
        chunk_text (str): 待总结的文本块
        client (OpenAI): OpenAI API 客户端
        model (str): LLM 模型
        language (str): 笔记语言
        note_style (str): 笔记风格

    Returns:
        str: 摘要文本
    """
    style_instruction = _note_style_instruction(note_style)
    system_prompt = f"""
你是论文"分块总结"助手。

现在给你论文的一部分内容，请你对这一部分进行结构化总结，
总结结果只作为后续整篇笔记的输入中间层使用。

要求：

1. 输出语言使用 **{language}**。
2. 使用 Markdown，适当用小标题与列表组织结构。
3. 尽量提取：
   - 这一部分涉及的背景/问题；
   - 关键概念或定义；
   - 方法/算法的核心步骤或公式要点（无需写具体公式编号）；
   - 实验设置的关键信息（数据集、指标、对比方法等，如果有的话）；
   - 重要结论或观察。
4. 不需要严格套用 Template.md，只要条理清晰即可。
5. 笔记长度风格：{style_instruction}
    """.strip()

    user_prompt = f"""
下面是论文的一部分内容，请进行分块总结：

\"\"\"{chunk_text}\"\"\"
    """.strip()

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    # 处理可能为None的情况
    content = resp.choices[0].message.content
    return content.strip() if content else ""


def summarize_paper_hierarchical(
    full_text: str,
    original_uri: str,
    api_key: str,
    base_url: str,
    model: str = "gpt-4.1-mini",
    *,
    template_path: Optional[str] = None,
    language: str = "zh",
    note_style: str = "normal",
    only_sections: Optional[List[str]] = None,
    no_chunks: bool = False,
    chunk_size: int = 12000,
    chunk_overlap: int = 800,
    direct_threshold: int = 18000,
) -> str:
    """分层总结入口（优先按“标题分段”，失败时按长度分块兜底）：
    - 若全文长度不大于 direct_threshold：直接调用模板总结一次搞定；
    - 否则：
      1) 尝试按标题模式 segment_text_by_headings；
      2) 若能分出多段：
         - 每段调用 summarize_chunk
         - 把所有段摘要拼起来 → 再调用 call_llm_with_template 生成最终笔记。
      3) 若没分成功（只有 1 段）：
         - fallback：使用长度分块 iter_text_chunks_length → 分块摘要 → 汇总。

    Args:
        full_text (str): 全文内容
        original_uri (str): 原始论文 URI
        api_key (str): OpenAI API Key
        base_url (str): OpenAI API Base URL
        model (str): LLM 模型
        template_path (Optional[str]): 模板文件路径
        language (str): 笔记语言
        note_style (str): 笔记风格
        only_sections (Optional[List[str]]): 仅生成指定部分
        chunk_size (int): 分块大小
        chunk_overlap (int): 分块重叠大小
        direct_threshold (int): 直接生成阈值

    Returns:
        str: 最终笔记内容
    """
    client = OpenAI(api_key=api_key, base_url=base_url)
    # 论文不长或要求不切片时时直接一次性按模板生成
    if no_chunks or len(full_text) <= direct_threshold:
        return call_llm_with_template(
            paper_representation=full_text,
            original_uri=original_uri,
            client=client,
            model=model,
            template_path=template_path,
            language=language,
            note_style=note_style,
            only_sections=only_sections,
        )
    # 1) 按标题分段
    sections = segment_text_by_headings(full_text)
    use_heading_based = len(sections) > 1
    # 完全没匹配到能用于分段的标题，退回按长度分块策略
    if not use_heading_based:
        chunk_summaries = []
        for idx, chunk in enumerate(
            iter_text_chunks_length(full_text, chunk_size, chunk_overlap),
            start=1,
        ):
            summary = summarize_chunk(
                chunk_text=chunk,
                client=client,
                model=model,
                language=language,
                note_style=note_style,
            )
            chunk_summaries.append(f"## 长度分块 {idx} 的摘要\n\n{summary}")
        combined_summary = "\n\n".join(chunk_summaries)
    else:
        # 用“标题分段”结果
        chunk_summaries = []
        for idx, sec in enumerate(sections, start=1):
            summary = summarize_chunk(
                chunk_text=sec,
                client=client,
                model=model,
                language=language,
                note_style=note_style,
            )
            chunk_summaries.append(f"## 标题分段 {idx} 的摘要\n\n{summary}")
        combined_summary = "\n\n".join(chunk_summaries)
    # 2) 用分块汇总结果走模板生成最终笔记
    return call_llm_with_template(
        paper_representation=combined_summary,
        original_uri=original_uri,
        client=client,
        model=model,
        template_path=template_path,
        language=language,
        note_style=note_style,
        only_sections=only_sections,
    )


# ========= 7. MCP 工具定义：summarize_paper =========

@mcp.tool()
def summarize_paper(
    uri: str,
    api_key: str,
    base_url: str,
    model: str = "gpt-4.1-mini",
    language: str = "中文",
    note_style: str = "normal",
    only_sections: Optional[List[str]] = None,
    no_chunks: bool = True,
    max_chars: int = 500000,
    chunk_chars: int = 10000,
    chunk_overlap_chars: int = 800,
    timeout: int = 300,
) -> str:
    """使用 LLM 自动阅读并总结指定 uri 对应的论文，返回符合指定模板结构的学习笔记。

    Args:
        uri (str): 论文标识，可以是：
            - 远程 HTTP(S) 链接（PDF / HTML 等）
            - 本地文件路径（PDF / TXT / MD ...）
            - arXiv ID：如 "arxiv:2410.12345" 或 "2410.12345"
            - DOI：如 "10.1145/1234567.8901234"
        api_key (str): OpenAI API 密钥
        base_url (str): OpenAI API 基础 URL
        model (str, optional): 用于一切总结调用的模型名称
        language (str, optional): 输出语言（"zh" 或 "en" 最常用）
        note_style (str, optional): 笔记风格:
            - "short"  : 精简版；
            - "normal" : 适中；
            - "long"   : 尽量详细
        only_sections (List[str] | None, optional): 若不为空，则表示你想重点关注
            的章节名（可以是中文标题片段），模板中这些章节会写得更详细，
            其他章节可以略写或留空. 示例：["概览", "方法", "个人思考"]
        max_chars (int, optional): 为防止极端长文导致调用次数过多，先对全文进行简单截断（按字符数）
        chunk_chars (int, optional): 分块时单块的最大字符数
        chunk_overlap_chars (int, optional): 相邻块之间的重叠字符数，多一点重叠有助于跨块信息连续
        timeout (int, optional): 超时时间（秒）

    Returns:
        str: 符合指定模板结构的学习笔记
    """
    # 标准化 note_style
    note_style = (note_style or "normal").lower()
    if note_style not in {"short", "normal", "long"}:
        note_style = "normal"
    # 将用户输入的 uri 归一化为真正可访问的 URI
    real_uri = normalize_identifier_to_uri(uri)
    # 1. 加载全文文本
    full_text = load_paper_text_from_uri(real_uri, timeout)
    # 2. 极端长度保护（按字符截断）
    if not no_chunks and len(full_text) > max_chars:
        full_text = full_text[:max_chars]
    # 3. 分层总结（内部会根据长度自动决定是否分块）
    summary_md = summarize_paper_hierarchical(
        full_text=full_text,
        original_uri=uri,  # 模板中的 uri 字段写用户原始输入更直观
        api_key=api_key,
        base_url=base_url,
        model=model,
        language=language,
        note_style=note_style,
        only_sections=only_sections,
        no_chunks=no_chunks,
        chunk_size=chunk_chars,
        chunk_overlap=chunk_overlap_chars,
    )
    return summary_md


# ========= 8. 入口 =========

if __name__ == "__main__":
    mcp.run()
