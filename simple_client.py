from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25")

server_params = StdioServerParameters(
    command="uv",
    args=["run", "simple_server.py"],
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            return agent_response

if __name__ == "__main__":
    result = asyncio.run(run_agent())
    print(result)