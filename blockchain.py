
"""Educational blockchain implementation using Python and the cryptography package.

This is a learning project, not production-ready cryptocurrency software.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def canonical_json(data: dict[str, Any]) -> bytes:
    """Serialize data consistently so the same content produces the same hash."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


class Wallet:
    """Create an RSA key pair and a SHA-256 address derived from its public key."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.address = hashlib.sha256(self.get_public_key_bytes()).hexdigest()

    def get_public_key_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )


class Transaction:
    """A transfer signed by the sender's private key."""

    def __init__(self, sender: Wallet, receiver: Wallet, amount: float) -> None:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Transaction amount must be a number.")
        if not math.isfinite(float(amount)) or amount <= 0:
            raise ValueError("Transaction amount must be a positive finite number.")

        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature: bytes | None = None

    def payload(self) -> dict[str, Any]:
        return {
            "sender": self.sender.get_public_key_bytes().decode("ascii"),
            "receiver": self.receiver.get_public_key_bytes().decode("ascii"),
            "amount": self.amount,
        }

    def get_data(self) -> bytes:
        return canonical_json(self.payload())

    @staticmethod
    def _signing_padding() -> padding.PSS:
        return padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        )

    def sign(self) -> None:
        self.signature = self.sender.private_key.sign(
            self.get_data(),
            self._signing_padding(),
            hashes.SHA256(),
        )

    def verify(self) -> bool:
        if self.signature is None:
            return False
        try:
            self.sender.public_key.verify(
                self.signature,
                self.get_data(),
                self._signing_padding(),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False

    def to_record(self) -> dict[str, Any]:
        if self.signature is None:
            raise ValueError("Sign the transaction before adding it to a block.")
        return {**self.payload(), "signature": self.signature.hex()}


class Block:
    """A group of signed transactions linked to the previous block by its hash."""

    def __init__(self, transactions: list[Transaction], previous_hash: str) -> None:
        self.transactions = [tx.to_record() for tx in transactions]
        self.previous_hash = previous_hash
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.nonce = 0
        self.current_hash = self.calculated_hash()

    def calculated_hash(self) -> str:
        block_data = {
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        return hashlib.sha256(canonical_json(block_data)).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        if difficulty < 0:
            raise ValueError("Difficulty cannot be negative.")
        target = "0" * difficulty
        self.current_hash = self.calculated_hash()
        while not self.current_hash.startswith(target):
            self.nonce += 1
            self.current_hash = self.calculated_hash()


class Blockchain:
    """A simple chain with a pending transaction pool and a demo balance ledger."""

    def __init__(self, difficulty: int = 4) -> None:
        if difficulty < 0:
            raise ValueError("Difficulty cannot be negative.")
        self.chain: list[Block] = [Block([], "0")]
        self.pending_transactions: list[Transaction] = []
        self.balances: dict[str, float] = {}
        self.difficulty = difficulty

    def set_balance(self, wallet: Wallet, amount: float) -> None:
        """Set a starting balance for demonstrations; this is not a real minting rule."""
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Balance must be a number.")
        if not math.isfinite(float(amount)) or amount < 0:
            raise ValueError("Balance must be a non-negative finite number.")
        self.balances[wallet.address] = float(amount)

    def add_transaction(self, transaction: Transaction) -> bool:
        """Verify and queue a transaction without allowing pending overspending."""
        if not transaction.verify():
            return False

        sender_address = transaction.sender.address
        available_balance = self.balances.get(sender_address, 0.0)
        already_pending = sum(
            tx.amount
            for tx in self.pending_transactions
            if tx.sender.address == sender_address
        )
        if available_balance - already_pending < transaction.amount:
            return False

        self.pending_transactions.append(transaction)
        return True

    def add_block(self, transactions: list[Transaction]) -> Block:
        previous_block = self.chain[-1]
        new_block = Block(transactions, previous_block.current_hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block

    def process_pending_transactions(self) -> bool:
        """Apply queued transactions, mine them into a block, and clear the pool."""
        if not self.pending_transactions:
            return False

        accepted: list[Transaction] = []
        for transaction in self.pending_transactions:
            sender_address = transaction.sender.address
            receiver_address = transaction.receiver.address
            sender_balance = self.balances.get(sender_address, 0.0)

            # Re-check at processing time in case balances changed after queuing.
            if transaction.verify() and sender_balance >= transaction.amount:
                self.balances[sender_address] = sender_balance - transaction.amount
                self.balances[receiver_address] = (
                    self.balances.get(receiver_address, 0.0) + transaction.amount
                )
                accepted.append(transaction)

        self.pending_transactions = []
        if not accepted:
            return False

        self.add_block(accepted)
        return True

    @staticmethod
    def _verify_transaction_record(record: dict[str, Any]) -> bool:
        """Verify a signed transaction stored inside a block."""
        try:
            signature = bytes.fromhex(record["signature"])
            payload = {
                "sender": record["sender"],
                "receiver": record["receiver"],
                "amount": record["amount"],
            }
            sender_public_key = serialization.load_pem_public_key(
                record["sender"].encode("ascii")
            )
            sender_public_key.verify(
                signature,
                canonical_json(payload),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except (KeyError, TypeError, ValueError, InvalidSignature):
            return False

    def is_valid(self) -> bool:
        """Check block links, hashes, proof of work, and stored signatures."""
        if not self.chain or self.chain[0].previous_hash != "0":
            return False

        for index, current_block in enumerate(self.chain):
            if current_block.current_hash != current_block.calculated_hash():
                return False

            if index == 0:
                continue

            previous_block = self.chain[index - 1]
            if current_block.previous_hash != previous_block.current_hash:
                return False
            if not current_block.current_hash.startswith("0" * self.difficulty):
                return False
            if not all(
                self._verify_transaction_record(record)
                for record in current_block.transactions
            ):
                return False

        return True
