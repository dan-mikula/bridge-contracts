from brownie import (
    accounts,
    config,
    network,
    Contract,
    USDC,
    USDC_BRIDGED,
    MainChainBridge,
    SideChainBridge,
)

from web3 import Web3


def show_accounts():
    presenter_1 = accounts.add(config["wallets"]["from_key_presenter_1"])
    presenter_2 = accounts.add(config["wallets"]["from_key_presenter_2"])
    presenter_3 = accounts.add(config["wallets"]["from_key_presenter_3"])
    presenter_4 = accounts.add(config["wallets"]["from_key_presenter_4"])

    print(f"Presenter 1 Owner: {presenter_1}")
    print(f"Presenter 2 Gateway: {presenter_2}")
    print(f"Presenter 3: {presenter_3}")
    print(f"Presenter 4: {presenter_4}")


def deploy_token_main(publish=False):
    owner_account = accounts.add(config["wallets"]["from_key_presenter_1"])
    token = USDC.deploy({"from": owner_account}, publish_source=publish)
    print(f"Token deployed on {network.show_active()} at address {token.address}")


def deploy_token_side(publish=False):
    gateway_account = accounts.add(config["wallets"]["from_key_presenter_2"])
    token = USDC_BRIDGED.deploy({"from": gateway_account}, publish_source=publish)
    print(f"Token deployed on {network.show_active()} at address {token.address}")


def deploy_and_setup_main_bridge(publish=False):

    owner_account = accounts.add(config["wallets"]["from_key_presenter_1"])
    gateway_account = accounts.add(config["wallets"]["from_key_presenter_2"])

    bridge = MainChainBridge.deploy(
        gateway_account.address, {"from": owner_account}, publish_source=publish
    )

    tx = bridge.addToken(USDC[-1].address, {"from": owner_account})
    tx.wait(1)


def main_bridge_addToken():
    owner_account = accounts.add(config["wallets"]["from_key_presenter_1"])

    bridge = Contract.from_abi(
        MainChainBridge._name,
        MainChainBridge[-1].address,
        MainChainBridge.abi,
    )

    bridge.addToken(USDC[-1].address, {"from": owner_account})


def deploy_and_setup_side_bridge_and_deploy_side_token(publish=False):
    print("Deploying start.")
    owner_account = accounts.add(config["wallets"]["from_key_presenter_1"])
    gateway_account = accounts.add(config["wallets"]["from_key_presenter_2"])

    bridge = SideChainBridge.deploy(
        gateway_account.address, {"from": owner_account}, publish_source=publish
    )

    token = USDC_BRIDGED.deploy(
        bridge.address, {"from": owner_account}, publish_source=publish
    )

    tx = bridge.addToken(token.address, {"from": owner_account})
    tx.wait(1)
    print(f"Deployment on {network.show_active()} done.")
    print("-" * 80)
    result_text = f"""
    Bridge Address: {bridge.address}
    Bridge Owner:   {owner_account.address}
    ==========================================================
    Token Address:  {token.address}
    Token Owner:    {owner_account.address}
    """
    print(result_text)
    print("-" * 80)


def mint_token_main():
    owner_account = accounts.add(config["wallets"]["from_key_presenter_1"])
    spender_account = accounts.add(config["wallets"]["from_key_presenter_3"])

    erc20 = Contract.from_abi(USDC._name, USDC[-1].address, USDC.abi)
    erc20.mint(owner_account, 100000 * 10 ** 6, {"from": owner_account})
    erc20.transfer(spender_account.address, 10000 * 10 ** 6, {"from": owner_account})
    print(
        f"{spender_account.address} balance: {erc20.balanceOf(spender_account.address)/10**6} USDC"
    )
    print(
        f"{owner_account.address} balance: {erc20.balanceOf(owner_account.address)/10**6} USDC"
    )


# def transfer_to_main_bridge():
#     spender_account = accounts.add(config["wallets"]["from_key_presenter_3"])

#     amount_to_bridge = 30 * 10**6

#     erc20 = Contract.from_abi(USDC._name, USDC[-1].address, USDC.abi)
#     token_transfer = erc20.transfer(
#         MainChainBridge[-1].address,
#         amount_to_bridge,
#         {"from": spender_account},
#     )
#     token_transfer.wait(1)
#     main_bridge = Contract.from_abi(
#         MainChainBridge._name,
#         MainChainBridge[-1].address,
#         MainChainBridge.abi,
#     )
#     txid = str(token_transfer.txid).replace("0x", "")
#     bridge_transfer = main_bridge.bridgeTokens(
#         spender_account.address,
#         spender_account.address,
#         USDC[-1].address,
#         amount_to_bridge,
#         txid,
#         800001,
#         {
#             "from": spender_account,
#             "gasPrice": Web3.toWei(2, "gwei"),
#             "gasLimit": 1000000,
#         },
#     )
#     bridge_transfer.wait(1)


# def return_token_on_side_chain():
#     spender_account = accounts.add(config["wallets"]["from_key_presenter_3"])

#     amount_to_bridge = 118 * 10**6

#     erc20 = Contract.from_abi(USDC_BRIDGED._name, USDC_BRIDGED[-1], USDC_BRIDGED.abi)

#     token_transfer = erc20.transfer(
#         SideChainBridge[-1].address,
#         amount_to_bridge,
#         {"from": spender_account},
#     )
#     token_transfer.wait(1)
#     print(token_transfer.txid)

#     side_bridge = Contract.from_abi(
#         SideChainBridge._name,
#         SideChainBridge[-1].address,
#         SideChainBridge.abi,
#     )
#     txid = str(token_transfer.txid).replace("0x", "")
#     bridge_transfer = side_bridge.returnTokens(
#         spender_account.address,
#         spender_account.address,
#         USDC_BRIDGED[-1].address,
#         amount_to_bridge,
#         txid,
#         5,
#         {
#             "from": spender_account,
#             "gasPrice": Web3.toWei(10, "gwei"),
#             "gasLimit": 1000000,
#         },
#     )
#     bridge_transfer.wait(1)


def show_info():
    print(f"You are currently on {network.show_active()}")
    show_accounts()
    if network.show_active() == "goerli":
        info = f"""
        USDC Token Address: {USDC[-1].address}
        MainBridge Address: {MainChainBridge[-1].address}
        """
    else:
        info = f"""
        USDC Bridged Token Address: {USDC_BRIDGED[-1].address}
        SideBridge Address: {SideChainBridge[-1].address}
        """

    print(info)


def deploy_on_mainnet():
    print(f"You are currently on {network.show_active()}")
    deploy_token_main()
    deploy_and_setup_main_bridge()
    mint_token_main()
    # main_bridge_addToken() # use if you want to add more than one token
    print("deployment on mainnet done.")


def deploy_on_sidechain():
    print(f"You are currently on {network.show_active()}")
    deploy_and_setup_side_bridge_and_deploy_side_token()


# def interact():
#     print(f"You are currently on {network.show_active()}")
#     if network.show_active() == "goerli":
#         transfer_to_main_bridge()
#     else:
#         return_token_on_side_chain()


def main():
    show_info()

    # interact()

    if network.show_active() == "goerli":
        # deploy contracts on mainnet
        deploy_on_mainnet()

    else:
        # deploy contracts on sidechain
        deploy_on_sidechain()
