from flask import Flask, render_template, request, flash, url_for, redirect
import re
from datetime import datetime, timedelta
from models import db, User, Article #Comment
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fefnews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.first():
            test_user = User(
                name='Тестовый Пользователь',
                email='test@example.com'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("Создан тестовый пользователь: test@example.com / password123")

def get_articles():
    return [
        {
            'id': 1,
            'title': 'Общаги - В С Е!!!',
            'date': datetime.now(),
            'preview': 'Кайданович жестко об общагах...',
            'content': 'Текст 1'
        },
        {
            'id': 2,
            'title': 'news 2',
            'date': datetime.now() - timedelta(days=1),
            'preview': 'discript 2',
            'content': 'Текст 2'
        },
        {
            'id': 3,
            'title': 'Чеченские ученые открыли...',
            'date': datetime.now() - timedelta(days=2),
            'preview': 'Стрельбу в центре города...',
            'content': 'Текст 3'
        },
        {
            'id': 4,
            'title': 'Новая школа программирования!',
            'date': datetime.now(),
            'preview': 'Сбербанк открыл профессиональную школу скама...',
            'content': 'Текст 4'
        },
    ]


@app.context_processor
def inject_today():
    return {'today': datetime.now().date()}


@app.context_processor
def inject_current_user():
    return {'current_user': current_user}


@app.route("/")
def index():
    articles = get_articles()
    return render_template('index.html', articles=articles)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        usermail = request.form.get('usermail', '').strip()
        textmess = request.form.get('textmess', '').strip()
        errors = {}

        if not username:
            errors['username'] = 'Обязательно введите имя'
        elif len(username) < 2:
            errors['username'] = 'Имя должно содержать минимум 2 символа'
        
        if not usermail:
            errors['usermail'] = 'Обязательно введите email'
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, usermail):
                errors['usermail'] = 'Введите корректный email адрес'
        
        if not textmess:
            errors['textmess'] = 'Обязательно введите сообщение'
        elif len(textmess) < 10:
            errors['textmess'] = 'Сообщение должно содержать минимум 10 символов'
        
        if errors:
            return render_template('feedback.html', 
                                 errors=errors, 
                                 username=username, 
                                 usermail=usermail, 
                                 textmess=textmess)
        else:
            print(f"   Name: {username}")
            print(f"   Email: {usermail}")
            print(f"   Message: {textmess}")
            print(f"   Send time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return render_template('page_after_feedback.html',
                                username=username, 
                                usermail=usermail, 
                                textmess=textmess)
    
    else:
        return render_template('feedback.html')


@app.route('/news/<int:id>')
def news(id):
    articles = get_articles()
    article = next((article for article in articles if article['id'] == id), None)
    
    if article is None:
        return "Статья не найдена", 404
    
    return render_template('news_detail.html', article=article)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        errors = {}
        
        if not name:
            errors['name'] = 'Обязательно введите имя'
        elif len(name) < 2:
            errors['name'] = 'Имя должно содержать минимум 2 символа'
        
        if not email:
            errors['email'] = 'Обязательно введите email'
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors['email'] = 'Введите корректный email адрес'
            elif User.query.filter_by(email=email).first():
                errors['email'] = 'Этот email уже зарегистрирован'
        
        if not password:
            errors['password'] = 'Обязательно введите пароль'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать минимум 6 символов'
        
        if not confirm_password:
            errors['confirm_password'] = 'Подтвердите пароль'
        elif password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
        
        if errors:
            return render_template('register.html', 
                                 errors=errors, 
                                 name=name, 
                                 email=email)
        
        new_user = User(
            name=name,
            email=email
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Регистрация прошла успешно! Добро пожаловать!', 'success')
        return redirect(url_for('index'))
    
    else:
        return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        errors = {}
        
        if not email:
            errors['email'] = 'Обязательно введите email'
        
        if not password:
            errors['password'] = 'Обязательно введите пароль'
        
        if not errors:
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash(f'Добро пожаловать, {user.name}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))
            else:
                errors['general'] = 'Неверный email или пароль'
        
        return render_template('login.html', 
                             errors=errors, 
                             email=email)
    
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы.', 'success')
    return redirect(url_for('index'))

@app.route('/create-article', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        text = request.form.get('text', '').strip()
        
        errors = {}
        
        if not title:
            errors['title'] = 'Обязательно введите заголовок'
        elif len(title) < 5:
            errors['title'] = 'Заголовок должен содержать минимум 5 символов'
        
        if not text:
            errors['text'] = 'Обязательно введите текст статьи'
        elif len(text) < 10:
            errors['text'] = 'Текст статьи должен содержать минимум 10 символов'
        
        if errors:
            return render_template('create_article.html', 
                                 errors=errors, 
                                 title=title, 
                                 text=text)
        
        new_article = Article(
            title=title,
            text=text,
            user_id=current_user.id
        )
        
        db.session.add(new_article)
        db.session.commit()
        
        flash('Статья успешно создана!', 'success')
        return redirect(url_for('index'))
    
    else:
        return render_template('create_article.html')

@app.route('/edit-article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    
    if article.user_id != current_user.id:
        flash('Вы можете редактировать только свои статьи!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        text = request.form.get('text', '').strip()
        
        errors = {}
        
        if not title:
            errors['title'] = 'Обязательно введите заголовок'
        elif len(title) < 5:
            errors['title'] = 'Заголовок должен содержать минимум 5 символов'
        
        if not text:
            errors['text'] = 'Обязательно введите текст статьи'
        elif len(text) < 10:
            errors['text'] = 'Текст статьи должен содержать минимум 10 символов'
        
        if errors:
            return render_template('edit_article.html', 
                                 errors=errors, 
                                 title=title, 
                                 text=text,
                                 article=article)
        
        article.title = title
        article.text = text
        db.session.commit()
        
        flash('Статья успешно обновлена!', 'success')
        return redirect(url_for('news', id=article.id))
    
    else:
        return render_template('edit_article.html', article=article)

@app.route('/delete-article/<int:id>')
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    
    if article.user_id != current_user.id:
        flash('Вы можете удалять только свои статьи!', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(article)
    db.session.commit()
    
    flash('Статья успешно удалена!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)