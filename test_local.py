import asyncio
from openreward import OpenReward


async def test_locally():
    client = OpenReward()

    # Connect to local server
    env = client.environments.get(
        name="countdownenvironment",
        base_url="http://localhost:8080"
    )

    # Get tasks
    tasks = await env.list_tasks(split="test")
    print(f"Found {len(tasks)} tasks")

    example_task = tasks[0]
    print(f"Testing task: {example_task['id']}")

    # Test with session
    async with env.session(task=example_task) as session:
        # Test prompt generation
        prompt = await session.get_prompt()
        print(f"\nPrompt:\n{prompt[0].text}\n")

        # Test tool call - combine first two numbers with addition
        result = await session.call_tool("combine_numbers", {
            "index1": 0,
            "index2": 1,
            "operator": "+"
        })

        print(f"Turn 1 Result:\n{result.blocks[0].text}")
        print(f"Reward: {result.reward}")
        print(f"Finished: {result.finished}")

        # If game not finished, try another move
        if not result.finished:
            result2 = await session.call_tool("combine_numbers", {
                "index1": 0,
                "index2": 1,
                "operator": "*"
            })
            print(f"\nTurn 2 Result:\n{result2.blocks[0].text}")
            print(f"Reward: {result2.reward}")
            print(f"Finished: {result2.finished}")

    print("\nTest PASSED!")


if __name__ == "__main__":
    asyncio.run(test_locally())
