from brownie import (
    accounts,
    network,
    config,
    Contract,
    interface
)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "development", "ganache-local", "mainnet-fork"]


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
