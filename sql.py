import sqlite3 as sql

con = sql.connect('test.db', check_same_thread=False)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS `chatIds` (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER)")
con.commit()
cur.close()

class ChatRepository:
    def __init__(self):
        self.tableName = "chatIds"

    def get(self, chat_id):
        cur = con.cursor()
        cur.execute(f"SELECT chat_id FROM {self.tableName} WHERE chat_id=?", (chat_id,))
        data = cur.fetchone()
        cur.close()
        if data:
            return data[0]
        return None

    def get_all(self):
        cur = con.cursor()
        cur.execute(f"SELECT chat_id FROM {self.tableName}")
        data = cur.fetchall()
        cur.close()
        return list(filter(lambda x: x[0], data))

    def subscribe(self, chat_id):
        cur = con.cursor()
        cur.execute(f"INSERT INTO {self.tableName}(chat_id) VALUES (?)", (chat_id,))
        con.commit()
        cur.close()

    def unsubscribe(self, chat_id):
        cur = con.cursor()
        cur.execute(f"DELETE FROM {self.tableName} WHERE chat_id=?", (chat_id,))
        con.commit()
        cur.close()