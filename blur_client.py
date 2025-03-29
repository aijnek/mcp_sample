from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

#model = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25")
model = ChatGoogleGenerativeAI(model="gemini-2.0-pro-exp-02-05")

server_params = StdioServerParameters(
    command="uv",
    args=["run", "blur_server.py"],
)

#message = "sample_image.pngのサムネイルを作成してください"
#message = "sample_image.pngのサムネイルを作成してtemp.pngに保存してください"
#message = "sample_image.pngの画像全体をぼかしてください"
#message = "sample_image.pngの画像左半分をぼかしてください"
#message = "sample_image.pngの画像左半分をぼかしてください.ファイル名は処理内容がわかる適切なものにしてください"
#message = "sample_image.pngの顔が写っている場所を教えてください"
message = "sample_image.pngの顔が写っている部分をぼかしてください"

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": message})
            return agent_response

if __name__ == "__main__":
    result = asyncio.run(run_agent())
    print(result)
