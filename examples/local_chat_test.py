import os
import json
import logging
from web3 import Web3

# -----------------
# 1. Setup & Config
# -----------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# To run this, you must have `openai` installed and an OPENAI_API_KEY set.
try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    exit(1)

client = OpenAI()

# -----------------
# 2. Web3 Execution
# -----------------
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
    }
]

def load_chain_config(chain_id: int) -> dict:
    """Helper to find the right chain JSON by chain_id inside the chains folder"""
    chains_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chains")
    for filename in os.listdir(chains_dir):
        if filename.endswith(".json"):
            with open(os.path.join(chains_dir, filename), 'r') as f:
                config = json.load(f)
                if config.get("chain_id") == chain_id:
                    return config
    raise ValueError(f"No configuration found for chain_id {chain_id}")

def execute_simulation(chain_id: int, token_in: str, token_out: str, amount_in: str, max_steps: int, gas_price: str) -> str:
    """
    This is the python implementation that runs when the LLM decides to use the `empx_gas_aware_route` tool.
    """
    logger.info(f"\n[Executing Web3 Call] Simulating swap on chain {chain_id} for {amount_in} of {token_in} to {token_out}...")
    
    try:
        config = load_chain_config(chain_id)
        router_address = Web3.to_checksum_address(config["router"])
        
        # In this demo, we mock the RPC connection rather than requiring a live node just to test the LLM. 
        # In a real environment:
        # w3 = Web3(Web3.HTTPProvider(RPC_URL))
        # contract = w3.eth.contract(address=router_address, abi=ROUTER_ABI)
        # offer = contract.functions.findBestPathWithGas(...).call()
        
        # Mocking the response for the sake of the chat interface dry-run
        mock_output = {
            "amounts": [amount_in, str(int(amount_in) * 0.99)], # Simple 1% drop mock
            "adapters": [config["adapters"][0] if config["adapters"] else "0xMockAdapter"],
            "path": [token_in, token_out],
            "gasEstimate": gas_price
        }
        
        logger.info(f"[Web3 Success] -> Found route via {router_address}")
        return json.dumps(mock_output)
        
    except Exception as e:
        logger.error(f"[Web3 Error] -> {e}")
        return json.dumps({"error": str(e)})

# -----------------
# 3. LLM Integration
# -----------------

def load_skill_as_tool(skill_filename: str) -> dict:
    """Reads our JSON skill schema and converts it into OpenAI's required Tool format"""
    skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", skill_filename)
    with open(skill_path, 'r') as f:
        skill = json.load(f)
        
    return {
        "type": "function",
        "function": {
            "name": skill["name"],
            "description": skill["description"],
            "parameters": skill["inputs"]
        }
    }

def chat_loop():
    print("====================================")
    print(" EmpX AI Skills - Local Chat Tester ")
    print("====================================")
    print("Type 'exit' to quit.\n")
    
    # Load our single simulation tool for testing
    tools = [load_skill_as_tool("empx-gas-aware-route.skill.json")]
    
    system_prompt = """You are a blockchain trading assistant. 
    Use the tools provided to simulate swaps when requested.
    If the user does not provide token addresses, just use mock placeholder like '0xTOKENA' and '0xTOKENB'.
    Always summarize the final results of the tool call to the user clearly."""

    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        # Send to LLM
        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo
            messages=messages,
            tools=tools
        )
        
        response_msg = response.choices[0].message
        
        # Did the LLM decide to call a tool?
        if response_msg.tool_calls:
            messages.append(response_msg) # Record the assistant's decision to call a tool
            
            for tool_call in response_msg.tool_calls:
                function_name = tool_call.function.name
                
                if function_name == "empx_gas_aware_route":
                    args = json.loads(tool_call.function.arguments)
                    
                    # Execute our actual Python code mapping to the tool
                    result = execute_simulation(
                        chain_id=args.get("chain_id"),
                        token_in=args.get("token_in"),
                        token_out=args.get("token_out"),
                        amount_in=args.get("amount_in"),
                        max_steps=args.get("max_steps", 4),
                        gas_price=args.get("gas_price", "0")
                    )
                    
                    # Provide the function result back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result
                    })

            # Get the LLM's final natural language response based on the tool output
            final_response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
            )
            assistant_msg = final_response.choices[0].message.content
            print(f"\nAI: {assistant_msg}")
            messages.append({"role": "assistant", "content": assistant_msg})
            
        else:
            # Normal conversational reply
            print(f"\nAI: {response_msg.content}")
            messages.append(response_msg)

if __name__ == "__main__":
    chat_loop()
