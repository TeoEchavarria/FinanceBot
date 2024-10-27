import sqlite3
import json
from typing import List, Optional, Dict

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
                openai_apikey TEXT NOT NULL,
                array_debts TEXT
            )
        ''')
        self.conn.commit()
    
    def add_user_config(self, name: str, openai_apikey: str = None, array_debts: List[str] = None) -> bool:
        """
        Add a new user configuration to the database.
        
        :param name: Unique name identifier for the user.
        :param openai_apikey: User's OpenAI API key.
        :param array_debts: List of debts associated with the user.
        :return: True if addition is successful, False if user already exists.
        """
        cursor = self.conn.cursor()
        array_debts_json = json.dumps(array_debts)
        try:
            cursor.execute('''
                INSERT INTO user_configs (name, openai_apikey, array_debts)
                VALUES (?, ?, ?)
            ''', (name, openai_apikey, array_debts_json))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_user_config(self, name: str, openai_apikey: Optional[str] = None, array_debts: Optional[List[str]] = None) -> bool:
        """
        Update an existing user's configuration.
        
        :param name: Unique name identifier for the user.
        :param openai_apikey: (Optional) New OpenAI API key.
        :param array_debts: (Optional) New list of debts.
        :return: True if update is successful, False if user does not exist.
        """
        cursor = self.conn.cursor()
        fields = []
        params = []
        
        if openai_apikey is not None:
            fields.append("openai_apikey = ?")
            params.append(openai_apikey)
        
        if array_debts is not None:
            fields.append("array_debts = ?")
            params.append(json.dumps(array_debts))
        
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
        cursor.execute('SELECT name, openai_apikey, array_debts FROM user_configs WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            name, openai_apikey, array_debts_json = row
            array_debts = json.loads(array_debts_json) if array_debts_json else []
            return {
                'name': name,
                'openai_apikey': openai_apikey,
                'array_debts': array_debts
            }
        else:
            return None
    
    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()