"""
Example Python AI Agent script using EmpX AI Skills.
Demonstrates how an agent simulates a trade and executes it via the EmpX Router.
"""
import os
import json
import logging
from web3 import Web3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Basic ABI for demonstration based on EmpX OpenAPI semantics
ROUTER_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "maxSteps", "type": "uint8"},
            {"name": "gasPrice", "type": "uint256"}
        ],
        "name": "findBestPathWithGas",
        "outputs": [
            {
                "components": [
                    {"name": "amounts", "type": "uint256[]"},
                    {"name": "adapters", "type": "address[]"},
                    {"name": "path", "type": "address[]"},
                    {"name": "gasEstimate", "type": "uint256"}
                ],
                "name": "FormattedOffer",
                "type": "tuple"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {
                "components": [
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOut", "type": "uint256"},
                    {"name": "path", "type": "address[]"},
                    {"name": "adapters", "type": "address[]"}
                ],
                "name": "trade",
                "type": "tuple"
            },
            {"name": "to", "type": "address"},
            {"name": "fee", "type": "uint256"}
        ],
        "name": "swapNoSplit",
        "outputs": [],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def load_chain_config(chain_file_path: str) -> dict:
    with open(chain_file_path, 'r') as f:
        return json.load(f)

def run_agent(chain_config_path: str, rpc_url: str, private_key: str):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        logger.error("Failed to connect to RPC node.")
        return

    account = w3.eth.account.from_key(private_key)
    logger.info(f"Agent account initialized: {account.address}")

    config = load_chain_config(chain_config_path)
    router_address = Web3.to_checksum_address(config["router"])
    router_contract = w3.eth.contract(address=router_address, abi=ROUTER_ABI)

    # Example: Simulating a swap from WPLS to an arbitrary token
    token_in = Web3.to_checksum_address(config["wrapped_native"])
    token_out = Web3.to_checksum_address("0x1111111111111111111111111111111111111111") # Placeholder target
    amount_in = w3.to_wei(100, 'ether')
    max_steps = 4
    gas_price = w3.eth.gas_price

    logger.info("Simulating multi-hop route with gas awareness...")
    
    # 1. Simulation Phase (Read-Only)
    try:
        offer = router_contract.functions.findBestPathWithGas(
            amount_in, token_in, token_out, max_steps, gas_price
        ).call()
        
        amounts, adapters, path, gas_estimate = offer
        
        if len(path) < 2 or amounts[-1] == 0:
            logger.warning("No profitable path found. Aborting execution.")
            return
            
        logger.info(f"Optimal path found via adapters: {adapters}")
        logger.info(f"Estimated output: {amounts[-1]}")
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return

    # 2. Execution Phase
    # Constructing trade object dynamically based on simulation
    trade = {
        "amountIn": amount_in,
        "amountOut": int(amounts[-1] * 0.995), # 0.5% Slippage tolerance
        "path": path,
        "adapters": adapters
    }
    
    logger.info("Proceeding to execution with Trade parameter.")
    
    # Normally we would build transaction and send here:
    # tx = router_contract.functions.swapNoSplit(trade, account.address, 0).build_transaction(...)
    logger.info(f"[Dry Run] Transaction would submit Trade struct: {json.dumps(trade, indent=2)}")

if __name__ == "__main__":
    import sys
    # For demonstration: pass path to config, RPC, and dummy private key
    _chain_config = sys.argv[1] if len(sys.argv) > 1 else "../chains/pulsechain.json"
    _rpc = os.getenv("RPC_URL", "https://rpc.pulsechain.com")
    _pk = os.getenv("PRIVATE_KEY", "0x" + "0" * 64) # Do not use explicitly in prod
    
    # This is a stub dry-run
    # run_agent(_chain_config, _rpc, _pk)
    logger.info("Agent script initialized in dry-run mode.")
