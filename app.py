from dotenv import load_dotenv
import os
import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

load_dotenv()

print("FROM APP:", os.getenv("GROQ_API_KEY"))


from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session
)


from ai.coach import get_ai_response


from database import (
    save_message,
    get_chat_messages,
    create_conversation,
    get_conversations,
    get_messages_by_conversation,
    delete_conversation
)



app = Flask(__name__)


# Login session ke liye
app.secret_key = "speakwise_secret_key"



# ===============================
# SIGNUP
# ===============================

@app.route("/signup", methods=["POST"])
def signup():


    data = request.get_json()


    name = data.get("name")
    email = data.get("email")
    password = data.get("password")


    hashed_password = generate_password_hash(password)


    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()



    try:


        cursor.execute(
            """
            INSERT INTO users(
                name,
                email,
                password
            )
            VALUES(?,?,?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )


        conn.commit()


        # create session after signup
        user_id = cursor.lastrowid


        session["user_id"] = user_id
        session["name"] = name



        conn.close()



        return jsonify({

            "success": True,

            "message": "Account created successfully"

        })



    except Exception as e:


        conn.close()


        return jsonify({

            "success": False,

            "error": str(e)

        })




# ===============================
# LOGIN
# ===============================


@app.route("/login", methods=["POST"])
def login():


    data = request.get_json()



    email = data.get("email")

    password = data.get("password")



    conn = sqlite3.connect("chat_history.db")

    cursor = conn.cursor()



    cursor.execute(
        """
        SELECT id,name,password
        FROM users
        WHERE email=?
        """,
        (email,)
    )



    user = cursor.fetchone()



    conn.close()




    if user and check_password_hash(user[2], password):


        session["user_id"] = user[0]

        session["name"] = user[1]



        return jsonify({

            "success": True,

            "message": "Login successful"

        })




    return jsonify({

        "success": False,

        "error": "Invalid email or password"

    })



# ===============================
# CHECK SESSION
# ===============================

@app.route("/check_session")
def check_session():


    if "user_id" in session:


        return jsonify({

            "logged_in": True

        })


    return jsonify({

        "logged_in": False

    })
# ===============================
# LOGOUT
# ===============================

@app.route("/logout")
def logout():

    global current_chat

    current_chat = None

    session.clear()


    return jsonify({

        "message":"Logged out"

    })





# Current running chat

current_chat = None



# ===============================
# HOME PAGE
# ===============================

@app.route("/")
def home():

    return render_template("index.html")





# ===============================
# CHAT
# ===============================

@app.route("/chat", methods=["POST"])
def chat():

    global current_chat


    data = request.get_json()


    user_message = data.get("message","")



    try:


        if current_chat is None:


            title = user_message.strip()


            if len(title) > 30:

                title = title[:30] + "..."



            current_chat = create_conversation(title)



        conversation_id = current_chat



        save_message(
            conversation_id,
            "user",
            user_message
        )



        reply = get_ai_response(user_message)



        save_message(
            conversation_id,
            "ai",
            reply
        )



        return jsonify({

            "reply": reply

        })



    except Exception as e:


        return jsonify({

            "reply": f"Error: {str(e)}"

        })





# ===============================
# RECENT CHATS
# ===============================

@app.route("/conversations")
def conversations():


    chats = get_conversations()


    return jsonify({

        "chats": chats

    })





# ===============================
# NEW CHAT
# ===============================

@app.route("/new_chat", methods=["POST"])
def new_chat():

    global current_chat


    current_chat = None


    return jsonify({

        "message":"New conversation started"

    })





# ===============================
# OPEN CHAT HISTORY
# ===============================

@app.route("/history/<int:id>")
def chat_history(id):


    messages = get_messages_by_conversation(id)



    return jsonify({

        "messages": messages

    })





# ===============================
# DELETE CHAT
# ===============================

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_chat(id):


    delete_conversation(id)



    return jsonify({

        "status":"deleted"

    })





# ===============================
# OLD HISTORY
# ===============================

@app.route("/history")
def history():


    return jsonify({

        "messages": get_chat_messages(1)

    })





# ===============================
# RUN APP
# ===============================

if __name__=="__main__":


    app.run(debug=True)