import sqlite3
import json
from typing import List, Optional, Dict, Union
from datetime import datetime

class UserConfigDB:
    def __init__(self, db_path: str = 'user_configs.db'):
        """
        Initialize the connection to the SQLite3 database.
        
        :param db_path: Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.create_table()
    
    def create_table(self):
        """
        Create the user_configs table if it doesn't already exist.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_configs (
                name TEXT PRIMARY KEY,
                openai_apikey TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def add_user_config(self, name: str, openai_apikey: str = None) -> bool:
        """
        Add a new user configuration to the database.
        
        :param name: Unique name identifier for the user.
        :param openai_apikey: User's OpenAI API key.
        :return: True if addition is successful, False if user already exists.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_configs (name, openai_apikey)
                VALUES (?, ?)
            ''', (name, openai_apikey))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_user_config(self, name: str, openai_apikey: Optional[str] = None) -> bool:
        """
        Update an existing user's configuration.
        
        :param name: Unique name identifier for the user.
        :param openai_apikey: (Optional) New OpenAI API key.
        :return: True if update is successful, False if user does not exist.
        """
        cursor = self.conn.cursor()
        fields = []
        params = []
        
        if openai_apikey is not None:
            fields.append("openai_apikey = ?")
            params.append(openai_apikey)
        
        if not fields:
            print("No fields to update.")
            return False  # Nothing to update
        
        params.append(name)
        sql = f"UPDATE user_configs SET {', '.join(fields)} WHERE name = ?"
        cursor.execute(sql, params)
        self.conn.commit()
        
        if cursor.rowcount == 0:
            return False
        else:
            return True
    
    def get_user_config(self, name: str) -> Optional[Dict]:
        """
        Retrieve a user's configuration from the database.
        
        :param name: Unique name identifier for the user.
        :return: Dictionary containing user configuration or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, openai_apikey FROM user_configs WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            name, openai_apikey = row
            return {
                'name': name,
                'openai_apikey': openai_apikey
            }
        else:
            return None
    
    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

