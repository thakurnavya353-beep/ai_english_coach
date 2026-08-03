import sqlite3


def create_database():

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    # Conversations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)



    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)



    # Messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        sender TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(conversation_id)
        REFERENCES conversations(id)

    )
    """)



    conn.commit()
    conn.close()





# New chat create karna
def create_conversation(title):

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO conversations(title)
        VALUES(?)
        """,
        (title,)
    )


    conn.commit()


    conversation_id = cursor.lastrowid


    conn.close()


    return conversation_id



# Message save karna

def save_message(conversation_id, sender, message):

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO messages(
        conversation_id,
        sender,
        message
        )

        VALUES(?,?,?)

        """,
        (
            conversation_id,
            sender,
            message
        )
    )


    conn.commit()
    conn.close()
    # Recent chats sidebar ke liye

def get_conversations():

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT id,title
        FROM conversations
        ORDER BY created_at DESC
        """
    )


    chats = cursor.fetchall()

    conn.close()


    return chats





# Kisi ek chat ke messages lana

def get_chat_messages(conversation_id):

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT sender,message
        FROM messages
        WHERE conversation_id=?
        """,
        (conversation_id,)
    )


    messages = cursor.fetchall()


    conn.close()


    return messages





# Recent chat open karne ke liye

def get_messages_by_conversation(conversation_id):

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT sender,message
        FROM messages
        WHERE conversation_id=?
        ORDER BY created_at
        """,
        (conversation_id,)
    )


    messages = cursor.fetchall()


    conn.close()


    return messages





create_database()





def delete_conversation(conversation_id):

    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()


    # pehle messages delete

    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id=?
        """,
        (conversation_id,)
    )



    # phir conversation delete

    cursor.execute(
        """
        DELETE FROM conversations
        WHERE id=?
        """,
        (conversation_id,)
    )


    conn.commit()
    conn.close()