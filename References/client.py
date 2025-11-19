import asyncio
import os
from typing import Any, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    """
    一个最小可用的 MCP Client：
    - 通过 stdio 启动 server.py
    - 列出工具
    - 调用 summarize_paper 并打印返回的 Markdown
    """

    # 1. 配置如何启动你的 MCP Server（就是现在这个 server.py）
    server_params = StdioServerParameters(
        command="python",          # 用 python 启动
        args=["server.py"],        # server 脚本路径（如果不在同一目录，请写绝对路径）
        env=os.environ.copy(),     # 继承当前环境变量
    )

    # 2. 建立 stdio 连接并创建 ClientSession
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 2.1 初始化 MCP 会话（握手、能力协商等）
            await session.initialize()

            # 2.2 列出可用工具，确认 summarize_paper 是否暴露成功
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print("🔗 已连接到 MCP Server")
            print("🛠️ 可用工具：", tool_names)

            if "summarize_paper" not in tool_names:
                print("❌ 没有找到 summarize_paper 工具，请检查 server 代码中的 @mcp.tool 装饰器。")
                return

            # 3. 准备调用 summarize_paper 所需的参数
            #    你也可以改成命令行参数 / 配置文件 / 交互式输入
            uri = input("请输入要总结的论文 URI / 本地路径 / arXiv ID / DOI：").strip()
            if not uri:
                print("❌ uri 不能为空")
                return

            # 尽量不要把 key 写死在代码里，从环境变量里读
            # api_key = os.environ.get("OPENAI_API_KEY")
            api_key = "sk-pafcemvohyyghtuqvvoziirlflfwnfvigrkesqcvtuksxary"
            if not api_key:
                api_key = input("请输入 OpenAI API Key（不会保存）：").strip()
            if not api_key:
                print("❌ API Key 不能为空")
                return

            # 如果你用 OpenAI 官方，就用默认；如果是自建网关，在这里改
            # base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            base_url = "https://api.siliconflow.cn/v1"

            # 你也可以把这些改成命令行参数
            # model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
            model = "Qwen/Qwen3-8B"
            language = "zh"
            note_style = "normal"  # "short" / "normal" / "long"
            only_sections = None   # 例如 ["概览", "方法", "个人思考"]

            arguments: Dict[str, Any] = {
                "uri": uri,
                "api_key": api_key,
                "base_url": base_url,
                "model": model,
                "language": language,
                "note_style": note_style,
                "only_sections": only_sections,
                # 下面这几个用默认值就好，也可以按需调整
                # "max_chars": 120_000,
                # "chunk_chars": 12_000,
                # "chunk_overlap_chars": 800,
            }

            print("\n⏳ 正在调用 summarize_paper 工具，请稍候...\n")

            # 4. 真正通过 MCP 调用工具
            call_result = await session.call_tool("summarize_paper", arguments)

            # 5. 解析并打印结果
            #    对于 FastMCP + 返回 str 的工具，通常会得到一个 TextContent，对应 .text
            print("✅ 调用成功，返回内容如下：\n")

            # call_result.content 是一个 content 列表
            for item in call_result.content:
                # 简单处理一下，只关注 text 类型
                if getattr(item, "type", None) == "text":
                    print(item.text)
                else:
                    # 以防以后工具返回别的类型，这里直接打印结构
                    print(repr(item))


if __name__ == "__main__":
    asyncio.run(main())
