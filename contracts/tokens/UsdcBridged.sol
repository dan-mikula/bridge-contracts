// SPDX-License-Identifier: MIT
// test token - d.m. ph33r!1337
pragma solidity ^0.8.15;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

contract USDC_BRIDGED is ERC20, ERC20Burnable {
    address bridge;
    address owner;

    modifier onlyBridge() {
        require(bridge == msg.sender, "ERROR: Not allowed");
        _;
    }

    modifier onlyOwner() {
        require(owner == msg.sender, "ERROR: Not allowed");
        _;
    }

    constructor(address _bridge) ERC20("USD Coin Mock - Bridged", "USDC_B") {
        bridge = _bridge;
        owner = msg.sender;
    }

    function decimals() public view override returns (uint8) {
        return 6;
    }

    function mint(address _receiver, uint256 _amount)
        public
        virtual
        onlyBridge
    {
        _mint(_receiver, _amount);
    }

    function burnFrom(address _account, uint256 _amount)
        public
        virtual
        override(ERC20Burnable)
        onlyBridge
    {
        super.burnFrom(_account, _amount);
    }

    function burn(uint256 _amount)
        public
        virtual
        override(ERC20Burnable)
        onlyBridge
    {
        super.burn(_amount);
    }
}
