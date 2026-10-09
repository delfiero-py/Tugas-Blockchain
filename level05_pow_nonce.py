"""
LEVEL 5 — Proof of Work dengan Nonce (PoW yang benar)
===============================================================

Perbaikan dari Level 3:
- Hash setiap blok DISIMPAN di dalam blok itu sendiri (field "hash").
- Nonce dicari sampai hash dimulai dengan "0" * difficulty.
- chain_valid() memeriksa hash tersimpan DAN bahwa nonce memenuhi PoW.
- Serangan re-link (Level 3) kini GAGAL karena nonce lama tidak memenuhi
  PoW untuk konten yang sudah diubah.

Jalankan tes: pytest test_level05_pow_nonce.py -v
"""

import hashlib
import json


class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain = []

        # Tambang blok genesis saat inisialisasi
        genesis = {"index": 0, "transactions": [], "previous_hash": "0", "nonce": 0}
        self.proof_of_work(genesis)
        self.chain.append(genesis)

    # ─────────────────────────── HELPER STATIS ───────────────────────────

    @staticmethod
    def hash_block(blok: dict) -> str:
        """
        Hitung SHA-256 dari blok, dengan MENGABAIKAN field 'hash' jika ada.
        Dict asli tidak boleh diubah.
        """
        # Buat salinan tanpa key 'hash'
        blok_tanpa_hash = {k: v for k, v in blok.items() if k != "hash"}
        return hashlib.sha256(
            json.dumps(blok_tanpa_hash, sort_keys=True).encode()
        ).hexdigest()

    # ─────────────────────────── PROOF OF WORK ───────────────────────────

    def proof_of_work(self, blok: dict) -> int:
        """
        Cari nonce terkecil (mulai dari 0) sehingga
        hash_block(blok) dimulai dengan '0' * difficulty.

        Mengubah blok['nonce'] dan blok['hash'] secara in-place.
        Kembalikan jumlah PERCOBAAN yang dilakukan (= nonce_akhir + 1).
        """
        target = "0" * self.difficulty
        blok["nonce"] = 0   # selalu mulai dari 0
        while True:
            h = self.hash_block(blok)
            if h.startswith(target):
                blok["hash"] = h
                return blok["nonce"] + 1   # percobaan = nonce + 1
            blok["nonce"] += 1


    # ─────────────────────────── API PUBLIK ───────────────────────────

    def new_block(self, transactions: list) -> dict:
        """
        Buat dan tambang blok baru dengan daftar transaksi.
        Blok yang sudah ditambang (dengan hash valid) ditambahkan ke rantai.
        """
        blok = {
            "index": len(self.chain),
            "transactions": transactions,
            "previous_hash": self.chain[-1]["hash"],
            "nonce": 0,
        }
        self.proof_of_work(blok)
        self.chain.append(blok)
        return blok

    def chain_valid(self) -> bool:
        """
        Validasi seluruh rantai:
        1. Hash tersimpan cocok dengan hash_block() sekarang.
        2. previous_hash cocok dengan hash blok sebelumnya.
        3. Nonce memenuhi PoW (hash dimulai dengan target).
        """
        target = "0" * self.difficulty
        for i, blok in enumerate(self.chain):
            # Cek hash tersimpan cocok dengan isi blok saat ini
            if blok.get("hash") != self.hash_block(blok):
                return False
            # Cek nonce memenuhi difficulty
            if not blok["hash"].startswith(target):
                return False
            # Cek previous_hash (kecuali genesis)
            if i > 0:
                if blok["previous_hash"] != self.chain[i - 1]["hash"]:
                    return False
        return True

    def tambang_ulang_dari(self, idx: int) -> int:
        """
        Tambang ulang semua blok mulai dari indeks `idx` hingga akhir rantai.
        Perbarui previous_hash setiap blok agar terhubung ke blok sebelumnya.

        Kembalikan total jumlah percobaan PoW yang dilakukan.
        """
        total_percobaan = 0
        for i in range(idx, len(self.chain)):
            blok = self.chain[i]
            # Perbarui previous_hash agar terhubung ke blok sebelumnya
            if i > 0:
                blok["previous_hash"] = self.chain[i - 1]["hash"]
            # Reset nonce lalu tambang ulang
            blok["nonce"] = 0
            total_percobaan += self.proof_of_work(blok)
        return total_percobaan
