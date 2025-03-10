from flask import Flask, render_template, request, jsonify # type: ignore
from flask_socketio import SocketIO # type: ignore
from datetime import datetime
import os

# Initialize the Flask app
app = Flask(__name__)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app)

# Simulated Database
users = [
    {"id": 1, "name": "Eva Mason", "points": 20, "history": []},
    {"id": 2, "name": "Nora Mason", "points": 15, "history": []},
    {"id": 3, "name": "Marco Almeida", "points": 10, "history": []},
]

chores = [
    {"id": 1, "task": "Make your bed", "points": 5},
    {"id": 2, "task": "Clean your room", "points": 10},
    {"id": 3, "task": "Do your homework", "points": 15},
    {"id": 4, "task": "Do the dishes", "points": 10},
    {"id": 5, "task": "Take out the trash", "points": 5},
]

penalties = [
    {"id": 1, "action": "Arguing", "points_lost": -5},
    {"id": 2, "action": "Fighting", "points_lost": -10},
    {"id": 3, "action": "Yelling", "points_lost": -3},
]

assigned_chores = [
    # Example:
    # {"user_id": 1, "chore_id": 2, "deadline": "2025-01-25", "status": "Pending"}
]

# Routes
@app.route('/home')
def home():
    return render_template('home.html', users=users)

@app.route('/users')
def view_users():
    return render_template('users.html', users=users)

@app.route('/chores')
def view_chores():
    return render_template('chores.html', chores=chores)

@app.route('/penalties')
def view_penalties():
    return render_template('penalties.html', penalties=penalties)

@app.route('/leaderboard')
def leaderboard():
    sorted_users = sorted(users, key=lambda u: u['points'], reverse=True)
    for user in sorted_users:
        user['points'] = max(0, min(user['points'], 100))
    return render_template('leaderboard.html', users=sorted_users)

@app.route('/assign', methods=['GET', 'POST'])
def assign_chore():
    if request.method == 'POST':
        data = request.form
        user_id = int(data.get('user_id'))
        chore_id = int(data.get('chore_id'))
        deadline = data.get('deadline')

        # Add the assigned chore to the database
        assigned_chores.append({
            "user_id": user_id,
            "chore_id": chore_id,
            "deadline": deadline,
            "status": "Pending"
        })

        return render_template('assign.html', message="Chore assigned successfully!", users=users, chores=chores)
    
    return render_template('assign.html', users=users, chores=chores)

@app.route('/users/<int:user_id>/profile')
def user_profile(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return "User not found", 404

    # Get assigned chores for this user
    user_assigned_chores = [
        {
            "task": next(c['task'] for c in chores if c['id'] == ac['chore_id']),
            "deadline": ac['deadline'],
            "status": ac['status']
        }
        for ac in assigned_chores if ac['user_id'] == user_id
    ]

    return render_template('profile.html', user=user, assigned_chores=user_assigned_chores)

@app.route('/api/users')
def get_all_users():
    return jsonify(users), 200

@app.route('/api/users/<int:user_id>/history', methods=['GET'])
def get_user_history(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"history": user['history']}), 200

@app.route('/test')
def test_route():
    app.logger.info("Accessed /test route")
    return "Test route is working!"

# Add Chore Points
@app.route('/api/users/<int:user_id>/add_chore', methods=['POST'])
def add_chore_to_user(user_id):
    data = request.json
    chore_id = data.get('chore_id')
    chore = next((c for c in chores if c['id'] == chore_id), None)
    user = next((u for u in users if u['id'] == user_id), None)

    if not user or not chore:
        return jsonify({"error": "Invalid user or chore"}), 400

    user['points'] += chore['points']
    user['history'].append({
        "action": f"Completed chore: {chore['task']}",
        "points": chore['points'],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return jsonify({"message": "Chore added successfully", "user": user}), 200

@app.route('/api/chores/<int:user_id>/<int:chore_id>/complete', methods=['POST'])
def complete_chore(user_id, chore_id):
    # Find the assigned chore
    assigned_chore = next(
        (ac for ac in assigned_chores if ac['user_id'] == user_id and ac['chore_id'] == chore_id), None
    )
    user = next((u for u in users if u['id'] == user_id), None)
    chore = next((c for c in chores if c['id'] == chore_id), None)

    if not assigned_chore or not user or not chore:
        return jsonify({"error": "Invalid user or chore"}), 400

    if assigned_chore["status"] == "Completed":
        return jsonify({"error": "Chore already completed"}), 400

    # Mark the chore as completed
    assigned_chore["status"] = "Completed"

    # Award points to the user
    user["points"] += chore["points"]

    # Add to user's history
    user["history"].append({
        "action": f"Completed chore: {chore['task']}",
        "points": chore["points"],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    return jsonify({"message": "Chore marked as completed successfully", "user": user}), 200

# Add Penalty Points
@app.route('/api/users/<int:user_id>/add_penalty', methods=['POST'])
def add_penalty_to_user(user_id):
    data = request.json
    penalty_id = data.get('penalty_id')
    penalty = next((p for p in penalties if p['id'] == penalty_id), None)
    user = next((u for u in users if u['id'] == user_id), None)

    if not user or not penalty:
        return jsonify({"error": "Invalid user or penalty"}), 400

    user['points'] += penalty['points_lost']
    user['history'].append({
        "action": f"Penalty: {penalty['action']}",
        "points": penalty['points_lost'],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return jsonify({"message": "Penalty added successfully", "user": user}), 200

@app.route('/api/chores/add', methods=['POST'])
def add_new_chore():
    data = request.json
    new_id = max(c['id'] for c in chores) + 1 if chores else 1
    new_chore = {"id": new_id, "task": data.get('task'), "points": data.get('points')}
    chores.append(new_chore)
    return jsonify({"message": "Chore added successfully", "chore": new_chore}), 200

@app.route('/api/chores/<int:chore_id>/edit', methods=['PUT'])
def edit_existing_chore(chore_id):
    data = request.json
    chore = next((c for c in chores if c['id'] == chore_id), None)
    if not chore:
        return jsonify({"error": "Chore not found"}), 404
    chore['task'] = data.get('task', chore['task'])
    chore['points'] = data.get('points', chore['points'])
    return jsonify({"message": "Chore updated successfully", "chore": chore}), 200

@app.route('/api/chores/<int:chore_id>/delete', methods=['DELETE'])
def delete_chore(chore_id):
    global chores
    chores = [c for c in chores if c['id'] != chore_id]
    return jsonify({"message": "Chore deleted successfully"}), 200

@app.route('/users/<int:user_id>/history')
def user_history(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return "User not found", 404
    return render_template('history.html', user=user)

@app.route('/api/users/<int:user_id>/reset', methods=['POST'])
def reset_points(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user['history'].append({
        "action": "Reset points",
        "points": -user['points'],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    user['points'] = 0
    return jsonify({"message": "User points reset successfully", "user": user}), 200

@app.route('/api/users/<int:user_id>/bonus', methods=['POST'])
def add_bonus(user_id):
    data = request.form
    bonus_points = int(data.get('bonus_points', 0))
    user = next((u for u in users if u['id'] == user_id), None)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user['points'] += bonus_points
    user['history'].append({
        "action": f"Bonus points added: {bonus_points}",
        "points": bonus_points,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return jsonify({"message": "Bonus points added successfully", "user": user}), 200

# Real-time updates with SocketIO
@socketio.on('update_points')
def handle_update_points(data):
    user_id = data['user_id']
    points = data['points']
    socketio.emit('points_updated', {'user_id': user_id, 'points': points})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)