class PocketDB:
    def __init__(self, db_path: str = 'pockets.db'):
        """
        Initialize the connection to the SQLite3 database.
        
        :param db_path: Path to the SQLite database file.
        """
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """
        Create the necessary tables: pockets and transactions.
        """
        cursor = self.conn.cursor()
        
        # Create pockets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pockets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                name TEXT NOT NULL,
                cut_off_date TEXT,
                payment_date TEXT,
                interest_rate REAL,
                UNIQUE(user_name, name)
            )
        ''')
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pocket_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ('positive', 'negative')),
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY(pocket_id) REFERENCES pockets(id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def add_pocket(
        self,
        user_name: str,
        name: str,
        cut_off_date: Optional[str] = None,
        payment_date: Optional[str] = None,
        interest_rate: Optional[float] = None
    ) -> bool:
        """
        Add a new pocket for a user.
        
        :param user_name: Name of the user.
        :param name: Name of the pocket.
        :param cut_off_date: (Optional) Cut-off date for credit cards (YYYY-MM-DD).
        :param payment_date: (Optional) Payment due date for credit cards (YYYY-MM-DD).
        :param interest_rate: (Optional) Interest rate for credit cards.
        :return: True if addition is successful, False otherwise.
        """

        print(user_name, name, cut_off_date, payment_date, interest_rate)
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pockets (
                    user_name, name, cut_off_date, payment_date, interest_rate
                ) VALUES (?, ?, ?, ?, ? )
            ''', (
                user_name,
                name,
                cut_off_date,
                payment_date,
                interest_rate
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(e)
            return False
    
    def update_pocket(
        self,
        user_name: str,
        name: str,
        cut_off_date: Optional[str] = None,
        payment_date: Optional[str] = None,
        interest_rate: Optional[float] = None
    ) -> bool:
        """
        Update an existing pocket's details.
        
        :param user_name: Name of the user.
        :param name: Name of the pocket.
        :param cut_off_date: (Optional) New cut-off date.
        :param payment_date: (Optional) New payment due date.
        :param interest_rate: (Optional) New interest rate.
        :return: True if update is successful, False otherwise.
        """
        cursor = self.conn.cursor()
        fields = []
        params = []
        
        if cut_off_date is not None:
            fields.append("cut_off_date = ?")
            params.append(cut_off_date)
        
        if payment_date is not None:
            fields.append("payment_date = ?")
            params.append(payment_date)
        
        if interest_rate is not None:
            fields.append("interest_rate = ?")
            params.append(interest_rate)
        
        if not fields:
            print("No fields to update.")
            return False  # Nothing to update
        
        params.extend([user_name, name])
        sql = f'''
            UPDATE pockets SET {', '.join(fields)}
            WHERE user_name = ? AND name = ?
        '''
        cursor.execute(sql, params)
        self.conn.commit()
        
        if cursor.rowcount == 0:
            print(f"Error: Pocket '{name}' for user '{user_name}' does not exist.")
            return False
        else:
            print(f"Pocket '{name}' updated successfully for user '{user_name}'.")
            return True
    
    def delete_pocket(self, user_name: str, name: str) -> bool:
        """
        Delete a pocket for a user.
        
        :param user_name: Name of the user.
        :param name: Name of the pocket.
        :return: True if deletion is successful, False otherwise.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM pockets WHERE user_name = ? AND name = ?
        ''', (user_name, name))
        self.conn.commit()
        
        if cursor.rowcount == 0:
            print(f"Error: Pocket '{name}' for user '{user_name}' does not exist.")
            return False
        else:
            print(f"Pocket '{name}' deleted successfully for user '{user_name}'.")
            return True
    
    def add_transaction(
        self,
        user_name: str,
        pocket_name: str,
        transaction_type: str,
        amount: float,
        description: Optional[str] = None,
        date: Optional[str] = None
    ) -> bool:
        """
        Add a transaction to a specific pocket.
        
        :param user_name: Name of the user.
        :param pocket_name: Name of the pocket.
        :param transaction_type: 'positive' for money received, 'negative' for money spent.
        :param amount: Amount of the transaction.
        :param description: (Optional) Description of the transaction.
        :param date: (Optional) Date of the transaction (YYYY-MM-DD). Defaults to today.
        :return: True if addition is successful, False otherwise.
        """
        if transaction_type not in ('positive', 'negative'):
            print("Error: transaction_type must be 'positive' or 'negative'.")
            return False
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Retrieve pocket_id
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id FROM pockets WHERE user_name = ? AND name = ?
        ''', (user_name, pocket_name))
        result = cursor.fetchone()
        if not result:
            print(f"Error: Pocket '{pocket_name}' for user '{user_name}' does not exist.")
            return False
        pocket_id = result[0]
        
        # Insert transaction
        cursor.execute('''
            INSERT INTO transactions (
                pocket_id, date, transaction_type, amount, description
            ) VALUES (?, ?, ?, ?, ?)
        ''', (pocket_id, date, transaction_type, amount, description))
        self.conn.commit()
        print(f"Transaction added to pocket '{pocket_name}' for user '{user_name}'.")
        return True
    
    def get_pockets(self, user_name: str) -> List[Dict]:
        """
        Retrieve all pockets for a user.
        
        :param user_name: Name of the user.
        :return: List of dictionaries containing pocket details.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, cut_off_date, payment_date, interest_rate
            FROM pockets WHERE user_name = ?
        ''', (user_name,))

        print(user_name)
        rows = cursor.fetchall()
        
        pockets = []
        for row in rows:
            pocket = {
                'id': row[0],
                'name': row[1],
                'cut_off_date': row[2],
                'payment_date': row[3],
                'interest_rate': row[4]
            }
            pockets.append(pocket)
        return pockets
    
    def get_pocket(self, user_name: str, pocket_name: str) -> Optional[Dict]:
        """
        Retrieve a specific pocket's details.
        
        :param user_name: Name of the user.
        :param pocket_name: Name of the pocket.
        :return: Dictionary containing pocket details or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, cut_off_date, payment_date, interest_rate
            FROM pockets WHERE user_name = ? AND name = ?
        ''', (user_name, pocket_name))
        row = cursor.fetchone()
        if row:
            pocket = {
                'id': row[0],
                'name': pocket_name,
                'cut_off_date': row[1],
                'payment_date': row[2],
                'interest_rate': row[3]
            }
            return pocket
        else:
            print(f"Pocket '{pocket_name}' for user '{user_name}' not found.")
            return None
    
    def get_transactions(self, user_name: str, pocket_name: str) -> List[Dict]:
        """
        Retrieve all transactions for a specific pocket.
        
        :param user_name: Name of the user.
        :param pocket_name: Name of the pocket.
        :return: List of dictionaries containing transaction details.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id FROM pockets WHERE user_name = ? AND name = ?
        ''', (user_name, pocket_name))
        result = cursor.fetchone()
        if not result:
            print(f"Error: Pocket '{pocket_name}' for user '{user_name}' does not exist.")
            return []
        pocket_id = result[0]
        
        cursor.execute('''
            SELECT date, transaction_type, amount, description
            FROM transactions WHERE pocket_id = ? ORDER BY date DESC
        ''', (pocket_id,))
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transaction = {
                'date': row[0],
                'transaction_type': row[1],
                'amount': row[2],
                'description': row[3]
            }
            transactions.append(transaction)
        return transactions
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a specific transaction by its ID.
        
        :param transaction_id: ID of the transaction to delete.
        :return: True if deletion is successful, False otherwise.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM transactions WHERE id = ?
        ''', (transaction_id,))
        self.conn.commit()
        
        if cursor.rowcount == 0:
            print(f"Error: Transaction with ID '{transaction_id}' does not exist.")
            return False
        else:
            print(f"Transaction with ID '{transaction_id}' deleted successfully.")
            return True
    
    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()
