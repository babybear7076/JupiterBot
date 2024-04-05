# this file buys and sells on jupiter
# keep in mind the amount is in lamports so 1 sol would be 1000000000
# to run the code: python jup.py 8wXtPeU6557ETkp9WHFY1n1EcU6NxDvbAggHGsMYiHsB 100

# consistent sizing $100 per trade -- 15x pays back 15 rugs
# solana_sniper chat - moondevonyt@gmail.com

import requests
import sys
import json 
import base64
import asyncio
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction 
from solders.signature import Signature
from solana.rpc.api import Client 
from solana.rpc.types import TxOpts

from datetime import datetime

import dontshare as d 
import constants as c

def logWithTimestamp(message:str):
    timestamp = datetime.now()
    print(f'{c.GREEN}[{timestamp}] {message}{c.RESET}')

# KEY FROM THE FILE DONTSHARE
KEY = Keypair.from_base58_string(d.PRIVATE_KEY)
SLIPPAGE = int(d.SLIPPAGE*100)
QUOTE_TOKEN = 'So11111111111111111111111111111111111111112'

token = 'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82' # sys.argv[1]
# amount = int(d.BUY_AMOUNT*10**9) # sys.argv[2] 0.003 sol
amount = 10000000

def Jupiter_Buy():

    http_client = Client("https://api.mainnet-beta.solana.com")

    buy_token = 'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82' # BOME
    # 0. Get price update of a token
    # cur_price = requests.get(f'https://public-api.birdeye.so/public/price?address={cur_token}', headers={"Content-Type": "application/json", "x-chain": "solana", "x-api-key": "262a14021fd14e71aae1f5367c826109"}).json()
    # print(float(cur_price['data']['value']))

    logWithTimestamp("4. Get the route for a swap")
    # 4. Get the route for a swap
    quote = requests.get(f'https://quote-api.jup.ag/v6/quote?inputMint={QUOTE_TOKEN}\
    &outputMint={buy_token}\
    &amount={amount}\
    &slippageBps={SLIPPAGE}').json()

    logWithTimestamp(quote)

    logWithTimestamp("5. Get the serialized transactions to perform the swap")
    # 5. Get the serialized transactions to perform the swap
    txRes = requests.post('https://quote-api.jup.ag/v6/swap',headers={"Content-Type": "application/json"}, data=json.dumps({"quoteResponse": quote, "userPublicKey": str(KEY.pubkey()) })).json()
    print(txRes)

    logWithTimestamp("6. Deserialize and sign transactioin")
    # 6. Deserialize and sign transactioin 
    swapTx = base64.b64decode(txRes['swapTransaction'])
    tx1 = VersionedTransaction.from_bytes(swapTx)
    tx = VersionedTransaction(tx1.message, [KEY])

    logWithTimestamp("7. Execute the transaction")
    # 7. Execute the transaction
    txId = http_client.send_raw_transaction(bytes(tx), TxOpts(skip_preflight=True)).value
    logWithTimestamp(f"https://solscan.io/tx/{str(txId)}")

    logWithTimestamp("Checking transaction status...")
    get_transaction_details = http_client.confirm_transaction(tx_sig=Signature.from_string(str(txId)), sleep_seconds=1)
    transaction_status = get_transaction_details.value[0].err

    if transaction_status is None:
        logWithTimestamp("Transaction SUCCESS!")
    else:
        logWithTimestamp(f"{c.RED}! Transaction FAILED!{c.RESET}")


if __name__ == "__main__":

    # asyncio.run(Jupiter_Buy())
    Jupiter_Buy()