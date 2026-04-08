from flask import Flask, request, jsonify
from fraud_engine import calculate_risk, get_top_user, update_graph
from database import insert_transaction, fetch_users, fetch_transactions
from database import register_user, login_user, fetch_user, initialize_database
import os
app = Flask(__name__)

# Initialize DB on startup
initialize_database()


# ------------------ HOME ------------------
@app.route('/')
def home():
    return "Fraud Detection System Running"


# ------------------ REGISTER ------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user_id = register_user(
            data['name'],
            data['mobile_number'],
            data['password'],
            data['mpin']
        )
        return jsonify({"message": "Registered successfully", "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------ LOGIN ------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    try:
        user = login_user(data['mobile_number'], data['mpin'])
        if user:
            return jsonify(user), 200
        return jsonify({"message": "Invalid mobile or MPIN"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------ CHECK RISK ONLY (no transaction saved) ------------------
@app.route('/check-risk', methods=['POST'])
def check_risk():
    data = request.json
    try:
        sender_id = data['sender_id']
        amount = data['amount']

        risk, breakdown = calculate_risk(sender_id, amount)

        if risk > 100:
            status = "BLOCKED"
        elif risk > 50:
            status = "WARNING"
        else:
            status = "SAFE"

        return jsonify({
            "risk": risk,
            "status": status,
            "breakdown": breakdown
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ------------------ SEND MONEY (actual transaction) ------------------
@app.route('/send-money', methods=['POST'])
def send_money():
    data = request.json
    try:
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        amount = data['amount']
        mpin = data['mpin']

        # Verify MPIN
        sender = fetch_user(sender_id)
        if not sender:
            return jsonify({"error": "Sender not found"}), 400

        if sender_id.startswith("U") and not _verify_mpin(sender_id, mpin):
            return jsonify({"error": "Invalid MPIN"}), 401

        # Calculate risk
        risk, breakdown = calculate_risk(sender_id, amount)

        if risk > 100:
            status = "BLOCKED"
        elif risk > 50:
            status = "WARNING"
        else:
            status = "SUCCESS"

        # Update graph
        update_graph(sender_id, receiver_id)

        # Save transaction (balance updated inside)
        insert_transaction(sender_id, receiver_id, amount, risk, status)

        # Return updated balance
        updated_sender = fetch_user(sender_id)

        return jsonify({
            "status": status,
            "risk": risk,
            "breakdown": breakdown,
            "new_balance": updated_sender["balance"] if updated_sender else 0
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def _verify_mpin(user_id, mpin):
    import sqlite3
    conn = sqlite3.connect("fraud.db")
    cursor = conn.cursor()
    cursor.execute("SELECT mpin FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row and str(row[0]) == str(mpin)


# ------------------ GET USERS ------------------
@app.route('/users', methods=['GET'])
def users():
    user_list = fetch_users()
    return jsonify([{"user_id": u[0], "name": u[1]} for u in user_list]), 200


# ------------------ TRANSACTIONS ------------------
@app.route('/transactions', methods=['GET'])
def transactions():
    data = fetch_transactions()
    result = []
    for t in data:
        result.append({
            "sender": t[0],
            "receiver": t[1],
            "amount": t[2],
            "risk": t[3],
            "status": t[4],
            "time": t[5]
        })
    return jsonify(result), 200


# ------------------ TOP USER ------------------
@app.route('/top-user', methods=['GET'])
def top_user():
    user = get_top_user()
    if user:
        risk, user_id = user
        return jsonify({"user_id": user_id, "risk": -risk}), 200
    return jsonify({"message": "No data"}), 200


# ------------------ RUN ------------------
if __name__ == '__main__':
    # Render provides a PORT environment variable. If it's not there, use 5000.
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' tells Flask to accept connections from outside the server
    app.run(host='0.0.0.0', port=port)