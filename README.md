# EmpX AI Skills

EmpX AI Skills is a machine-readable repository that exposes the **EmpsealRouter** — an on-chain multi-adapter DEX aggregator — as callable infrastructure for AI agents, LLM tool-use frameworks, and autonomous trading systems.

EmpX is a decentralized, on-chain liquidity router optimized for AI agents. This repository provides machine-readable skill definitions, schemas, and examples enabling AI systems to discover, simulate, and execute token swaps across EVM-compatible blockchains.

Primary use cases:

- Autonomous trading agents
- AI-driven portfolio rebalancing
- Cross-chain liquidity routing
- Gas-aware execution optimization

**Keywords:** AI agents, on-chain execution, autonomous trading, DEX aggregation, router contract, machine-readable skills

## Features: Let AIs Safely Trade
This infrastructure is designed specifically to ensure AI agents do not execute non-deterministic or revert-prone transactions during autonomous trading:
- **Simulatable**: `findBestPath` and `findBestPathWithGas` are pure `view` functions. AIs can dry-run swaps with zero state mutation and zero gas costs via RPC.
- **Deterministic**: Given the same inputs and blockchain state, the route and output are perfectly replicable. 
- **Gas-Aware**: The `findBestPathWithGas` simulation natively factors in the current gas cost (denominated in the output token) to ensure multi-hop routes are strictly profitable.
- **Slippage-Controlled**: Agents can set their minimum expected `amountOut` safely. Transactions will revert cleanly (`"Insufficient output amount"`) if the market shifts unfavorably during block confirmation.

## Repository Structure
- `ai-plugin.json` & `openapi.yaml`: Auto-discoverable specifications for OpenAI / Claude / AutoGPT crawlers and tool ingestors.
- `skills/`: Individual machine-readable JSON skill capabilities (`empx-swap`, `empx-best-path`, `empx-gas-aware-route`).
- `chains/`: Per-chain JSON configs mapping the correct router logic and adapters across blockchains (PulseChain, Base, Sonic, Sei, etc).
- `examples/`: Copy-and-paste boilerplate codebase setups for Python and TypeScript agents, plus LLM prompt patterns.
- `schemas/`: Standardized JSON Schemas to validate agent `Trade` and `Query` struct payloads before on-chain submission.
- `contracts/`: Reference Solidity interface for the `EmpsealRouter`.

## Usage for AI Agents

**Target Workflow:**
1. Agent ingests `skills/` and `chains/` config for discovering target networks.
2. Agent reads target token allocations and decides it needs to swap Token A to Token B.
3. Agent uses the `empx_gas_aware_route` (or standard `empx_best_path`) simulation tool.
4. Agent evaluates output vs gas estimations from the simulation.
5. If profitable, agent passes the exact `adapters` and `path` array returned from the simulation directly to the `empx_execute_swap` tool, enforcing at minimum a 0.5% slippage buffer.

See `examples/prompt_examples.md` for proper in-context LLM instructions.
