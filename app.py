from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'  # 本番時にはより複雑なキーにしてください
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースとログイン管理の初期化
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ユーザー読み込みのための関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# トップページ：ログイン済ユーザーの予定一覧
@app.route('/')
@login_required
def index():
    events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', events=events)

# ユーザー登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        # ユーザー名が既に存在するかチェック
        if User.query.filter_by(username=username).first():
            flash('このユーザー名は既に使われています。')
            return redirect(url_for('register'))
        
        # 新規ユーザーを作成
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('登録に成功しました。ログインしてください。')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('ログインしました！')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません。')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。')
    return redirect(url_for('login'))

# 新しいイベントの追加
@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        date = request.form.get('date').strip()  # フォーマットは例：YYYY-MM-DD
        description = request.form.get('description').strip()
        
        new_event = Event(title=title, date=date, description=description, user_id=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        flash('イベントが追加されました。')
        return redirect(url_for('index'))
    
    return render_template('add.html')

# イベントの編集
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        event.title = request.form.get('title').strip()
        event.date = request.form.get('date').strip()
        event.description = request.form.get('description').strip()
        db.session.commit()
        flash('イベントが更新されました。')
        return redirect(url_for('index'))
    
    return render_template('edit.html', event=event)

# イベントの削除
@app.route('/delete_event/<int:event_id>')
@login_required
def delete_event(event_id):
    event = Event.query.filter_by(id=event_id, user_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    flash('イベントが削除されました。')
    return redirect(url_for('index'))


# アカウント削除機能
@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        # 現在のユーザーに紐づくすべてのイベントを削除
        events = Event.query.filter_by(user_id=current_user.id).all()
        for event in events:
            db.session.delete(event)
        
        # ユーザーアカウントを削除する前にログアウト（セッションが残っていると問題になる場合があるため）
        user = User.query.get(current_user.id)
        logout_user()
        
        # ユーザーアカウントを削除
        db.session.delete(user)
        db.session.commit()
        
        flash('アカウントとすべてのイベントを削除しました。')
        # アカウント削除後は新規登録画面へリダイレクト（またはトップページなど適宜変更）
        return redirect(url_for('register'))
    
    # GETリクエストの場合は確認ページを表示
    return render_template('confirm_delete_account.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # まだテーブルが作成されていなければ作成
    app.run(host='0.0.0.0', port=10000)
