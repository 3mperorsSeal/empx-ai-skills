// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EmpsealRouter Interface Stub
 * @dev This is a stub interface representing the execution surface of the EmpX router.
 * It is provided for reference to ensure agents and frameworks can construct valid calldata.
 */
interface IEmpsealRouter {
    struct Trade {
        uint256 amountIn;
        uint256 amountOut;
        address[] path;
        address[] adapters;
    }

    /// @notice Returns optimal multi-hop route
    function findBestPath(uint256 amountIn, address tokenIn, address tokenOut, uint8 maxSteps) 
        external view returns (uint256[] memory amounts, address[] memory adapters, address[] memory path);

    /// @notice Returns optimal gas-aware multi-hop route
    function findBestPathWithGas(uint256 amountIn, address tokenIn, address tokenOut, uint8 maxSteps, uint256 gasPrice) 
        external view returns (uint256[] memory amounts, address[] memory adapters, address[] memory path, uint256 gasEstimate);

    /// @notice Single hop query across all adapters
    function queryNoSplit(uint256 amountIn, address tokenIn, address tokenOut) 
        external view returns (address adapter, address tokenIn_, address tokenOut_, uint256 amountOut);

    /// @notice Single hop query for specific adapter
    function queryAdapter(uint256 amountIn, address tokenIn, address tokenOut, uint8 index) 
        external view returns (address adapter, address tokenIn_, address tokenOut_, uint256 amountOut);

    /// @notice Executes a token swap
    function swapNoSplit(Trade calldata trade, address to, uint256 fee) external;

    /// @notice Executes a token swap starting from native token (e.g., PLS on PulseChain)
    function swapNoSplitFromPLS(Trade calldata trade, address to, uint256 fee) external payable;

    /// @notice Executes a token swap ending in native token (e.g., PLS on PulseChain)
    function swapNoSplitToPLS(Trade calldata trade, address to, uint256 fee) external;

    /// @notice Executes a token swap starting from native token (e.g., ETH on Ethereum/Arbitrum/Base)
    function swapNoSplitFromETH(Trade calldata trade, address to, uint256 fee) external payable;

    /// @notice Executes a token swap ending in native token (e.g., ETH on Ethereum/Arbitrum/Base)
    function swapNoSplitToETH(Trade calldata trade, address to, uint256 fee) external;
}
