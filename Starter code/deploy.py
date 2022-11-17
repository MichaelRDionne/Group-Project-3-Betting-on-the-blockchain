import os
import json
from web3 import Web3
from solcx import compile_standard, install_solc
import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


# Install Solidity compiler.
_solc_version = "0.8.17"
install_solc(_solc_version)

with open("test_game.sol", "r") as file:
    test_game_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"test_game.sol": {"content": test_game_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version=_solc_version,
)
print(compiled_sol)

#with open("coinflip_abi.json", "w") as file:
#    json.dump(compiled_sol, file)

    
# get bytecode
bytecode = compiled_sol["contracts"]["test_game.sol"]["CoinFlip"]["evm"]["bytecode"]["object"]
# get abi
abi = json.loads(compiled_sol["contracts"]["test_game.sol"]["CoinFlip"]["metadata"])["output"]["abi"]

with open("coinflip_abi.json", "w") as file:
    json.dump(abi, file)


# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
address = "0x954510eC2BA516356B56781e0698a55BB1eDD493"
private_key = "5ec2ad9110f2a69ea0c5bb0a9aec08c3868175841fcd82b0917c9d8b9634062c" 

# Create the contract in Python
coinflip_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the number of latest transaction
nonce = w3.eth.getTransactionCount(address)


# build transaction

transaction = coinflip_contract.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": address,
        "nonce": nonce,
    }
)
# Sign the transaction
sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract!")
# Send the transaction
transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")

# Updates current .env file with new contract address
os.environ['CURRENT_CONTRACT_ADDRESS'] = transaction_receipt.contractAddress
dotenv.set_key(dotenv_file, 'CURRENT_CONTRACT_ADDRESS', os.environ['CURRENT_CONTRACT_ADDRESS'])
