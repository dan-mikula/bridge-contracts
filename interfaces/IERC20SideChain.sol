// SPDX-License-Identifier: MIT
// test token - d.m. ph33r!1337
pragma solidity ^0.8.15;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IERC20SideChain is IERC20 {
    function mint(address recipient, uint256 amount) external;

    function burn(uint256 amount) external;

    function burnFrom(address account, uint256 amount) external;

    function returnBridge() external;
}
