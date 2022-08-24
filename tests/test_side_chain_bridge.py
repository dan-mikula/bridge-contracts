from brownie import USDC, USDC_BRIDGED, SideChainBridge, accounts, config, reverts
import pytest

AMOUNT = 1000 * 10 ** 6


@pytest.fixture(scope="module")
def account():
    return accounts.add(config["wallets"]["from_key"])


@pytest.fixture(scope="module")
def gateway():
    return accounts.add(config["wallets"]["from_key_2"])


@pytest.fixture(scope="module")
def token_main(account):
    return USDC.deploy({"from": account})


@pytest.fixture(scope="module")
def side_chain_bridge(account, gateway):
    return SideChainBridge.deploy(gateway.address, {"from": account})


@pytest.fixture(scope="module")
def token_side(side_chain_bridge, gateway):
    return USDC_BRIDGED.deploy(side_chain_bridge.address, {"from": gateway})


def test_side_chain_add_token_and_return_allowed_tokens(
    account, gateway, token_main, token_side, side_chain_bridge
):
    tx = side_chain_bridge.addToken(token_main.address, {"from": account})
    tx.wait(1)
    assert tx.return_value == True

    tx = side_chain_bridge.addToken(token_side.address, {"from": account})
    tx.wait(1)
    assert tx.return_value == True

    add_token_again = side_chain_bridge.addToken(token_side.address, {"from": account})
    add_token_again.wait(1)
    assert add_token_again.return_value == False

    with reverts("ERROR: Not authorized"):
        tx = side_chain_bridge.addToken(token_side.address, {"from": gateway})
        tx.wait(1)

    tx = side_chain_bridge.getAllowedTokensAddresses()
    assert len(tx) == 2
    assert tx[0] == token_main.address
    assert tx[1] == token_side.address


def test_side_chain_add_token_bridge_wrong_token(
    account, gateway, token_main, token_side, side_chain_bridge
):
    transfer_account = accounts.add()

    tx = token_side.mint(
        transfer_account.address, AMOUNT, {"from": side_chain_bridge.address}
    )

    hashtxid = str(tx.txid).replace("0x", "")

    with reverts("ERROR: Token not allowed"):
        tx = side_chain_bridge.returnTokens(
            transfer_account.address,
            transfer_account.address,
            gateway.address,
            AMOUNT,
            hashtxid,
            42,
            {"from": transfer_account},
        )
        tx.wait(1)


def test_set_and_get_fees(account, gateway, side_chain_bridge):
    # bridge initialized with fees apply
    tx = side_chain_bridge.getFeesApply()
    assert tx == True

    with reverts("ERROR: Not authorized"):
        side_chain_bridge.setFeesApply(False, {"from": gateway})

    side_chain_bridge.setFeesApply(False, {"from": account})

    assert side_chain_bridge.getFeesApply() == False

    side_chain_bridge.setFeesApply(True, {"from": account})


def test_set_and_get_fees_apply(account, gateway, side_chain_bridge):
    assert side_chain_bridge.getFeesApply() == True

    with reverts("ERROR: Not authorized"):
        side_chain_bridge.setFeesApply(False, {"from": gateway})

    side_chain_bridge.setFeesApply(False, {"from": account})

    assert side_chain_bridge.getFeesApply() == False

    side_chain_bridge.setFeesApply(True, {"from": account})


def test_set_and_get_bridge_active(account, gateway, side_chain_bridge):
    # bridge gets initialized as active
    assert side_chain_bridge.getBridgeActive() == True

    with reverts("ERROR: Not authorized"):
        side_chain_bridge.setBridgeActive(False, {"from": gateway})

    side_chain_bridge.setBridgeActive(False, {"from": account})

    assert side_chain_bridge.getBridgeActive() == False

    side_chain_bridge.setBridgeActive(True, {"from": account})
    assert side_chain_bridge.getBridgeActive() == True


def test_bridge_tokens_fees(account, gateway, side_chain_bridge, token_side):
    transfer_account = accounts.add()

    hashtxid = str(token_side.address).replace("0x", "")

    token_mint_tx = side_chain_bridge.bridgedTokens(
        transfer_account.address,
        transfer_account.address,
        token_side.address,
        AMOUNT,
        hashtxid,
        42,
        {"from": gateway},
    )

    token_mint_tx.wait(1)

    assert token_side.balanceOf(transfer_account.address) == AMOUNT

    token_transfer = token_side.transfer(
        side_chain_bridge.address, AMOUNT, {"from": transfer_account}
    )
    token_transfer.wait(1)

    assert token_side.balanceOf(side_chain_bridge.address) == AMOUNT
    assert token_side.balanceOf(transfer_account.address) == 0

    bridge_transfer = side_chain_bridge.returnTokens(
        transfer_account.address,
        transfer_account.address,
        token_side.address,
        AMOUNT,
        hashtxid,
        42,
        {"from": transfer_account},
    )
    bridge_transfer.wait(1)

    FEE = side_chain_bridge.getFee() / 10
    fee_paid = (AMOUNT * FEE) / 100
    bridged_amount = AMOUNT - fee_paid

    print(f"bridged amount: {bridged_amount/10**6}")
    print(f"fee paid: {fee_paid/10**6}")

    assert token_side.balanceOf(side_chain_bridge.address) == 0
    assert token_side.balanceOf(gateway.address) == fee_paid
    print(bridge_transfer.events)
