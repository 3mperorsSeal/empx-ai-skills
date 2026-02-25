# Prompt Examples for EmpX AI Agents

When interacting with an LLM tool integration, provide these context instructions to ensure deterministic and safe utilization of the EmpX skills.

## Core Directives

Include this in the system prompt for your AI Agent:
```text
You are an autonomous trading agent equipped with the EmpX Router skills. 
RULES:
1. NEVER execute `empx_execute_swap` without first calling `empx_best_path` or `empx_gas_aware_route`.
2. ALWAYS verify that the `amountOut` returned by the simulation meets the user's minimum expected threshold before executing.
3. If no route is found (empty path array), you must ABORT the transaction and inform the user.
4. Always apply at least a 0.5% slippage tolerance to the simulated output when constructing the Trade parameter.
5. IF the trade involves the chain's native token (like ETH or PLS), you MUST read the `native_swap_from_func` or `native_swap_to_func` defined in the chain's JSON mapping and invoke that specific function signature. Do not default to `swapNoSplitFromETH` unless it is explicitly defined in the chain file.
```

## Natural Language Scenario 1: Basic Swap

**User Query:**
> "I want to swap 100 WETH into USDC on Arbitrum. Find me the best route and execute it."

**Agent Reasoning Loop:**
1. **Tool Check:** Agent checks `chain_ids` and loads `chains/arbitrum.json` to get token addresses.
2. **Simulation:** Agent calls `empx_gas_aware_route` with `chain_id: 42161, token_in: WETH_ADDR, token_out: USDC_ADDR, amount_in: 1000000000...`.
3. **Execution Validation:** Agent evaluates the `FormattedOffer`. The output is ~300,000 USDC.
4. **Execution:** Agent passes the `path` and `adapters` array exactly as received from the simulation into `empx_execute_swap`, setting `amount_out` to 298,500 USDC (0.5% slippage adjustment).

## Natural Language Scenario 2: Gas-Aware Skipping

**User Query:**
> "Rebalance my portfolio by swapping $50 worth of PEPE into ETH on Ethereum Mainnet."

**Agent Reasoning Loop:**
1. **Simulation:** Agent calls `empx_gas_aware_route` with the Ethereum Mainnet `chain_id` and the current gas price. 
2. **Analysis:** The `gasEstimate` parameter reveals the transaction will cost $60 in gas. Since the gas cost is higher than the trade size, the agent logically determines the trade is unprofitable.
3. **Action:** Agent skips execution and replies: "I found a route, but the gas fees ($60) exceed the trade size ($50). Skipping swap."
