from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kids_rewards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "kid" or "parent"
    points = db.Column(db.Integer, default=0)

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    points_required = db.Column(db.Integer, nullable=False)

class Penalty(db.Model):  # New model for penalties
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    points_lost = db.Column(db.Integer, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

# Routes
@app.route('/api/users', methods=['GET', 'POST'])
def manage_users():
    if request.method == 'POST':
        data = request.json
        user = User(name=data['name'], role=data['role'], points=0)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User added!'}), 201

    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'role': u.role, 'points': u.points} for u in users])

@app.route('/api/chores', methods=['GET', 'POST'])
def manage_chores():
    if request.method == 'POST':
        data = request.json
        chore = Chore(title=data['title'], points=data['points'], assigned_to=data['assigned_to'])
        db.session.add(chore)
        db.session.commit()
        return jsonify({'message': 'Chore added!'}), 201

    chores = Chore.query.all()
    return jsonify([{'id': c.id, 'title': c.title, 'points': c.points, 'status': c.status, 'assigned_to': c.assigned_to} for c in chores])

@app.route('/api/chores/<int:chore_id>', methods=['PUT'])
def update_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    chore.status = "Completed"

    # Add points to the user who completed the chore
    user = User.query.get_or_404(chore.assigned_to)
    user.points += chore.points

    db.session.commit()
    return jsonify({'message': 'Chore updated!'})

@app.route('/api/rewards', methods=['GET', 'POST'])
def manage_rewards():
    if request.method == 'POST':
        data = request.json
        reward = Reward(title=data['title'], points_required=data['points_required'])
        db.session.add(reward)
        db.session.commit()
        return jsonify({'message': 'Reward added!'}), 201

    rewards = Reward.query.all()
    return jsonify([{'id': r.id, 'title': r.title, 'points_required': r.points_required} for r in rewards])

@app.route('/api/penalties', methods=['GET', 'POST'])
def manage_penalties():
    if request.method == 'POST':
        data = request.json
        penalty = Penalty(title=data['title'], points_lost=data['points_lost'], assigned_to=data['assigned_to'])
        db.session.add(penalty)

        # Deduct points from the assigned user
        user = User.query.get_or_404(penalty.assigned_to)
        user.points -= penalty.points_lost
        db.session.commit()

        return jsonify({'message': 'Penalty added and points deducted!'}), 201

    penalties = Penalty.query.all()
    return jsonify([{'id': p.id, 'title': p.title, 'points_lost': p.points_lost, 'assigned_to': p.assigned_to} for p in penalties])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)

