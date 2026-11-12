"""Run a small Alice-to-Bob blockchain transfer demonstration."""

from blockchain import Blockchain, Transaction, Wallet


def main() -> None:
    alice = Wallet("Alice")
    bob = Wallet("Bob")
    blockchain = Blockchain(difficulty=4)

    # Demo-only starting balances.
    blockchain.set_balance(alice, 1_000)
    blockchain.set_balance(bob, 100)

    transaction = Transaction(alice, bob, 150)
    transaction.sign()

    print("Signature valid:", transaction.verify())
    print("Transaction accepted:", blockchain.add_transaction(transaction))
    print("Pending transactions:", len(blockchain.pending_transactions))

    blockchain.process_pending_transactions()

    print("\nBalances after mining:")
    print("Alice:", blockchain.balances[alice.address])
    print("Bob:  ", blockchain.balances[bob.address])
    print("Blocks:", len(blockchain.chain))
    print("Blockchain valid:", blockchain.is_valid())

    mined_block = blockchain.chain[-1]
    print("\nMined block:")
    print("Previous hash:", mined_block.previous_hash)
    print("Current hash: ", mined_block.current_hash)
    print("Nonce:        ", mined_block.nonce)

    # Demonstrate tamper detection without changing the original transaction object.
    mined_block.transactions[0]["amount"] = 999
    print("Blockchain valid after tampering:", blockchain.is_valid())


if __name__ == "__main__":
    main()
