import os
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db
from auth import generate_token, login_required, admin_required, ensure_admin

app = Flask(__name__, static_folder=None)
CORS(app)

# Path to built frontend files
DIST_DIR = os.path.join(os.path.dirname(__file__), '..', 'dist')
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production' or not app.debug

# ── Helpers ──────────────────────────────────────────

def parse_tags(tags_val):
    if isinstance(tags_val, list):
        return tags_val
    if not tags_val:
        return []
    return [t.strip() for t in tags_val.split(',') if t.strip()]


def _row_get(row, key, default=None):
    try:
        return row[key]
    except (KeyError, IndexError):
        return default


def post_row_to_dict(row):
    return {
        'slug': row['slug'],
        'title': row['title'],
        'date': row['date'],
        'category': row['category'],
        'tags': parse_tags(row['tags']),
        'excerpt': row['excerpt'],
        'content': row['content'],
        'cover_image': _row_get(row, 'cover_image', ''),
        'status': _row_get(row, 'status', 'published'),
        'pinned': bool(_row_get(row, 'pinned', 0)),
        'author': _row_get(row, 'author_username'),
        'user_id': row['user_id'],
    }


def user_row_to_dict(row):
    return {
        'id': row['id'],
        'username': row['username'],
        'is_admin': bool(row['is_admin']),
        'bio': _row_get(row, 'bio', ''),
        'status': _row_get(row, 'status', 'active'),
        'created_at': row['created_at'],
    }

# ── Auth ──────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供注册信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 2 or len(username) > 30:
        return jsonify({'error': '用户名长度为 2-30 个字符'}), 400
    if len(password) < 3:
        return jsonify({'error': '密码至少 3 个字符'}), 400
    if not username.replace('_', '').replace('-', '').isalnum():
        return jsonify({'error': '用户名只能包含字母、数字、下划线和连字符'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': '用户名已存在'}), 409

    db.execute(
        'INSERT INTO users (username, password_hash) VALUES (?, ?)',
        (username, generate_password_hash(password))
    )
    db.commit()

    user = db.execute('SELECT id, username, is_admin FROM users WHERE username = ?', (username,)).fetchone()
    db.close()

    token = generate_token(user['id'])
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin'])},
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供用户名和密码'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '请提供用户名和密码'}), 400

    db = get_db()
    user = db.execute(
        'SELECT id, username, password_hash, is_admin, status FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    db.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': '用户名或密码错误'}), 401
    if user['status'] == 'banned':
        return jsonify({'error': '账号已被封禁'}), 403

    token = generate_token(user['id'])
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'username': user['username'], 'is_admin': bool(user['is_admin'])},
    })


@app.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (g.user['id'],)).fetchone()
    db.close()
    return jsonify({'user': user_row_to_dict(user)})

# ── Users ────────────────────────────────────────────

@app.route('/api/users', methods=['GET'])
def list_users():
    db = get_db()
    rows = db.execute(
        'SELECT id, username, bio, is_admin, status, created_at FROM users WHERE status = "active" ORDER BY created_at DESC'
    ).fetchall()
    db.close()
    return jsonify([user_row_to_dict(r) for r in rows])


@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': '用户不存在'}), 404

    posts = db.execute(
        """SELECT p.*, u.username as author_username
           FROM posts p JOIN users u ON p.user_id = u.id
           WHERE p.user_id = ? AND p.status = 'published'
           ORDER BY p.date DESC""",
        (user['id'],)
    ).fetchall()
    db.close()

    return jsonify({
        'user': user_row_to_dict(user),
        'posts': [post_row_to_dict(r) for r in posts],
    })

# ── Posts ────────────────────────────────────────────

