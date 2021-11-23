from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import network, interface, config
from web3 import Web3

AMOUNT = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    weth = interface.IWeth(erc20_address)

    # Get WETH if we do not have some
    if network.show_active() in ["mainnet-fork"]:
        get_weth(0.1)
    elif weth.balanceOf(account) < AMOUNT:
        get_weth(0.1)

    lendingPool = get_lending_pool()

    # Approve sending out ERC20 tokens
    approve_erc20(AMOUNT, lendingPool.address, erc20_address, account)

    # Deposite ETH
    print("Depositing . . .")
    tx = lendingPool.deposit(erc20_address, AMOUNT,
                             account.address, 0, {"from": account})
    tx.wait(1)
    print("Successfully deposited !")

    # Borrow DAI
    borrowable_eth, total_debt_eth = get_borrowable_data(lendingPool, account)
    print("Let's Borrow some DAI")
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"])
    # Borrow for half the borrowable_eth
    to_borrow_dai = borrowable_eth / 2 / dai_eth_price
    print(
        f"Will now borrow {to_borrow_dai}DAI -> {borrowable_eth/2}ETH worth of DAI")
    to_borrow_dai_wei = Web3.toWei(to_borrow_dai, "ether")
    dai_address = config["networks"][network.show_active()]["dai_address"]
    print("---------------------------")
    print("---------------------------")
    print("Now borrowing some DAI. . .")
    borrow_tx = lendingPool.borrow(
        dai_address,        # Address of token to borrow
        to_borrow_dai_wei,  # Amount to borrow
        2,                  # rate Mode 1 for fixed, 2 for variable
        0,                  # Referral code
        account.address,    # On Behalf Of (address)
        {"from": account}
    )
    borrow_tx.wait(1)
    print("Succesfully borrowed DAI !")
    print("---------------------------")
    print("---------------------------")

    # Get account info to check if it worked
    borrowable_eth, total_debt_eth = get_borrowable_data(lendingPool, account)
    balance_of_dai = get_dai_balance(account)

    # Repay
    print("---------------------------")
    print("---------------------------")
    print("Let's repay back what we borrowed !")
    repay_all(balance_of_dai, lendingPool, account)
    print("successfully repaid !")
    print("---------------------------")
    print("---------------------------")

    # Check our account
    borrowable_eth, total_debt_eth = get_borrowable_data(lendingPool, account)
    balance_of_dai = get_dai_balance(account)


def repay_all(_amount, _lending_pool, _account):
    approve_erc20(Web3.toWei(_amount, "ether"), _lending_pool,
                  config["networks"][network.show_active()]["dai_address"], _account)
    tx = _lending_pool.repay(
        # Address of token to repay
        config["networks"][network.show_active()]["dai_address"],
        # Amount to repay
        Web3.toWei(_amount, "ether"),
        # rate Mode 1 for fixed, 2 for variable
        2,
        # On Behalf Of (address)
        _account.address,
        {"from": _account}
    )
    tx.wait(1)
    return(tx)


def get_dai_balance(_account):
    dai_interface = interface.IDai(
        config["networks"][network.show_active()]["dai_address"])
    balance = dai_interface.balanceOf(_account.address)
    converted_balance = Web3.fromWei(balance, "ether")
    print(f"You own {converted_balance}DAI")
    return(float(converted_balance))


def get_asset_price(_price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(_price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH latest price is {converted_latest_price}")
    return(float(converted_latest_price))


def get_borrowable_data(_lending_pool, _account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrows_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = _lending_pool.getUserAccountData(_account)
    available_borrows_eth = Web3.fromWei(available_borrows_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow up to {available_borrows_eth} worth of ETH.")
    return(float(available_borrows_eth), float(total_debt_eth))


def get_lending_pool():
    lendingPoolAddressesProvider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_provider"])
    lendingPool_address = lendingPoolAddressesProvider.getLendingPool()

    lendingPool = interface.ILendingPool(lendingPool_address)
    return(lendingPool)


def approve_erc20(_amount, _spender, _erc20_address, _account):
    print("Approving ERC20 token . . .")
    erc20 = interface.IERC20(_erc20_address)
    tx = erc20.approve(_spender, _amount, {"from": _account})
    tx.wait(1)
    print("Approved !")
    return(tx)
