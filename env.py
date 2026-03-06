import textarena as ta
from typing import List
from pydantic import BaseModel, field_validator
from openreward.environments import Environment, JSONObject, ToolOutput, TextBlock, tool


class TaskSpec(BaseModel):
    id: str
    env_id: str
    seed: int
    variant: str = ""


class CombineNumbersParams(BaseModel, extra="forbid"):
    index1: int
    index2: int
    operator: str

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v):
        v = v.strip()
        if v not in ("+", "-", "*", "/"):
            raise ValueError("operator must be one of: +, -, *, /")
        return v


class CountdownEnvironment(Environment):
    GAME_NAME = "Countdown"
    VARIANTS = ["Countdown-v0", "Countdown-v0-train", "Countdown-v0-raw"]
    NUM_TASKS_PER_VARIANT = 50

    def __init__(self, task_spec: JSONObject, secrets: dict[str, str] = {}) -> None:
        super().__init__(task_spec)
        self.config = TaskSpec.model_validate(task_spec)
        self.ta_env = ta.make(env_id=self.config.env_id)
        self.game_done = False
        self.turn_count = 0

    @classmethod
    def list_splits(cls) -> list[str]:
        return ["train", "test"]

    @classmethod
    def list_tasks(cls, split: str) -> list[JSONObject]:
        tasks = []
        for variant_id in cls.VARIANTS:
            for seed_idx in range(cls.NUM_TASKS_PER_VARIANT):
                seed = seed_idx if split == "train" else seed_idx + 10000
                tasks.append({
                    "id": f"{variant_id}_seed{seed}",
                    "env_id": variant_id,
                    "seed": seed,
                    "variant": variant_id
                })
        return tasks

    def _map_reward(self, raw: float) -> float:
        """Map raw reward from [-1, 1] to [0, 1]"""
        return max(0.0, min(1.0, (raw + 1.0) / 2.0))

    async def get_prompt(self) -> List[TextBlock]:
        self.ta_env.reset(num_players=1, seed=self.config.seed)
        _, obs = self.ta_env.get_observation()
        obs_text = obs if isinstance(obs, str) else str(obs)

        prompt = f"""You are playing Countdown Numbers.

{obs_text}

Use the combine_numbers tool to combine two numbers from the available list.
Provide 0-based indices of two numbers and an operator (+, -, *, /).
The result replaces both numbers in the list. Reach the target number!"""

        return [TextBlock(text=prompt)]

    @tool
    async def combine_numbers(self, params: CombineNumbersParams) -> ToolOutput:
        """Combine two numbers from the available list using an arithmetic operator. Provide 0-based indices and operator (+, -, *, /). The result replaces both numbers."""
        if self.game_done:
            return ToolOutput(
                blocks=[TextBlock(text="Game is already over.")],
                metadata={"error": "game_finished"},
                reward=0.0,
                finished=True
            )

        action = f"[{params.index1} {params.index2} {params.operator}]"
        done, info = self.ta_env.step(action=action)
        self.turn_count += 1

        if done:
            self.game_done = True
            rewards, game_info = self.ta_env.close()

            # Extract reward for player 0
            raw = rewards.get(0, 0.0) if isinstance(rewards, dict) else float(rewards)
            reward = self._map_reward(raw)

            # Extract reason from game_info
            reason = ""
            if isinstance(game_info, dict) and 0 in game_info:
                reason = game_info[0].get("reason", "")

            summary = f"Game Over! Reward: {reward:.2f}"
            if reason:
                summary += f"\n{reason}"

            return ToolOutput(
                blocks=[TextBlock(text=summary)],
                metadata={"turn": self.turn_count, "reward": reward},
                reward=reward,
                finished=True
            )

        # Game continues
        _, obs = self.ta_env.get_observation()
        obs_text = obs if isinstance(obs, str) else str(obs)

        return ToolOutput(
            blocks=[TextBlock(text=obs_text)],
            metadata={"turn": self.turn_count},
            reward=0.0,
            finished=False
        )
