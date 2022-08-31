// SPDX-License-Identifier: MIT
// Bridge for main chain - d.m. ph33r!1337
pragma solidity ^0.8.15;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MainChainBridge {
    mapping(address => IERC20) addressToTokensMap;
    address[] private allowedTokens;
    uint256 public FEE;
    bool public feesApply;
    bool public bridgeActive;

    address private gateway;
    address private owner;

    event BridgedTokens(
        address indexed sender,
        address indexed receiver,
        bytes32 indexed mainDepositHash,
        uint256 targetChain,
        uint256 amount,
        uint256 timestamp
    );
    event ReturnedTokens(
        address indexed sender,
        address indexed receiver,
        bytes32 indexed sideDepositHash,
        uint256 sourceChain,
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
            addressToTokensMap[_tokenAddress] = IERC20(_tokenAddress);
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

    function bridgeTokens(
        address _sender,
        address _receiver,
        address _tokenAddress,
        uint256 _bridgedAmount,
        bytes32 _depositHash, // string memory
        uint256 _targetChain
    ) external {
        require(bridgeActive == true, "Bridge not active");
        require(
            _isTokenAllowed(_tokenAddress) == true,
            "ERROR: Token not allowed"
        );
        if (getFeesApply() == true) {
            uint256 bridgedAmount = (_bridgedAmount * (1000 - FEE)) / 1000;
            uint256 fee = _bridgedAmount - bridgedAmount;
            addressToTokensMap[_tokenAddress].transfer(gateway, fee);
        }
        emit BridgedTokens(
            _sender,
            _receiver,
            _depositHash,
            _targetChain,
            _bridgedAmount,
            block.timestamp
        );
    }

    function returnedTokens(
        address _sender,
        address _receiver,
        address _tokenAddress,
        uint256 _bridgedAmount,
        bytes32 _depositHash, // string memory
        uint256 _sourceChain
    ) external onlyGateway {
        addressToTokensMap[_tokenAddress].transfer(_receiver, _bridgedAmount);
        emit ReturnedTokens(
            _sender,
            _receiver,
            _depositHash,
            _sourceChain,
            _bridgedAmount,
            block.timestamp
        );
    }
}
