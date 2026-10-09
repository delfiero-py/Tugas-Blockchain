"""
LEVEL 4 — Blockchain dengan Transaksi
===============================================================

Pada level ini, blok menyimpan DAFTAR TRANSAKSI, bukan sekadar string `data`.
Kita belajar:
  1. Menambah transaksi ke daftar "pending" (belum ditambang).
  2. Memvalidasi transaksi (sender, recipient, amount).
  3. Mine: memindahkan semua pending ke blok baru, lalu mengosongkan pending.
  4. Menelusuri riwayat transaksi seseorang dari rantai.

Jalankan tes: pytest test_level04_transaksi.py -v
"""

import datetime
import hashlib
import json


class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain = []
        self.pending_transactions = []

        # Buat blok genesis tanpa transaksi
        self._create_block(proof=1, previous_hash="0", transactions=[])

    # ─────────────────────────── HELPER ───────────────────────────

    def hash(self, block: dict) -> str:
        """Hitung SHA-256 dari sebuah blok (dict)."""
        return hashlib.sha256(
            json.dumps(block, sort_keys=True).encode()
        ).hexdigest()

    def _valid_proof(self, previous_proof: int, proof: int) -> bool:
        """Cek apakah proof memenuhi kesulitan (difficulty)."""
        h = hashlib.sha256(
            str(proof ** 2 - previous_proof ** 2).encode()
        ).hexdigest()
        return h.startswith("0" * self.difficulty)

    def _create_block(self, proof: int, previous_hash: str, transactions: list) -> dict:
        """Buat dan simpan blok baru ke rantai."""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "transactions": list(transactions),   # salin agar tidak terpengaruh perubahan luar
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.chain.append(block)
        return block

    # ─────────────────────────── API PUBLIK ───────────────────────────

    def add_transaction(self, sender, recipient, amount) -> int:
        """
        Tambahkan transaksi ke daftar pending.

        Validasi:
        - sender dan recipient harus string tidak kosong/spasi, dan tidak boleh None
        - sender dan recipient tidak boleh sama
        - amount harus int atau float (bukan bool), dan harus > 0

        Kembalikan: index blok BERIKUTNYA (len(chain) + 1).
        Raise ValueError jika validasi gagal.
        """
        # Validasi sender
        if not isinstance(sender, str) or not sender.strip():
            raise ValueError("sender tidak valid")

        # Validasi recipient
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("recipient tidak valid")

        # Sender dan recipient tidak boleh sama
        if sender == recipient:
            raise ValueError("sender dan recipient tidak boleh sama")

        # Validasi amount: harus int/float, bukan bool, dan > 0
        if isinstance(amount, bool):
            raise ValueError("amount tidak boleh berupa bool")
        if not isinstance(amount, (int, float)):
            raise ValueError("amount harus berupa angka")
        if amount <= 0:
            raise ValueError("amount harus lebih dari 0")

        transaksi = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        }
        self.pending_transactions.append(transaksi)
        return len(self.chain) + 1

    def mine_block(self) -> dict:
        """
        Tambang blok baru yang berisi semua pending_transactions.
        Setelah ditambang, pending_transactions dikosongkan.
        """
        prev = self.chain[-1]
        proof = 1
        while not self._valid_proof(prev["proof"], proof):
            proof += 1

        blok = self._create_block(
            proof=proof,
            previous_hash=self.hash(prev),
            transactions=self.pending_transactions,
        )
        # Kosongkan pending setelah ditambang
        self.pending_transactions = []
        return blok

    def riwayat(self, nama: str) -> list:
        """
        Kembalikan daftar transaksi yang melibatkan `nama` dari blok yang sudah ditambang.

        Format kembalian: list of tuple (index_blok, transaksi_dict)
        Transaksi pending (belum ditambang) TIDAK dimasukkan.
        """
        hasil = []
        # Mulai dari index 1 (lewati genesis)
        for blok in self.chain[1:]:
            for tx in blok["transactions"]:
                if tx["sender"] == nama or tx["recipient"] == nama:
                    hasil.append((blok["index"], tx))
        return hasil
