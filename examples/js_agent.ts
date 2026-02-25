/**
 * Example TypeScript AI Agent script using EmpX AI Skills.
 * Demonstrates querying the best path and securely constructing a transaction.
 */
import { createPublicClient, createWalletClient, http, encodeFunctionData, parseAbi } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet } from 'viem/chains'; // Swap with appropriate chain

const ROUTER_ABI = parseAbi([
    'function findBestPathWithGas(uint256 amountIn, address tokenIn, address tokenOut, uint8 maxSteps, uint256 gasPrice) view returns (uint256[] amounts, address[] adapters, address[] path, uint256 gasEstimate)',
    'function swapNoSplit((uint256 amountIn, uint256 amountOut, address[] path, address[] adapters) trade, address to, uint256 fee)'
]);

async function runAgent() {
    const privateKey = process.env.PRIVATE_KEY as `0x${string}`;
    const account = privateKeyToAccount(privateKey);

    const publicClient = createPublicClient({
        chain: mainnet, // Placeholder
        transport: http()
    });

    const walletClient = createWalletClient({
        account,
        chain: mainnet,
        transport: http()
    });

    const routerAddress = '0x0000000000000000000000000000000000000000'; // Define router
    const tokenIn = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'; // WETH example
    const tokenOut = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eb48'; // USDC example
    const amountIn = 1000000000000000000n; // 1 WETH

    console.log(`[Agent] Initiating swap sequence for ${account.address}`);

    try {
        const gasPrice = await publicClient.getGasPrice();

        console.log(`[Agent] Step 1: Simulating read-only EmpX path mapping...`);
        const [amounts, adapters, path, gasEstimate] = await publicClient.readContract({
            address: routerAddress,
            abi: ROUTER_ABI,
            functionName: 'findBestPathWithGas',
            args: [amountIn, tokenIn, tokenOut, 4, gasPrice]
        });

        if (adapters.length === 0) {
            console.log(`[Agent] No valid paths found. Exiting.`);
            return;
        }

        const estimatedOutput = amounts[amounts.length - 1];
        const minimumOutput = (estimatedOutput * 995n) / 1000n; // 0.5% buffer

        const tradeStruct = {
            amountIn,
            amountOut: minimumOutput,
            path: [...path],
            adapters: [...adapters]
        };

        console.log(`[Agent] Step 2: Preparing transaction data...`);
        const data = encodeFunctionData({
            abi: ROUTER_ABI,
            functionName: 'swapNoSplit',
            args: [tradeStruct, account.address, 0n]
        });

        // In a real execution, the agent would submit this transaction:
        // const hash = await walletClient.sendTransaction({ to: routerAddress, data });
        console.log(`[Agent] Transaction simulated. Encoded payload: ${data.substring(0, 50)}...`);

    } catch (error) {
        console.error(`[Agent] Failure during operation:`, error);
    }
}

// runAgent().catch(console.error);
console.log("TS Agent example loaded.");
