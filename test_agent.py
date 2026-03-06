import asyncio
import json
import os
from openai import AsyncOpenAI
from openreward import OpenReward


async def test_with_openai():
    or_client = OpenReward()
    oai_client = AsyncOpenAI()

    MODEL_NAME = "gpt-5.2"
    ENV_NAME = "countdownenvironment"
    SPLIT = "test"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return

    environment = or_client.environments.get(
        name=ENV_NAME,
        base_url="http://localhost:8080"
    )

    tasks = await environment.list_tasks(split=SPLIT)
    print(f"Found {len(tasks)} tasks")

    # Define tool schema for combine_numbers
    tools = [{
        "type": "function",
        "name": "combine_numbers",
        "description": "Combine two numbers using an arithmetic operator.",
        "parameters": {
            "type": "object",
            "properties": {
                "index1": {
                    "type": "integer",
                    "description": "0-based index of first number"
                },
                "index2": {
                    "type": "integer",
                    "description": "0-based index of second number"
                },
                "operator": {
                    "type": "string",
                    "enum": ["+", "-", "*", "/"],
                    "description": "Arithmetic operator"
                }
            },
            "required": ["index1", "index2", "operator"],
            "additionalProperties": False
        }
    }]

    # Test first task
    for task in tasks[:1]:
        print(f"\n{'='*60}")
        print(f"Testing task: {task['id']}")
        print(f"{'='*60}")

        async with environment.session(
            task=task,
            secrets={"openai_api_key": OPENAI_API_KEY}
        ) as session:
            prompt = await session.get_prompt()
            input_list = [{"role": "user", "content": prompt[0].text}]
            finished = False
            turn = 0
            max_turns = 20

            while not finished and turn < max_turns:
                turn += 1
                print(f"\nTurn {turn}:")

                # Use responses.create(), NOT chat.completions.create()
                response = await oai_client.responses.create(
                    model=MODEL_NAME,
                    tools=tools,
                    input=input_list
                )

                # Response has 'output', NOT 'choices'
                input_list += response.output

                for item in response.output:
                    if item.type == "function_call":
                        print(f"Tool call: {item.name}")
                        print(f"Arguments: {item.arguments}")

                        tool_result = await session.call_tool(
                            item.name,
                            json.loads(str(item.arguments))
                        )

                        finished = tool_result.finished

                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": tool_result.blocks[0].text
                        })

                        print(f"Tool output: {tool_result.blocks[0].text}")
                        print(f"Reward: {tool_result.reward:.3f}")

                        if tool_result.finished:
                            print('\nGAME FINISHED!')
                            print(f"Final reward: {tool_result.reward:.3f}")
                            break

            if turn >= max_turns and not finished:
                print(f"\nReached max turns ({max_turns}) without finishing")


if __name__ == "__main__":
    asyncio.run(test_with_openai())
