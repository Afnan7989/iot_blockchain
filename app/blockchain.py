from django.conf import settings
from web3 import Web3
import os
import json
from dotenv import load_dotenv

load_dotenv()
# 1. Connect to Ganache
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
CONTRACT_ADDRESS2 = "0x2992EDB565c39675C0Db03085025d4705eD73895"
if CONTRACT_ADDRESS2 != str(CONTRACT_ADDRESS):
    print("CONTRACT_ADDRESS does not match CONTRACT_ADDRESS2, please check .env file for typos.")
if CONTRACT_ADDRESS is None:
    # This prevents the TypeError you saw earlier and clarifies the issue
    raise ValueError("CONTRACT_ADDRESS not found in .env file. Please check for typos.")
# 2. Load ABI correctly
ABI_PATH = os.path.join(settings.BASE_DIR, "contract_abi.json")

with open(ABI_PATH, "r") as f:
    abi = json.load(f)

# 3. Load contract
contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
    abi=abi
)

# 4. Load account from Ganache private key
ACCOUNT = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

def store_on_chain(cid):
    nonce = w3.eth.get_transaction_count(ACCOUNT.address)

    tx = contract.functions.storeRecord(cid).build_transaction({
        "from": ACCOUNT.address,
        "nonce": nonce,
        "gas": 200000,
        "chainId": 1337  # Ganache chain ID
    })

    signed_tx = ACCOUNT.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

    return {
        "account_address": ACCOUNT.address,
        "tx_hash": tx_hash.hex()
    }

def verify_on_chain(cid):
    return contract.functions.verify(cid).call()
