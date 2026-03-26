# Countdown
[![OpenReward Environment](https://img.shields.io/badge/%E2%AD%90%20OpenReward-Environment-f7e6cc)](https://openreward.ai/GeneralReasoning/Countdown)
## Description
**Countdown** is an ORS environment for evaluating agents on the Countdown Numbers game, where agents must reach a target number by combining available numbers with arithmetic operations. The task was originally introduced in [Stream of Search (SoS)](https://arxiv.org/abs/2404.03683) as a domain for learning to search in language. This environment wraps the Countdown implementation from [TextArena](https://github.com/LeonGuertler/TextArena), a framework for text-based game environments.
## Capabilities
- Mathematical reasoning and arithmetic operations
- Search and planning in combinatorial spaces
- Goal-directed problem solving
## Compute Requirements
Countdown does not require a sandbox. It has minimal compute requirements.
## License
[MIT](https://github.com/LeonGuertler/TextArena/blob/main/LICENSE).
## Tasks
There are two splits: train (150 tasks) and test (150 tasks). Each split contains 50 tasks across each of 3 variants:
- **Countdown-v0**: Standard countdown with formatted feedback
- **Countdown-v0-train**: Training variant with additional guidance
- **Countdown-v0-raw**: Raw feedback without formatting
Each task is seeded for reproducibility.
## Reward Structure
This is a sparse reward environment. Rewards are mapped from TextArena's native range of {-1, 0, 1} to {0.0, 0.5, 1.0} via `(raw + 1) / 2`.
We do not use LLM graders for this environment; reward is determined programmatically.
## Data
Game state is generated procedurally by the TextArena engine using seeded randomness. No external data files are required.
## Tools
Agents are given a single tool:
- `combine_numbers(index1, index2, operator)`: Combine two numbers from the available list using an arithmetic operator. Provide 0-based indices and operator (+, -, *, /). The result replaces both numbers.
## Time Horizon
Countdown is a multi-turn environment.
## Environment Difficulty
Medium. The game requires strategic planning to reach the target number, with varying difficulty based on the numbers available and the target value.
## Other Environment Requirements
There are no further environment requirements; Countdown works out of the box without any secrets or API keys.
## Safety
Agents in Countdown interact only with an arithmetic puzzle game and have no access to external systems, the internet, or sensitive data. The environment does not present safety risks.
## Citations
```bibtex
@article{gandhi2024stream,
  title={Stream of search (sos): Learning to search in language},
  author={Gandhi, Kanishk and Lee, Denise and Grand, Gabriel and Liu, Muxin and Cheng, Winson and Sharma, Archit and Goodman, Noah D},
  journal={arXiv preprint arXiv:2404.03683},
  year={2024}
}

@software{textarena2024,
  author    = {Guertler, Leon and Banting, Wilfried and Pignatelli, Eduardo},
  title     = {TextArena},
  year      = {2024},
  publisher = {GitHub},
  url       = {https://github.com/LeonGuertler/TextArena}
}
```
