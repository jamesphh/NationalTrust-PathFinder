import hashlib
import sqlite3


class accountLogin:
    def __init__(self):
        # Connect to the database and create a cursor object
        self.conn = sqlite3.connect("database.db")
        self.c = self.conn.cursor()

    def userExists(self, username):
        # Check if the username exists in the database
        self.c.execute("SELECT * FROM users WHERE username = ?", (username,))
        data = self.c.fetchall()
        if len(data) == 0:
            return False
        else:
            return True

    def createUser(self, username, password):
        # Create a new user if the username and password are valid and the username does not already exist
        if not self.userExists(username):
            # Hash the password using the SHA-256 algorithm
            hashedPassword = hashlib.sha256(password.encode()).hexdigest()
            self.c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashedPassword))
            self.conn.commit()
            return True
        else:
            return False

    def login(self, username, password):
        # Check if the provided username and password match the stored values
        self.c.execute("SELECT password FROM users WHERE username = ?", (username,))
        data = self.c.fetchone()
        if data is not None:
            # Retrieve the hashed password from the database
            hashedPassword = data[0]
            # Hash the provided password and compare it to the stored hashed password
            if hashlib.sha256(password.encode()).hexdigest() == hashedPassword:
                return True
            else:
                return False
        else:
            return False
