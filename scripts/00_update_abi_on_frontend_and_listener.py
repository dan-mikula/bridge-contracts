import json
import os
from brownie import config


LISTENER_PATH = config["local"]["listener_path"]
FRONTEND_PATH = config["local"]["frontend_path"]


def create_abi_file(filename, target):
    with open(f"{os.getcwd()}/build/contracts/{filename}", "r") as f:
        data = json.load(f)
        with open(f"{target}/{filename}", "w") as abi:
            abi.write(json.dumps(data["abi"]))


def main():
    create_abi_file("MainChainBridge.json", LISTENER_PATH)
    create_abi_file("SideChainBridge.json", LISTENER_PATH)
    create_abi_file("USDC_BRIDGED.json", LISTENER_PATH)
    create_abi_file("MainChainBridge.json", FRONTEND_PATH)
    create_abi_file("SideChainBridge.json", FRONTEND_PATH)
