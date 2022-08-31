from brownie import (
    network,
    accounts,
    config,
    Contract,
    USDC_BRIDGED,
    USDC,
    SideChainBridge,
    MainChainBridge,
)
from web3 import Web3
from hexbytes import HexBytes


def transfer_to_main_bridge():
    spender_account = accounts.add(config["wallets"]["from_key_presenter_3"])

    amount_to_bridge = 30 * 10 ** 6

    erc20 = Contract.from_abi(USDC._name, USDC[-1].address, USDC.abi)
    token_transfer = erc20.transfer(
        MainChainBridge[-1].address,
        amount_to_bridge,
        {"from": spender_account},
    )
    token_transfer.wait(1)
    main_bridge = Contract.from_abi(
        MainChainBridge._name,
        MainChainBridge[-1].address,
        MainChainBridge.abi,
    )
    txid = HexBytes(token_transfer.txid)
    bridge_transfer = main_bridge.bridgeTokens(
        spender_account.address,
        spender_account.address,
        USDC[-1].address,
        amount_to_bridge,
        txid,
        800001,
        {
            "from": spender_account,
            "gasPrice": Web3.toWei(2, "gwei"),
            "gasLimit": 1000000,
        },
    )
    bridge_transfer.wait(1)


def return_token_on_side_chain():
    spender_account = accounts.add(config["wallets"]["from_key_presenter_3"])

    amount_to_bridge = 31.82 * 10 ** 6

    erc20 = Contract.from_abi(USDC_BRIDGED._name, USDC_BRIDGED[-1], USDC_BRIDGED.abi)

    token_transfer = erc20.transfer(
        SideChainBridge[-1].address,
        amount_to_bridge,
        {"from": spender_account},
    )
    token_transfer.wait(1)

    side_bridge = Contract.from_abi(
        SideChainBridge._name,
        SideChainBridge[-1].address,
        SideChainBridge.abi,
    )
    txid = HexBytes(token_transfer.txid)
    bridge_transfer = side_bridge.returnTokens(
        spender_account.address,
        spender_account.address,
        USDC_BRIDGED[-1].address,
        amount_to_bridge,
        txid,
        5,
        {
            "from": spender_account,
            "gasPrice": Web3.toWei(10, "gwei"),
            "gasLimit": 1000000,
        },
    )
    bridge_transfer.wait(1)


def interact():
    print(f"You are currently on {network.show_active()}")
    if network.show_active() == "goerli":
        transfer_to_main_bridge()
    else:
        return_token_on_side_chain()


def main():
    interact()
