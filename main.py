from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.transactions import TransactionArgument, TransactionPayload, EntryFunction, Serializer, RawTransaction, SignedTransaction
from aptos_sdk.authenticator import Authenticator, Ed25519Authenticator

from loguru import logger
from time import time, sleep
import asyncio
from random import randint
from settings import *

with open('private_keys.txt', 'r') as f:
    ACCOUNTS = [x.strip() for x in f.readlines()]


async def main(number: int, key: str):
    GAS_LIMIT = randint(1500, 2000)
    GAS_PRICE = randint(100, 123)
    try:
        client = RestClient(RPC)
        account = Account.load_key(key)
        address = account.address()
        balance = int(await client.account_balance(address)) / 100000000

        logger.info(f'Account №{number} address - {address}')
        logger.info(f'Account №{number} balance - {balance} APT')

        payload = EntryFunction.natural(
            '0x3::token::opt_in_direct_transfer',
            'opt_in_direct_transfer',
            [],
            [TransactionArgument(True, Serializer.bool)]
        )

        raw_txn = RawTransaction(
            address,
            await client.account_sequence_number(address),
            TransactionPayload(payload),
            GAS_LIMIT,
            GAS_PRICE,
            int(time()) + 60,
            chain_id=1,
        )

        sign = account.sign(raw_txn.keyed())
        auth = Authenticator(
            Ed25519Authenticator(account.public_key(), sign)
        )

        tx_hash = await client.submit_bcs_transaction(SignedTransaction(raw_txn, auth))
        await client.wait_for_transaction(tx_hash)
        logger.success(f'Txn hash: {tx_hash}')
        
    except Exception as err: 
        if 'INSUFFICIENT_BALANCE' in str(err):
            logger.error(f'Account #{number} balance is not enough')
        else: 
            logger.error(err)


if __name__ == '__main__':
    for num, key in enumerate(ACCOUNTS, start=1):
        asyncio.run(main(num, key))
        sleep_time = randint(SLEEP_BETWEEN_ACCOUNTS_MIN, SLEEP_BETWEEN_ACCOUNTS_MAX)
        logger.debug(f'Sleeping {sleep_time} seconds')
        sleep(sleep_time)
    logger.success('Done 🏁')
