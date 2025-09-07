import hashlib
import os
import sqlite3


class accountLogin:
    def __init__(self):
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def userExists(self, username):
        self.c.execute("SELECT 1 FROM users WHERE username = ? LIMIT 1", (username,))
        return self.c.fetchone() is not None

    def hashPassword(self, password, salt=None):
        """Generate a salted PBKDF2 hash of the password."""
        if salt is None:
            salt = os.urandom(16)  # 128-bit salt
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return salt.hex() + ":" + hashed.hex()

    def verifyPassword(self, password, stored_hash):
        """Check a password against the stored hash."""
        salt_hex, hashed_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        new_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return new_hash.hex() == hashed_hex

    def createUser(self, username, password):
        if not self.userExists(username):
            hashedPassword = self.hashPassword(password)
            self.c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashedPassword),
            )
            self.conn.commit()
            return True
        return False

    def login(self, username, password):
        self.c.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = self.c.fetchone()
        if row:
            stored_hash = row[0]
            return self.verifyPassword(password, stored_hash)
        return False
