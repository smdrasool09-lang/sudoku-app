from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ─── Health Check (Required by Render) ───────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Sudoku Solver"}), 200

@app.route("/favicon.ico")
def favicon():
    return "", 204

# ─── Sudoku Logic ─────────────────────────────────────────
def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    r0, c0 = 3 * (row // 3), 3 * (col // 3)
    for r in range(r0, r0 + 3):
        for c in range(c0, c0 + 3):
            if board[r][c] == num:
                return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for num in range(1, 10):
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True

# ─── API Endpoint ─────────────────────────────────────────
@app.route("/solve", methods=["POST"])
def solve_sudoku():
    data = request.get_json()
    if not data or "board" not in data:
        return jsonify({"status": "error", "message": "Missing board"}), 400
    board = data["board"]
    if solve(board):
        return jsonify({"status": "solved", "board": board}), 200
    return jsonify({"status": "no_solution", "message": "No solution exists"}), 200

# ─── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)