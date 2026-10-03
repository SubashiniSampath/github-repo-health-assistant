print("Script started")
import asyncio
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import time

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

# This tells the client HOW to start our MCP server
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=[os.path.join(os.path.dirname(__file__), "..", "mcp_server", "server.py")],
)

MODEL_NAME = "gemini-3.6-flash"


def call_gemini_with_retry(contents, tools_config, max_retries=3):
    """Calls Gemini, retrying a few times if its servers are temporarily busy."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=tools_config,
            )
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[Gemini seems busy, retrying in 5 seconds... (attempt {attempt + 1}/{max_retries})]")
                time.sleep(5)
            else:
                raise e


async def ask_question(question: str) -> str:
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            gemini_tools = types.Tool(function_declarations=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.inputSchema.get("properties", {}),
                        "required": tool.inputSchema.get("required", []),
                    },
                }
                for tool in tools_result.tools
            ])
            tools_config = types.GenerateContentConfig(tools=[gemini_tools])

            # Keep a running conversation so Gemini can make multiple tool calls
            conversation = [question]
            max_tool_calls = 5  # safety limit, so it can't loop forever

            for _ in range(max_tool_calls):
                try:
                    response = call_gemini_with_retry(conversation, tools_config)
                except Exception as e:
                    return f"Sorry, Gemini's servers seem busy right now. Please try again in a minute. (Error: {e})"

                candidate = response.candidates[0]
                part = candidate.content.parts[0]

                if not part.function_call:
                    # Gemini is done calling tools and has given a final answer
                    print("\nAnswer:", part.text)
                    return part.text

                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)
                print(f"[Gemini is calling tool: {tool_name} with {tool_args}]")

                tool_result = await session.call_tool(tool_name, tool_args)
                result_text = tool_result.content[0].text

                # Add this tool call and its result into the conversation,
                # so Gemini can decide if it needs to call ANOTHER tool next
                conversation.append(f"[Called tool '{tool_name}' with {tool_args}]")
                conversation.append(f"Tool result: {result_text}")

            fallback = "Sorry, I wasn't able to fully answer that after several tool calls. Please try rephrasing your question."
            print("\nAnswer:", fallback)
            return fallback


if __name__ == "__main__":
    user_question = input("Ask a question about a GitHub repo: ")
    asyncio.run(ask_question(user_question))