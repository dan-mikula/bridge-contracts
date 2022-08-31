from brownie import USDC, USDC_BRIDGED, MainChainBridge, accounts, config, reverts
import pytest


@pytest.fixture(scope="module")
def account():
    return accounts.add(config["wallets"]["from_key_presenter_1"])


@pytest.fixture(scope="module")
def token_main(account):
    return USDC.deploy({"from": account})


@pytest.fixture(scope="module")
def token_side(account):
    return USDC_BRIDGED.deploy(account.address, {"from": account})


@pytest.fixture(scope="module")
def gateway():
    return accounts.add(config["wallets"]["from_key_presenter_2"])


@pytest.fixture(scope="module")
def main_chain_bridge(account, gateway):
    return MainChainBridge.deploy(gateway.address, {"from": account})


def test_mint_usdc(token_main, account):
    token_main.mint(account.address, 100 * 10 ** 6, {"from": account})
    assert token_main.balanceOf(account) == 100 * 10 ** 6


def test_main_chain_add_token_and_return_allowed_tokens(
    account, gateway, token_main, token_side, main_chain_bridge
):
    tx = main_chain_bridge.addToken(token_main.address, {"from": account})
    tx.wait(1)
    assert tx.return_value == True

    tx = main_chain_bridge.addToken(token_side.address, {"from": account})
    tx.wait(1)
    assert tx.return_value == True

    add_token_again = main_chain_bridge.addToken(token_side.address, {"from": account})
    add_token_again.wait(1)
    assert add_token_again.return_value == False

    with reverts("ERROR: Not authorized"):
        tx = main_chain_bridge.addToken(token_side.address, {"from": gateway})
        tx.wait(1)

    tx = main_chain_bridge.getAllowedTokensAddresses()
    assert len(tx) == 2
    assert tx[0] == token_main.address
    assert tx[1] == token_side.address


def test_main_chain_add_token_bridge_wrong_token(
    account, gateway, token_main, token_side, main_chain_bridge
):

    transfer_account = accounts.add()

    tx = token_main.mint(transfer_account.address, 100 * 10 ** 6, {"from": account})

    hashtxid = str(tx.txid).replace("0x", "")

    with reverts("ERROR: Token not allowed"):
        tx = main_chain_bridge.bridgeTokens(
            transfer_account.address,
            transfer_account.address,
            gateway.address,
            100 * 10 ** 6,
            hashtxid,
            42,
            {"from": transfer_account},
        )
        tx.wait(1)


def test_set_and_get_fees(account, gateway, main_chain_bridge):
    # bridge is initialized with fee of 0.3%
    tx = main_chain_bridge.getFee()
    assert tx == 3
    with reverts("ERROR: Not authorized"):
        main_chain_bridge.setFee(5, {"from": gateway})  # set fee to 0.5%
    main_chain_bridge.setFee(5, {"from": account})
    tx = main_chain_bridge.getFee()
    print(tx)
    assert tx == 5
    # set back to 0.3
    main_chain_bridge.setFee(3, {"from": account})


def test_set_and_get_fees_apply(account, gateway, main_chain_bridge):
    # bridge gets initialize with fees apply
    tx = main_chain_bridge.getFeesApply()
    print(f"fees apply: {tx}")
    assert tx == True

    with reverts("ERROR: Not authorized"):
        main_chain_bridge.setFeesApply(False, {"from": gateway})

    main_chain_bridge.setFeesApply(False, {"from": account})

    tx = main_chain_bridge.getFeesApply()
    assert tx == False
    # set back to True
    main_chain_bridge.setFeesApply(True, {"from": account})


def test_set_and_get_bridge_active(account, gateway, main_chain_bridge):
    # bridge gets initialized as active
    tx = main_chain_bridge.getBridgeActive()
    assert tx == True

    with reverts("ERROR: Not authorized"):
        main_chain_bridge.setBridgeActive(False, {"from": gateway})

    main_chain_bridge.setBridgeActive(False, {"from": account})

    tx = main_chain_bridge.getBridgeActive()
    assert tx == False
    # set back to true
    tx = main_chain_bridge.setBridgeActive(True, {"from": account})
    tx.wait(1)
    tx = main_chain_bridge.getBridgeActive()
    assert tx == True


def test_bridge_tokens_fees(account, gateway, main_chain_bridge, token_main):
    transfer_account = accounts.add()

    token_main.mint(transfer_account.address, 1000 * 10 ** 6, {"from": account})

    assert token_main.balanceOf(transfer_account.address) == 1000 * 10 ** 6

    token_transfer = token_main.transfer(
        main_chain_bridge.address, 1000 * 10 ** 6, {"from": transfer_account}
    )
    token_transfer.wait(1)

    assert token_main.balanceOf(transfer_account.address) == 0

    hashtxid = str(token_transfer.txid).replace("0x", "")

    bridge_transfer = main_chain_bridge.bridgeTokens(
        transfer_account.address,
        transfer_account.address,
        token_main.address,
        1000 * 10 ** 6,
        hashtxid,
        42,
        {"from": transfer_account},
    )
    bridge_transfer.wait(1)

    print(main_chain_bridge.address)
    print(transfer_account.address)
    print(bridge_transfer.events)

    FEE = main_chain_bridge.getFee() / 10
    fee_paid = (1000 * 10 ** 6 * FEE) / 100
    bridged_amount = 1000 * 10 ** 6 - fee_paid

    print(f"bridged amount: {token_main.balanceOf(main_chain_bridge.address)/10**6}")
    print(f"fee paid: {token_main.balanceOf(gateway.address)/10**6}")

    assert token_main.balanceOf(main_chain_bridge.address) == bridged_amount
    assert token_main.balanceOf(gateway.address) == fee_paid


def test_bridge_tokens_without_fees(main_chain_bridge, account, token_main, gateway):
    main_chain_bridge.setFeesApply(False, {"from": account})

    get_fees_apply_tx = main_chain_bridge.getFeesApply()
    assert get_fees_apply_tx == False

    transfer_account = accounts.add()
    token_main.mint(transfer_account.address, 1000 * 10 ** 6, {"from": account})

    token_transfer = token_main.transfer(
        main_chain_bridge.address, 1000 * 10 ** 6, {"from": transfer_account}
    )
    token_transfer.wait(1)

    hashtxid = str(token_transfer.txid).replace("0x", "")

    bridge_transfer = main_chain_bridge.bridgeTokens(
        transfer_account.address,
        transfer_account.address,
        token_main.address,
        1000 * 10 ** 6,
        hashtxid,
        42,
        {"from": transfer_account},
    )
    bridge_transfer.wait(1)

    if get_fees_apply_tx == True:
        FEE = main_chain_bridge.getFee() / 10
    elif get_fees_apply_tx == False:
        FEE = 0
    fee_paid = (1000 * 10 ** 6 * FEE) / 100
    bridged_amount = 1000 * 10 ** 6 - fee_paid

    print(f"bridged amount: {token_main.balanceOf(main_chain_bridge.address)/10**6}")
    print(f"fee paid: {token_main.balanceOf(gateway.address)/10**6}")

    assert 1000 * 10 ** 6 == bridged_amount
    assert 0 == fee_paid
