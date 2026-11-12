# Python Blockchain From Scratch

An educational blockchain prototype built with Python. It demonstrates how a signed transaction is verified, added to a pending pool, grouped into a block, hashed with SHA-256, and mined with a simple Proof-of-Work loop.

## What it demonstrates

- **Wallets:** Generate RSA-2048 public/private key pairs and derive wallet addresses from public-key bytes using SHA-256.
- **Digital signatures:** Sign transaction payloads with RSA-PSS and SHA-256; verify the signature before accepting a transaction.
- **Deterministic serialization:** Serialize transaction and block data as sorted, compact JSON before hashing or signing.
- **Hash-linked blocks:** Store a previous-block hash in each new block so changes to earlier data break the chain's link checks.
- **Proof of Work:** Increment a nonce until the block hash has the configured number of leading zeroes.
- **Demo balance ledger:** Assign starting balances, reject transactions that exceed available funds, and update balances when pending transactions are processed.
- **Validation and tamper detection:** Recalculate block hashes and check previous-hash links, Proof of Work, and transaction signatures.

## How the implementation flows

1. A wallet creates an RSA-2048 key pair and derives an address from its public key.
2. A transaction serializes its sender key, receiver key, and amount, then the sender signs that payload.
3. The blockchain verifies the signature and checks the sender's available demo balance before queuing the transaction.
4. Pending transactions are recorded in a block linked to the previous block hash.
5. Proof of Work searches for a nonce that produces the configured leading-zero hash prefix.
6. Chain validation recalculates block hashes and verifies links, Proof of Work, and transaction signatures.

## Project structure

```text
python-blockchain-from-scratch/
├── blockchain.py                  # Wallet, Transaction, Block, Blockchain
├── demo.py                        # End-to-end Alice-to-Bob demonstration
├── blockchain_walkthrough.ipynb   # Main Jupyter walkthrough
├── requirements.txt               # Runtime dependency
├── tests/
│   └── test_blockchain.py         # Unit tests
└── notebooks/
    └── learning/
        ├── 01_ledger.ipynb        # First in-memory transaction ledger
        └── 02_transaction_hashing.ipynb  # Serialization and SHA-256 experiments
```

`blockchain.py` contains the consolidated implementation. The notebooks in `notebooks/learning/` preserve the early learning exercises; `blockchain_walkthrough.ipynb` demonstrates the consolidated version.

## Requirements

- Python 3.10 or later
- `cryptography`

## Run on Windows

Open PowerShell or the VS Code terminal in the repository folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python demo.py
```

If PowerShell blocks virtual-environment activation, call the environment's Python directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe demo.py
```

## Run on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py
```

## Run the tests

The tests use Python's built-in `unittest` framework:

```bash
python -m unittest discover -s tests -v
```

They cover transaction signatures, tamper detection, balance checks, transaction processing, block mining, and chain validation.

## Follow the notebook

Start with `notebooks/learning/01_ledger.ipynb`, then `notebooks/learning/02_transaction_hashing.ipynb`. For the complete implementation, open `blockchain_walkthrough.ipynb` from the repository root so that its import of `blockchain.py` works.


## Publish to GitHub

Create an empty repository on GitHub named `python-blockchain-from-scratch` (do not pre-create a README, license, or `.gitignore`). Then run these commands from this project folder:

```bash
git init
git add .
git commit -m "Build Python blockchain prototype"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/python-blockchain-from-scratch.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Scope and limitations

This is a learning project, **not** a production cryptocurrency or payment system. It does not implement peer-to-peer networking, distributed consensus between independent nodes, persistent wallet/key storage, mining rewards, or a production-grade state-transition protocol. Starting balances are assigned directly for demonstration. Chain validation checks block hashes, previous-hash links, Proof of Work, and signatures in stored transactions; it is not a full audit of historical account balances.

Private keys are held in memory and are not encrypted or persisted. Do not use real funds, real private keys, or sensitive financial data with this project.
