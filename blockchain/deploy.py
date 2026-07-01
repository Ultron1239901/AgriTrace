"""
Deploy CropTrace.sol to Polygon Amoy Testnet.

Prerequisites:
  pip install web3 python-dotenv solcx

Usage:
  python deploy.py

Environment variables required:
  WEB3_PROVIDER       - Polygon Amoy RPC URL
  DEPLOYER_PRIVATE_KEY - Wallet private key with test MATIC
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3

load_dotenv()

CONTRACT_PATH = Path(__file__).parent / "contracts" / "CropTrace.sol"
ABI_PATH = Path(__file__).parent / "abi" / "CropTrace.json"


def compile_contract():
    install_solc("0.8.20")
    source = CONTRACT_PATH.read_text(encoding="utf-8")
    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {"CropTrace.sol": {"content": source}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "evm.bytecode"]}
                }
            },
        },
        solc_version="0.8.20",
    )
    contract_data = compiled["contracts"]["CropTrace.sol"]["CropTrace"]
    ABI_PATH.write_text(json.dumps(contract_data["abi"], indent=2), encoding="utf-8")
    return contract_data["abi"], contract_data["evm"]["bytecode"]["object"]


def deploy():
    provider_url = os.getenv("WEB3_PROVIDER")
    private_key = os.getenv("DEPLOYER_PRIVATE_KEY")

    if not provider_url or not private_key:
        print("Error: Set WEB3_PROVIDER and DEPLOYER_PRIVATE_KEY in environment.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(provider_url))
    if not w3.is_connected():
        print("Error: Cannot connect to Web3 provider.")
        sys.exit(1)

    account = w3.eth.account.from_key(private_key)
    print(f"Deploying from: {account.address}")
    print(f"Chain ID: {w3.eth.chain_id}")

    abi, bytecode = compile_contract()

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)

    tx = Contract.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "gas": 2000000,
            "gasPrice": w3.eth.gas_price,
            "chainId": w3.eth.chain_id,
        }
    )

    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"\nContract deployed successfully!")
    print(f"Address: {receipt.contractAddress}")
    print(f"Transaction: {tx_hash.hex()}")
    print(f"\nAdd to your .env file:")
    print(f"CONTRACT_ADDRESS={receipt.contractAddress}")


if __name__ == "__main__":
    deploy()
