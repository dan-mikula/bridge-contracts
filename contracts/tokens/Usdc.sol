// SPDX-License-Identifier: MIT
// test token - d.m. ph33r!1337
pragma solidity ^0.8.15;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract USDC is ERC20, ERC20Burnable, Ownable {
    constructor() ERC20("USD Coin - Mock", "USDC") {}

    function decimals() public view override returns (uint8) {
        return 6;
    }

    function mint(address _receiver, uint256 _amount) public onlyOwner {
        require(_amount > 0, "Please provide an amount that is bigger than 0");
        _mint(_receiver, _amount);
    }

    function burnFrom(address account, uint256 amount)
        public
        virtual
        override(ERC20Burnable)
        onlyOwner
    {
        super.burnFrom(account, amount);
    }

    function burn(uint256 _amount)
        public
        virtual
        override(ERC20Burnable)
        onlyOwner
    {
        require(_amount > 0, "Please provide an amount that is bigger than 0");
        super.burn(_amount);
    }
}
