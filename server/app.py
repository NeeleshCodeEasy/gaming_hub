import json
from flask import render_template
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    settings = db.Column(db.String(500), default='{}')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game = db.Column(db.String(100))
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route('/init')
def init_db():
    db.create_all()
    return "DB created."

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'error':'username/password required'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error':'user exists'}), 400
    u = User(username=data['username'], password_hash=generate_password_hash(data['password']))
    db.session.add(u)
    db.session.commit()
    return jsonify({'message':'registered'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    u = User.query.filter_by(username=data.get('username')).first()
    if u and check_password_hash(u.password_hash, data.get('password','')):
        return jsonify({'user_id': u.id, 'username': u.username})
    return jsonify({'error':'invalid'}), 401

@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    user_id = data.get('user_id')
    game = data.get('game')
    score = int(data.get('score',0))
    s = Score(user_id=user_id, game=game, score=score)
    db.session.add(s)
    db.session.commit()
    return jsonify({'message':'saved'})

@app.route('/leaderboard/<game>', methods=['GET'])
def leaderboard(game):
    top = (db.session.query(Score, User)
           .join(User, Score.user_id==User.id)
           .filter(Score.game==game)
           .order_by(Score.score.desc()).limit(10).all())
    results = [{'username':u.User.username, 'score':u.Score.score} for u in top]
    return jsonify(results)

@socketio.on('join')
def on_join(data):
    room = data.get('room','lobby')
    join_room(room)
    emit('status', {'msg': f"{data.get('username')} has joined."}, room=room)

@socketio.on('message')
def on_message(data):
    room = data.get('room','lobby')
    emit('message', data, room=room)

@app.route('/leaderboards')
def web_leaderboards():
    # find distinct games
    games = db.session.query(Score.game).distinct().all()
    games = [g[0] for g in games]

    all_leaders = {}
    for game in games:
        rows = (db.session.query(Score, User)
                   .join(User, Score.user_id==User.id)
                   .filter(Score.game==game)
                   .order_by(Score.score.desc()).limit(10).all())
        # convert to simple dict list
        leaders = []
        for r in rows:
            score_row, user_row = r.Score, r.User
            leaders.append({
                'username': user_row.username,
                'score': score_row.score,
                'when': score_row.created_at.strftime("%Y-%m-%d %H:%M")
            })
        all_leaders[game] = leaders

    return render_template('leaderboards.html', leaders=all_leaders)

# ===============================
# USER SETTINGS API
# ===============================
@app.route('/settings/<int:user_id>', methods=['GET'])
def get_user_settings(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({}), 404
    try:
        return jsonify(json.loads(u.settings or "{}"))
    except:
        return jsonify({}), 200

@app.route('/settings/<int:user_id>', methods=['POST'])
def save_user_settings(user_id):
    u = User.query.get(user_id)
    if not u:
        return jsonify({'error':'user not found'}), 404
    data = request.json
    u.settings = json.dumps(data)
    db.session.commit()
    return jsonify({'message':'settings saved'})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