@app.route('/api/posts', methods=['GET'])
def list_posts():
    db = get_db()
    author = request.args.get('author', '')
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = """SELECT p.*, u.username as author_username
               FROM posts p JOIN users u ON p.user_id = u.id
               WHERE u.status = 'active'"""
    params = []
    count_params = []

    if author:
        query += ' AND u.username = ?'
        params.append(author)
        count_params.append(author)
    else:
        query += " AND p.status = 'published'"

    if category:
        query += ' AND p.category = ?'
        params.append(category)
        count_params.append(category)

    # Get total count before pagination
    count_query = """SELECT COUNT(*) FROM posts p JOIN users u ON p.user_id = u.id
                     WHERE u.status = 'active'"""
    if author:
        count_query += ' AND u.username = ?'
    else:
        count_query += " AND p.status = 'published'"
    if category:
        count_query += ' AND p.category = ?'

    total = db.execute(count_query, count_params).fetchone()[0]

    query += ' ORDER BY p.pinned DESC, p.date DESC'
    query += ' LIMIT ? OFFSET ?'
    params.append(per_page)
    params.append((page - 1) * per_page)

    rows = db.execute(query, params).fetchall()

    # Client-side tag filtering (tags stored as CSV)
    if tag:
        rows = [r for r in rows if tag in parse_tags(r['tags'])]

    db.close()
    return jsonify({
        'posts': [post_row_to_dict(r) for r in rows],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, -(-total // per_page)),
    })


@app.route('/api/posts/<slug>', methods=['GET'])
def get_post(slug):
    db = get_db()
    row = db.execute(
        """SELECT p.*, u.username as author_username
           FROM posts p JOIN users u ON p.user_id = u.id
           WHERE p.slug = ? AND u.status = 'active'""",
        (slug,)
    ).fetchone()

    if not row:
        db.close()
        return jsonify({'error': '文章未找到'}), 404

    # Record view
    db.execute('INSERT INTO post_views (post_slug) VALUES (?)', (slug,))
    db.commit()

    # Get view count
    views = db.execute('SELECT COUNT(*) FROM post_views WHERE post_slug = ?', (slug,)).fetchone()[0]
    db.close()

    result = post_row_to_dict(row)
    result['views'] = views
    return jsonify(result)


@app.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供文章数据'}), 400

    slug = data.get('slug', '').strip()
    title = data.get('title', '').strip()
    content = data.get('content', '')

    if not slug or not title:
        return jsonify({'error': 'slug 和 title 为必填项'}), 400

    db = get_db()
    existing = db.execute('SELECT id FROM posts WHERE slug = ?', (slug,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': '该 slug 已存在'}), 409

    tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', '')

    db.execute(
        """INSERT INTO posts (slug, title, content, category, tags, excerpt, cover_image, date, user_id, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (slug, title, content,
         data.get('category', ''),
         tags,
         data.get('excerpt', ''),
         data.get('cover_image', ''),
         data.get('date', ''),
         g.user['id'],
         data.get('status', 'published'))
    )
    db.commit()
    db.close()
    return jsonify({'ok': True, 'slug': slug}), 201


@app.route('/api/posts/<slug>', methods=['PUT'])
@login_required
def update_post(slug):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE slug = ?', (slug,)).fetchone()
    if not post:
        db.close()
        return jsonify({'error': '文章不存在'}), 404

    # Only author or admin can edit
    if post['user_id'] != g.user['id'] and not g.user['is_admin']:
        db.close()
        return jsonify({'error': '无权编辑此文章'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供文章数据'}), 400

    tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', '')

    db.execute(
        """UPDATE posts SET title=?, content=?, category=?, tags=?, excerpt=?, cover_image=?,
           date=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE slug=?""",
        (data.get('title', post['title']),
         data.get('content', post['content']),
         data.get('category', post['category']),
         tags,
         data.get('excerpt', post['excerpt']),
         data.get('cover_image', _row_get(post, 'cover_image', '')),
         data.get('date', post['date']),
         data.get('status', post['status']),
         slug)
    )
    db.commit()
    db.close()
    return jsonify({'ok': True, 'slug': slug})


@app.route('/api/posts/<slug>', methods=['DELETE'])
@login_required
def delete_post(slug):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE slug = ?', (slug,)).fetchone()
    if not post:
        db.close()
        return jsonify({'error': '文章不存在'}), 404

    if post['user_id'] != g.user['id'] and not g.user['is_admin']:
        db.close()
        return jsonify({'error': '无权删除此文章'}), 403

    db.execute('DELETE FROM posts WHERE slug = ?', (slug,))
    db.execute('DELETE FROM comments WHERE post_slug = ?', (slug,))
    db.execute('DELETE FROM post_views WHERE post_slug = ?', (slug,))
    db.commit()
    db.close()
    return jsonify({'ok': True})

# ── My Posts (for logged-in user) ────────────────────

@app.route('/api/my/posts', methods=['GET'])
@login_required
def my_posts():
    db = get_db()
    rows = db.execute(
        """SELECT p.*, u.username as author_username
           FROM posts p JOIN users u ON p.user_id = u.id
           WHERE p.user_id = ? ORDER BY p.date DESC""",
        (g.user['id'],)
    ).fetchall()
    db.close()
    return jsonify([post_row_to_dict(r) for r in rows])

# ── Comments ─────────────────────────────────────────

@app.route('/api/comments/<slug>', methods=['GET'])
def list_comments(slug):
    db = get_db()
    rows = db.execute(
        'SELECT id, post_slug, author, content, created_at FROM comments WHERE post_slug = ? ORDER BY created_at ASC',
        (slug,)
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/comments/<slug>', methods=['POST'])
def create_comment(slug):
    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供评论内容'}), 400

    author = data.get('author', '').strip()
    content = data.get('content', '').strip()
    parent_id = data.get('parent_id')

    if not author:
        author = '匿名'
    if not content:
        return jsonify({'error': '评论内容不能为空'}), 400
    if len(content) > 2000:
        return jsonify({'error': '评论内容过长（最多2000字）'}), 400

    db = get_db()
    # Verify post exists
    post = db.execute('SELECT id FROM posts WHERE slug = ?', (slug,)).fetchone()
    if not post:
        db.close()
        return jsonify({'error': '文章不存在'}), 404

    # Verify parent comment exists and belongs to same post
    if parent_id is not None:
        parent = db.execute('SELECT id FROM comments WHERE id = ? AND post_slug = ?', (parent_id, slug)).fetchone()
        if not parent:
            db.close()
            return jsonify({'error': '父评论不存在'}), 404

    cursor = db.execute(
        'INSERT INTO comments (post_slug, author, content, parent_id) VALUES (?, ?, ?, ?)',
        (slug, author, content, parent_id)
    )
    comment_id = cursor.lastrowid
    db.commit()

    row = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    db.close()
    return jsonify(dict(row)), 201


@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    db = get_db()
    comment = db.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        db.close()
        return jsonify({'error': '评论不存在'}), 404

    # Check ownership: comment belongs to post, admin can delete any
    post = db.execute('SELECT user_id FROM posts WHERE slug = ?', (comment['post_slug'],)).fetchone()
    if post and post['user_id'] != g.user['id'] and not g.user['is_admin']:
        db.close()
        return jsonify({'error': '无权删除此评论'}), 403

    db.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    db.commit()
    db.close()
    return jsonify({'ok': True})

# ── Admin ─────────────────────────────────────────────

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    db = get_db()
    stats = {
        'users': db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'posts': db.execute('SELECT COUNT(*) FROM posts').fetchone()[0],
        'published': db.execute("SELECT COUNT(*) FROM posts WHERE status='published'").fetchone()[0],
        'drafts': db.execute("SELECT COUNT(*) FROM posts WHERE status='draft'").fetchone()[0],
        'comments': db.execute('SELECT COUNT(*) FROM comments').fetchone()[0],
        'views': db.execute('SELECT COUNT(*) FROM post_views').fetchone()[0],
    }
    db.close()
    return jsonify(stats)


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_list_users():
    db = get_db()
    rows = db.execute(
        """SELECT u.*, (SELECT COUNT(*) FROM posts WHERE user_id = u.id) as post_count
           FROM users u ORDER BY u.created_at DESC"""
    ).fetchall()
    db.close()
    result = []
    for r in rows:
        u = user_row_to_dict(r)
        u['post_count'] = r['post_count']
        result.append(u)
    return jsonify(result)


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def admin_update_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': '请提供数据'}), 400

    is_admin = data.get('is_admin')
    status = data.get('status')
    password = data.get('password')

    if is_admin is not None:
        db.execute('UPDATE users SET is_admin = ? WHERE id = ?', (1 if is_admin else 0, user_id))
    if status:
        if status not in ('active', 'banned'):
            db.close()
            return jsonify({'error': '无效的状态值'}), 400
        db.execute('UPDATE users SET status = ? WHERE id = ?', (status, user_id))
    if password:
        db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                   (generate_password_hash(password), user_id))

    db.commit()
    db.close()
    return jsonify({'ok': True})


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': '用户不存在'}), 404
    if user['is_admin']:
        db.close()
        return jsonify({'error': '不能删除管理员账号'}), 403

    # Delete all user's posts, comments, views
    post_slugs = db.execute('SELECT slug FROM posts WHERE user_id = ?', (user_id,)).fetchall()
    for p in post_slugs:
        db.execute('DELETE FROM comments WHERE post_slug = ?', (p['slug'],))
        db.execute('DELETE FROM post_views WHERE post_slug = ?', (p['slug'],))
    db.execute('DELETE FROM posts WHERE user_id = ?', (user_id,))
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    db.close()
    return jsonify({'ok': True})


@app.route('/api/admin/posts', methods=['GET'])
@admin_required
def admin_list_posts():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    total = db.execute('SELECT COUNT(*) FROM posts').fetchone()[0]

    rows = db.execute(
        """SELECT p.*, u.username as author_username
           FROM posts p JOIN users u ON p.user_id = u.id
           ORDER BY p.pinned DESC, p.date DESC
           LIMIT ? OFFSET ?""",
        (per_page, (page - 1) * per_page)
    ).fetchall()
    db.close()
    return jsonify({
        'posts': [post_row_to_dict(r) for r in rows],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, -(-total // per_page)),
    })

# ── Pin post (admin) ─────────────────────────────────

@app.route('/api/admin/posts/<slug>/pin', methods=['POST'])
@admin_required
def toggle_pin(slug):
    db = get_db()
    post = db.execute('SELECT id, pinned FROM posts WHERE slug = ?', (slug,)).fetchone()
    if not post:
        db.close()
        return jsonify({'error': '文章不存在'}), 404

    new_pinned = 0 if post['pinned'] else 1
    db.execute('UPDATE posts SET pinned = ? WHERE slug = ?', (new_pinned, slug))
    db.commit()
    db.close()
    return jsonify({'pinned': bool(new_pinned)})

# ── Related posts ────────────────────────────────────

@app.route('/api/posts/<slug>/related', methods=['GET'])
def related_posts(slug):
    db = get_db()
    post = db.execute('SELECT tags FROM posts WHERE slug = ? AND status = ?', (slug, 'published')).fetchone()
    if not post:
        db.close()
        return jsonify([])

    tags = parse_tags(post['tags'])
    if not tags:
        db.close()
        return jsonify([])

    rows = db.execute(
        "SELECT p.*, u.username as author_username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.slug != ? AND p.status = 'published' AND u.status = 'active' ORDER BY p.date DESC",
        (slug,)
    ).fetchall()
    db.close()

    scored = []
    for r in rows:
        r_tags = parse_tags(r['tags'])
        overlap = len(set(tags) & set(r_tags))
        if overlap > 0:
            scored.append((overlap, post_row_to_dict(r)))

    scored.sort(key=lambda x: x[0], reverse=True)
    return jsonify([item[1] for item in scored[:3]])

# ── Favorites ────────────────────────────────────────

@app.route('/api/favorites/<slug>', methods=['POST'])
@login_required
def toggle_favorite(slug):
    db = get_db()
    post = db.execute('SELECT id FROM posts WHERE slug = ?', (slug,)).fetchone()
    if not post:
        db.close()
        return jsonify({'error': '文章不存在'}), 404

    fav = db.execute(
        'SELECT id FROM favorites WHERE user_id = ? AND post_slug = ?',
        (g.user['id'], slug)
    ).fetchone()

    if fav:
        db.execute('DELETE FROM favorites WHERE id = ?', (fav['id'],))
        db.commit()
        db.close()
        return jsonify({'favorited': False})
    else:
        db.execute(
            'INSERT INTO favorites (user_id, post_slug) VALUES (?, ?)',
            (g.user['id'], slug)
        )
        db.commit()
        db.close()
        return jsonify({'favorited': True})

@app.route('/api/favorites/<slug>', methods=['GET'])
@login_required
def check_favorite(slug):
    db = get_db()
    fav = db.execute(
        'SELECT id FROM favorites WHERE user_id = ? AND post_slug = ?',
        (g.user['id'], slug)
    ).fetchone()
    db.close()
    return jsonify({'favorited': bool(fav)})

@app.route('/api/my/favorites', methods=['GET'])
@login_required
def my_favorites():
    db = get_db()
    rows = db.execute(
        """SELECT p.*, u.username as author_username, f.created_at as fav_date
           FROM favorites f
           JOIN posts p ON f.post_slug = p.slug
           JOIN users u ON p.user_id = u.id
           WHERE f.user_id = ?
           ORDER BY f.created_at DESC""",
        (g.user['id'],)
    ).fetchall()
    db.close()
    return jsonify([post_row_to_dict(r) for r in rows])

# ── RSS ──────────────────────────────────────────────

@app.route('/api/rss', methods=['GET'])
def rss_feed():
    from xml.etree.ElementTree import Element, SubElement, tostring
    from xml.dom import minidom

    db = get_db()
    rows = db.execute(
        """SELECT p.slug, p.title, p.excerpt, p.date, p.content, u.username
           FROM posts p JOIN users u ON p.user_id = u.id
           WHERE p.status = 'published' AND u.status = 'active'
           ORDER BY p.date DESC LIMIT 20"""
    ).fetchall()
    db.close()

    rss = Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = '博客平台'
    SubElement(channel, 'link').text = request.host_url
    SubElement(channel, 'description').text = '分享技术，记录生活'
    SubElement(channel, 'language').text = 'zh-CN'

    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', request.host_url.rstrip('/') + '/api/rss')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    for row in rows:
        item = SubElement(channel, 'item')
        SubElement(item, 'title').text = row['title']
        SubElement(item, 'link').text = request.host_url + '#/post/' + row['slug']
        SubElement(item, 'guid').text = row['slug']
        SubElement(item, 'pubDate').text = row['date']
        SubElement(item, 'author').text = row['username']
        desc = row['excerpt'] or row['content'][:200]
        SubElement(item, 'description').text = desc

    raw = tostring(rss, encoding='unicode')
    dom = minidom.parseString(raw)
    return dom.toxml(encoding='utf-8'), 200, {'Content-Type': 'application/xml; charset=utf-8'}

# ── Migrate markdown posts ───────────────────────────

def migrate_posts():
    import os, re

    posts_dir = os.path.join(os.path.dirname(__file__), '..', 'posts')
    if not os.path.isdir(posts_dir):
        return

    db = get_db()
    existing_count = db.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    if existing_count > 0:
        db.close()
        return

    # Assign existing markdown posts to admin user
    admin = db.execute('SELECT id FROM users WHERE is_admin = 1 LIMIT 1').fetchone()
    if not admin:
        db.close()
        return

    for filename in os.listdir(posts_dir):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()

        slug = filename[:-3]
        title = slug
        date = ''
        category = ''
        tags = ''
        excerpt = ''
        content = raw

        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', raw, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            content = fm_match.group(2).strip()

            for line in fm_text.split('\n'):
                kv = re.match(r'(\w+):\s*(.+)', line)
                if not kv:
                    continue
                key = kv.group(1)
                val = kv.group(2).strip().strip('"').strip("'")

                if key == 'title':
                    title = val
                elif key == 'date':
                    date = val
                elif key == 'category':
                    category = val
                elif key == 'excerpt':
                    excerpt = val
                elif key == 'tags':
                    tags_match = re.match(r'\[(.*)\]', val)
                    if tags_match:
                        tags = ','.join(t.strip().strip('"').strip("'") for t in tags_match.group(1).split(',') if t.strip())
                    else:
                        tags = val

        db.execute(
            'INSERT INTO posts (slug, title, content, category, tags, excerpt, date, user_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (slug, title, content, category, tags, excerpt, date, admin['id'], 'published')
        )

    db.commit()
    db.close()
    print(f'Migrated {len(os.listdir(posts_dir))} markdown posts to database (author: admin).')


# ── SPA static file serving (production) ──────────────

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend static files in production. API routes take precedence."""
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    if not os.path.isdir(DIST_DIR):
        return jsonify({'error': 'Frontend not built. Run: npm run build'}), 503

    file_path = os.path.join(DIST_DIR, path) if path else os.path.join(DIST_DIR, 'index.html')
    if path and os.path.isfile(file_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


# ── Entry ─────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    ensure_admin()
    migrate_posts()
    print('Blog backend running at http://localhost:5000')
    app.run(debug=True, port=5000)
