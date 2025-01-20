from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Simulated Database
users = [
    {"id": 1, "name": "Eva Mason", "points": 20, "history": []},
    {"id": 2, "name": "Nora Mason", "points": 15, "history": []},
    {"id": 3, "name": "Marco Almeida", "points": 10, "history": []}
]

chores = [
    {"id": 1, "task": "Make your bed", "points": 5},
    {"id": 2, "task": "Clean your room", "points": 10},
    {"id": 3, "task": "Do your homework", "points": 15},
    {"id": 4, "task": "Do the dishes", "points": 10},
    {"id": 5, "task": "Take out the trash", "points": 5},
    {"id": 6, "task": "Walk the dog", "points": 10},
    {"id": 8, "task": "Water the plants", "points": 5},
    {"id": 9, "task": "Fold the laundry", "points": 10},
    {"id": 10, "task": "Sweep the floor", "points": 5},
    {"id": 11, "task": "Mop the floor", "points": 10},
    {"id": 12, "task": "Vacuum the carpet", "points": 10},
    {"id": 13, "task": "Clean the windows", "points": 10},
    {"id": 14, "task": "Clean the bathroom", "points": 15},
    {"id": 15, "task": "Clean the kitchen", "points": 15},
    {"id": 16, "task": "Clean the living room", "points": 10},
    {"id": 17, "task": "Clean the dining room", "points": 10},
    {"id": 18, "task": "Clean the garage", "points": 10},
    {"id": 19, "task": "Clean the backyard", "points": 10},
    {"id": 20, "task": "Clean the front yard", "points": 10},
    {"id": 21, "task": "Clean the car", "points": 10},
    {"id": 22, "task": "Clean the bikes", "points": 5},
    {"id": 23, "task": "Clean the toys", "points": 5},
    {"id": 24, "task": "Clean the shoes", "points": 5},
    {"id": 25, "task": "Clean the clothes", "points": 10},
    {"id": 26, "task": "Clean the dishes", "points": 10},
    {"id": 27, "task": "Clean the silverware", "points": 5},
    {"id": 28, "task": "Clean the pots and pans", "points": 5},
    {"id": 29, "task": "Clean the glasses", "points": 5},
    {"id": 30, "task": "Clean the plates", "points": 5},
    {"id": 31, "task": "Clean the cups", "points": 5},
    {"id": 32, "task": "Clean the bowls", "points": 5},
    {"id": 33, "task": "Clean the utensils", "points": 5},
    {"id": 34, "task": "Soing something nice for your sibling", "points": 10},
    {"id": 35, "task": "Doing something nice for your parents", "points": 10},
    {"id": 36, "task": "Doing something nice for your cousin", "points": 10},
    {"id": 37, "task": "Followed instructions", "points": 10}
]

penalties = [
    {"id": 1, "action": "Arguing", "points_lost": -5},
    {"id": 2, "action": "Fighting", "points_lost": -10},
    {"id": 3, "action": "Yelling", "points_lost": -3},
    {"id": 4, "action": "Not doing homework", "points_lost": -15},
    {"id": 5, "action": "Not cleaning room", "points_lost": -10},
    {"id": 6, "action": "Not making bed", "points_lost": -5},
    {"id": 7, "action": "Not doing chores", "points_lost": -20},
    {"id": 8, "action": "Not listening", "points_lost": -5},
    {"id": 9, "action": "Not following rules", "points_lost": -10},
    {"id": 10, "action": "Not respecting others", "points_lost": -15},
    {"id": 11, "action": "Not being honest", "points_lost": -10},
    {"id": 12, "action": "Not being responsible", "points_lost": -15},
    {"id": 13, "action": "Not being respectful", "points_lost": -10},
    {"id": 14, "action": "Not being kind", "points_lost": -10},
    {"id": 15, "action": "Not being helpful", "points_lost": -10},
    {"id": 16, "action": "Not being polite", "points_lost": -10},
    {"id": 17, "action": "Not being grateful", "points_lost": -10},
    {"id": 18, "action": "Not going to bed", "points_lost": -10},
    {"id": 19, "action": "Not waking up", "points_lost": -10},
    {"id": 20, "action": "Not eating breakfast", "points_lost": -5},
    {"id": 21, "action": "Not eating lunch", "points_lost": -5},
    {"id": 22, "action": "Not eating dinner", "points_lost": -5},
    {"id": 23, "action": "Not eating vegetables", "points_lost": -5}
]

# Routes

@app.route('/home')
def home():
    return render_template('home.html', users=users)

@app.route('/users')
def view_users():
    print("Accessed /users route")  # Debug log
    return render_template('users.html', users=users)

@app.route('/chores')
def view_chores():
    return render_template('chores.html', chores=chores)

@app.route('/penalties')
def view_penalties():
    return render_template('penalties.html', penalties=penalties)

@app.route('/test')
def test_route():
    return "Test route is working!"

if __name__ == '__main__':
    app.run(debug=True)

# Add Chore Points
@app.route('/api/users/<int:user_id>/add_chore', methods=['POST'])
def add_chore(user_id):
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

# Add Penalty Points
@app.route('/api/users/<int:user_id>/add_penalty', methods=['POST'])
def add_penalty(user_id):
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

if __name__ == '__main__':
    app.run(debug=True)
