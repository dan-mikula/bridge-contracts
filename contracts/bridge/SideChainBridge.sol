// SPDX-License-Identifier: MIT
// Bridge for side chain - d.m. ph33r!1337
pragma solidity ^0.8.15;

import {IERC20SideChain} from "../../interfaces/IERC20SideChain.sol";

contract SideChainBridge {
    mapping(address => IERC20SideChain) addressToTokensMap;
    address[] private allowedTokens;
    uint256 public FEE;
    bool public feesApply;
    bool public bridgeActive;

    address gateway;
    address owner;

    event BridgedTokens(
        address indexed sender,
        address indexed receiver,
        string mainDepositHash,
        uint256 sourceChain,
        uint256 amount,
        uint256 timestamp
    );
    event ReturnedTokens(
        address indexed sender,
        address indexed receiver,
        string sideDepositHash,
        uint256 targetChain,
        uint256 amount,
        uint256 timestamp
    );

    modifier onlyGateway() {
        require(msg.sender == gateway, "ERROR: Not authorized");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "ERROR: Not authorized");
        _;
    }

    constructor(address _gateway) {
        gateway = _gateway;
        owner = msg.sender;
        feesApply = true;
        FEE = 3;
        bridgeActive = true;
    }

    /* Administrative tasks START */

    function addToken(address _tokenAddress) public onlyOwner returns (bool) {
        bool _add = true;
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _tokenAddress) {
                _add = false;
            }
        }
        if (_add == true) {
            allowedTokens.push(_tokenAddress);
            addressToTokensMap[_tokenAddress] = IERC20SideChain(_tokenAddress);
        }
        return _add;
    }

    function getAllowedTokensAddresses()
        public
        view
        returns (address[] memory)
    {
        return allowedTokens;
    }

    function _isTokenAllowed(address _tokenAddress) private returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _tokenAddress) {
                return true;
            }
        }
        return false;
    }

    function setFee(uint256 _fee) public onlyOwner {
        FEE = _fee;
    }

    function getFee() public view returns (uint256) {
        return FEE;
    }

    function setFeesApply(bool _feesApply) public onlyOwner {
        feesApply = _feesApply;
    }

    function getFeesApply() public view returns (bool) {
        return feesApply;
    }

    function setBridgeActive(bool _bridgeActive) public onlyOwner {
        bridgeActive = _bridgeActive;
    }

    function getBridgeActive() public view returns (bool) {
        return bridgeActive;
    }

    /* Administrative tasks END */

    function returnTokens(
        address _sender,
        address _receiver,
        address _tokenAddress,
        uint256 _returnedAmount,
        string memory _depositHash,
        uint256 _targetChain
    ) external {
        require(bridgeActive == true, "Bridge not active");
        require(
            _isTokenAllowed(_tokenAddress) == true,
            "ERROR: Token not allowed"
        );
        if (getFeesApply() == true) {
            uint256 returnedAmount = (_returnedAmount * (1000 - FEE)) / 1000;
            uint256 fee = _returnedAmount - returnedAmount;
            addressToTokensMap[_tokenAddress].transfer(gateway, fee);
            addressToTokensMap[_tokenAddress].burn(returnedAmount);
        } else {
            addressToTokensMap[_tokenAddress].burn(_returnedAmount);
        }
        emit ReturnedTokens(
            _sender,
            _receiver,
            _depositHash,
            _targetChain,
            _returnedAmount,
            block.timestamp
        );
    }

    function bridgedTokens(
        address _sender,
        address _receiver,
        address _tokenAddress,
        uint256 _amount,
        string memory _depositHash,
        uint256 _sourceChain
    ) external onlyGateway returns (address) {
        require(
            _isTokenAllowed(_tokenAddress) == true,
            "ERROR: Token not allowed."
        );
        addressToTokensMap[_tokenAddress].mint(_receiver, _amount);
        emit BridgedTokens(
            _sender,
            _receiver,
            _depositHash,
            _sourceChain,
            _amount,
            block.timestamp
        );
    }
}
