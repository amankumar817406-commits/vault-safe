import heapq
from collections import deque
import sqlite3

# ------------------ GRAPH ------------------
graph = {}
flagged = {"U3", "U7", "U13"}  # pre-flagged fraud users

def update_graph(sender, receiver):
    if sender not in graph:
        graph[sender] = []
    graph[sender].append(receiver)


# ------------------ PRIORITY QUEUE ------------------
risk_heap = []

def add_to_heap(user_id, risk):
    heapq.heappush(risk_heap, (-risk, user_id))

def get_top_user():
    if risk_heap:
        return heapq.heappop(risk_heap)
    return None


# ------------------ BFS ------------------
def bfs_check(user):
    visited = set()
    queue = deque([user])

    while queue:
        node = queue.popleft()
        if node in flagged:
            return True
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False


# ------------------ DFS ------------------
def dfs_check(user, visited=None):
    if visited is None:
        visited = set()
    if user in visited:
        return False
    visited.add(user)
    if user in flagged:
        return True
    for neighbor in graph.get(user, []):
        if dfs_check(neighbor, visited):
            return True
    return False


# ------------------ GET USER FROM DB ------------------
def get_user(user_id):
    conn = sqlite3.connect("fraud.db")
    cursor = conn.cursor()
    cursor.execute("SELECT avg_amount, account_age FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {"avg_amount": user[0], "account_age": user[1]}
    return None


# ------------------ MAIN RISK FUNCTION ------------------
def calculate_risk(user_id, amount):
    user = get_user(user_id)

    if not user:
        return 0, {}

    risk = 0
    breakdown = {}

    # Behavioral: spike detection
    if amount > 3 * user["avg_amount"]:
        risk += 50
        breakdown["Spike Detection"] = 50
    else:
        breakdown["Spike Detection"] = 0

    # Account age
    if user["account_age"] < 30:
        risk += 30
        breakdown["New Account Risk"] = 30
    else:
        breakdown["New Account Risk"] = 0

    # BFS graph check
    if bfs_check(user_id):
        risk += 40
        breakdown["BFS Fraud Connection"] = 40
    else:
        breakdown["BFS Fraud Connection"] = 0

    # DFS graph check
    if dfs_check(user_id):
        risk += 20
        breakdown["DFS Fraud Chain"] = 20
    else:
        breakdown["DFS Fraud Chain"] = 0

    add_to_heap(user_id, risk)

    return risk, breakdown