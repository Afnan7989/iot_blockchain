import json
import os
from web3 import Web3
from solcx import compile_source, install_solc, set_solc_version

# Ensure the correct version is installed and set
install_solc("0.8.20")
set_solc_version("0.8.20")

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
assert w3.is_connected(), "Ganache not running. Please open Ganache UI or run ganache-cli."

# Load the Solidity source code
try:
    with open("contract.sol", "r") as f:
        source = f.read()
except FileNotFoundError:
    print("Error: contract.sol not found in the current directory.")
    exit()

# Compile with a specific EVM version to avoid 'invalid opcode' (PUSH0)
# We target 'paris' which is widely supported by local testnets
compiled = compile_source(
    source,
    output_values=["abi", "bin"],
    solc_version="0.8.20",
    evm_version="paris"  # <--- THIS IS THE FIX
)

contract_id, contract_interface = compiled.popitem()

abi = contract_interface["abi"]
bytecode = contract_interface["bin"]

# Set the deployment account
acct = w3.eth.accounts[0]

# Initialize Contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

print("Deploying contract...")

try:
    # Submit the transaction to deploy the contract
    tx_hash = Contract.constructor().transact({"from": acct})
    
    # Wait for the transaction to be mined
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("-" * 30)
    print(f"Contract deployed successfully!")
    print(f"Contract Address: {tx_receipt.contractAddress}")
    print("-" * 30)

    # Ensure the directory exists before saving
    os.makedirs("app", exist_ok=True) # Changed from apps/blockchain to app based on your previous logs

    # Save ABI for Django runtime
    with open("app/contract_abi.json", "w") as f:
        json.dump(abi, f, indent=2)
        print("ABI saved to app/contract_abi.json")

except Exception as e:
    print(f"Deployment failed: {e}")