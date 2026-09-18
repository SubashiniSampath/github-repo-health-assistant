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
    command=sys.executable,  # uses the same python interpreter you're running now
    args=[os.path.join(os.path.dirname(__file__), "..", "mcp_server", "server.py")],
)


async def ask_question(question: str):
    # Start the MCP server and connect to it
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Ask the MCP server what tools it has
            tools_result = await session.list_tools()

            # Convert MCP's tool format into the format Gemini expects
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

            # Send the question to Gemini, along with the list of available tools
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=question,
                config=types.GenerateContentConfig(tools=[gemini_tools]),
            )

            candidate = response.candidates[0]
            part = candidate.content.parts[0]

            # Did Gemini decide to call a tool?
            if part.function_call:
                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)

                print(f"[Gemini is calling tool: {tool_name} with {tool_args}]")

                # Actually run the tool via the MCP server
                tool_result = await session.call_tool(tool_name, tool_args)
                result_text = tool_result.content[0].text
                
                # Send the tool's result back to Gemini so it can write a final answer
                # Retry a few times if Gemini's servers are temporarily overloaded
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        follow_up = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[
                                question,
                                f"Tool '{tool_name}' returned this data: {result_text}",
                                "Now answer the original question in plain English using this data.",
                            ],
                        )
                        print("\nAnswer:", follow_up.text)
                        break  # success, exit the retry loop
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"[Gemini seems busy, retrying in 5 seconds... (attempt {attempt + 1}/{max_retries})]")
                            time.sleep(5)
                        else:
                            print(f"\nSorry, Gemini's servers seem busy right now. Please try again in a minute. (Error: {e})")
            else:
                # Gemini answered directly without needing a tool
                print("\nAnswer:", part.text)


if __name__ == "__main__":
    user_question = input("Ask a question about a GitHub repo: ")
    asyncio.run(ask_question(user_question))