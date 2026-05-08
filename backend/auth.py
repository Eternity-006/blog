import jwt
import os
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask import request, jsonify, g

from db import get_db

SECRET_KEY = os.environ.get('JWT_SECRET', 'dev-secret-change-in-production')


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
        'iat': datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '未登录'}), 401

        try:
            token = auth_header.split(' ', 1)[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            db = get_db()
            user = db.execute(
                'SELECT id, username, is_admin, status FROM users WHERE id = ?',
                (payload['user_id'],)
            ).fetchone()
            db.close()

            if not user:
                return jsonify({'error': '用户不存在'}), 401
            if user['status'] == 'banned':
                return jsonify({'error': '账号已被封禁'}), 403

            g.user = {
                'id': user['id'],
                'username': user['username'],
                'is_admin': bool(user['is_admin']),
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的令牌'}), 401

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '未登录'}), 401

        try:
            token = auth_header.split(' ', 1)[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            db = get_db()
            user = db.execute(
                'SELECT id, username, is_admin, status FROM users WHERE id = ?',
                (payload['user_id'],)
            ).fetchone()
            db.close()

            if not user:
                return jsonify({'error': '用户不存在'}), 401
            if not user['is_admin']:
                return jsonify({'error': '需要管理员权限'}), 403

            g.user = {
                'id': user['id'],
                'username': user['username'],
                'is_admin': True,
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效的令牌'}), 401

        return f(*args, **kwargs)
    return decorated


def ensure_admin():
    """Create default admin user if no users exist."""
    from werkzeug.security import generate_password_hash
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if count == 0:
        db.execute(
            'INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)',
            ('admin', generate_password_hash('admin'))
        )
        db.commit()
    db.close()
