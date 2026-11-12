import unittest

from blockchain import Blockchain, Transaction, Wallet


class BlockchainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.alice = Wallet("Alice")
        self.bob = Wallet("Bob")
        self.blockchain = Blockchain(difficulty=1)
        self.blockchain.set_balance(self.alice, 100.0)
        self.blockchain.set_balance(self.bob, 25.0)

    def test_signed_transaction_verifies_and_detects_changes(self) -> None:
        transaction = Transaction(self.alice, self.bob, 20)
        transaction.sign()

        self.assertTrue(transaction.verify())

        transaction.amount = 21
        self.assertFalse(transaction.verify())

    def test_pending_transaction_is_mined_and_updates_demo_balances(self) -> None:
        transaction = Transaction(self.alice, self.bob, 30)
        transaction.sign()

        self.assertTrue(self.blockchain.add_transaction(transaction))
        self.assertTrue(self.blockchain.process_pending_transactions())

        self.assertEqual(self.blockchain.balances[self.alice.address], 70.0)
        self.assertEqual(self.blockchain.balances[self.bob.address], 55.0)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertTrue(self.blockchain.is_valid())

    def test_insufficient_funds_are_rejected(self) -> None:
        transaction = Transaction(self.alice, self.bob, 101)
        transaction.sign()

        self.assertFalse(self.blockchain.add_transaction(transaction))
        self.assertEqual(self.blockchain.pending_transactions, [])

    def test_tampered_block_is_invalid(self) -> None:
        transaction = Transaction(self.alice, self.bob, 10)
        transaction.sign()
        self.assertTrue(self.blockchain.add_transaction(transaction))
        self.assertTrue(self.blockchain.process_pending_transactions())
        self.assertTrue(self.blockchain.is_valid())

        self.blockchain.chain[1].transactions[0]["amount"] = 999
        self.assertFalse(self.blockchain.is_valid())


if __name__ == "__main__":
    unittest.main()
