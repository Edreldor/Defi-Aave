from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def get_weth(_value):
    '''
    Mints WETH by depositing ETH
    '''
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": _value*10**18})
    print(f"Received {_value} WETH")
    return (tx)


def withdraw_weth(_value):
    '''
    Withdraw our WETH
    '''
    account = get_account()
    weth = interface.IWeth(
        config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw({"from": account, "value": _value})
    tx.wait(1)
    print(f"Succesfully withdrew {_value/(10**18)}WETH")
    return(tx)


def main():
    weth_value = 0.1
    get_weth(weth_value)
