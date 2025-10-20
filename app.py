from flask import Flask, render_template, request, flash, url_for, redirect
import re
from datetime import datetime, timedelta
from models import db, User, Article, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fefnews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123456'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к странице.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    with app.app_context():
        db.create_all() 

        test_user = User.query.filter_by(email='bich@mail.ru').first()
        if not test_user:
            test_user = User(
                name='testUser', 
                email='bich@mail.ru',
                hashed_password=generate_password_hash('12345')
            )
            db.session.add(test_user)
            db.session.commit()
        
        if Article.query.count() == 0:
            articles_data = [
                {
                    'title': 'title 1',
                    'text': 'content 1',
                    'category': 'Технологии',
                    'days_ago': 5
                },
                {
                    'title': 'title 2', 
                    'text': 'content 2',
                    'category': 'Медицина',
                    'days_ago': 3
                },
                {
                    'title': 'title 3',
                    'text': 'content 3',
                    'category': 'Общее',
                    'days_ago': 1
                }
            ]
                
            for article_data in articles_data:
                article_date = datetime.now() - timedelta(days=article_data['days_ago'])
                
                article = Article(
                    title=article_data['title'],
                    text=article_data['text'],
                    category=article_data['category'],
                    author=test_user,
                    created_date=article_date
                )
                db.session.add(article)
            
            db.session.commit()

def get_articles(category=None):
    query = Article.query
    
    if category:
        query = query.filter_by(category=category)
    
    articles_from_db = query.order_by(Article.created_date.desc()).all()
    
    articles = []
    for article in articles_from_db:
        articles.append({
            'id': article.id,
            'title': article.title,
            'date': article.created_date,
            'preview': article.text[:100] + '...' if len(article.text) > 100 else article.text,
            'content': article.text,
            'author': article.author.name,
            'category': article.category
        })
    
    return articles

def get_categories():
    categories = db.session.query(Article.category).distinct().all()
    return [category[0] for category in categories]

@app.context_processor
def inject_today():
    return {'today': datetime.now().date()}

@app.context_processor
def inject_categories():
    categories = get_categories()
    return {'categories': categories}

@app.context_processor
def inject_current_user():
    return {'current_user': current_user}

@app.route("/register", methods=['GET', 'POST'])
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
                errors['email'] = 'Пользователь с таким email уже существует'
        
        if not password:
            errors['password'] = 'Обязательно введите пароль'
        elif len(password) < 6:
            errors['password'] = 'Пароль должен содержать минимум 6 символов'
        
        if not confirm_password:
            errors['confirm_password'] = 'Обязательно подтвердите пароль'
        elif password != confirm_password:
            errors['confirm_password'] = 'Пароли не совпадают'
        
        if errors:
            return render_template('register.html', errors=errors, name=name, email=email)
        
        user = User(
            name=name,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash(f'Регистрация прошла успешно! Добро пожаловать, {user.name}!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember'))
        errors = {}

        if not email:
            errors['email'] = 'Обязательно введите email'
        if not password:
            errors['password'] = 'Обязательно введите пароль'
        
        if errors:
            return render_template('login.html', errors=errors, email=email)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.name}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            errors['login'] = 'Неверный email или пароль'
            return render_template('login.html', errors=errors, email=email)
    
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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

@app.route("/feedback", methods=['POST','GET'])
def feedback():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        usermail = request.form.get('usermail', '').strip()
        textmess = request.form.get('textmess', '').strip()
        errors = {}

        if not username:
            errors['username'] = 'Обязательно введите имя'
        if not usermail:
            errors['usermail'] = 'Обязательно введите email'
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, usermail):
                errors['usermail'] = 'Введите корректный email адрес'
        if not textmess:
            errors['textmess'] = 'Обязательно введите сообщение'
        
        if errors:
            return render_template('feedback.html', errors=errors, username=username, usermail=usermail, textmess=textmess)
        
        flash('Сообщение успешно отправлено! Спасибо за обратную связь.', 'success')
        return render_template('post_feedback.html', errors=errors, username=username, usermail=usermail, textmess=textmess)
    else:
        return render_template('feedback.html')

@app.route('/news/<int:id>')
def news(id):
    article = Article.query.get_or_404(id)

    comments = Comment.query.filter_by(article_id=id).order_by(Comment.date.desc()).all()
    
    article_data = {
        'id': article.id,
        'title': article.title,
        'date': article.created_date,
        'preview': article.text[:100] + '...' if len(article.text) > 100 else article.text,
        'content': article.text,
        'author': article.author.name,
        'category': article.category
    }
    
    return render_template('news_detail.html', article=article_data, comments=comments)

@app.route('/add-comment/<int:article_id>', methods=['POST'])
@login_required 
def add_comment(article_id):
    article = Article.query.get_or_404(article_id)
    
    author_name = current_user.name  
    
    comment_text = request.form.get('comment_text', '').strip()
    errors = {}
    
    if not comment_text:
        errors['comment_text'] = 'Обязательно введите текст комментария'
    
    if errors:
        comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.date.desc()).all()
        article_data = {
            'id': article.id,
            'title': article.title,
            'date': article.created_date,
            'preview': article.text[:100] + '...' if len(article.text) > 100 else article.text,
            'content': article.text,
            'author': article.author.name,
            'category': article.category
        }
        return render_template('news_detail.html', 
                             article=article_data, 
                             comments=comments,
                             errors=errors,
                             author_name=author_name,
                             comment_text=comment_text)
    
    comment = Comment(
        text=comment_text,
        author_name=author_name,
        article_id=article_id,
        date=datetime.now()
    )
    
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('news', id=article_id))

@app.route('/create-article', methods=['POST', 'GET'])
@login_required
def create_article():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        text = request.form.get('text', '').strip()
        category = request.form.get('category', '').strip()
        new_category = request.form.get('new_category', '').strip()
        errors = {}

        if not title:
            errors['title'] = 'Обязательно введите заголовок'
        if not text:
            errors['text'] = 'Обязательно введите текст статьи'
        
        if not category and not new_category:
            errors['category'] = 'Обязательно выберите или введите категорию'
        elif new_category:
            category = new_category

        if errors:
            return render_template('create_article.html', errors=errors, title=title, text=text, category=category)

        article = Article(
            title=title,
            text=text,
            category=category,
            author=current_user,
            created_date=datetime.now()
        )

        db.session.add(article)
        db.session.commit()
        flash('Статья успешно создана!', 'success')
        return redirect(url_for('news', id=article.id))

    return render_template('create_article.html')

@app.route('/edit-article/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    
    if article.author != current_user:
        flash('У вас нет прав для редактирования этой статьи!', 'danger')
        return redirect(url_for('news', id=id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        text = request.form.get('text', '').strip()
        category = request.form.get('category', '').strip()
        new_category = request.form.get('new_category', '').strip()
        errors = {}

        if not title:
            errors['title'] = 'Обязательно введите заголовок'
        if not text:
            errors['text'] = 'Обязательно введите текст статьи'
        
        if not category and not new_category:
            errors['category'] = 'Обязательно выберите или введите категорию'
        elif new_category:
            category = new_category

        if errors:
            return render_template('edit_article.html', errors=errors, title=title, text=text, category=category, article=article)

        article.title = title
        article.text = text
        article.category = category
        
        db.session.commit()
        return redirect(url_for('news', id=article.id))

    return render_template('edit_article.html', article=article)

@app.route('/delete-article/<int:id>', methods=['POST'])
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    
    if article.author != current_user:
        flash('У вас нет прав для удаления этой статьи!', 'danger')
        return redirect(url_for('news', id=id))
    
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/articles")
def articles():
    category = request.args.get('category', '').strip()
    if category:
        return articles_by_category(category)
    
    articles = get_articles()
    return render_template('articles.html', articles=articles)

@app.route("/articles/<category>")
def articles_by_category(category):
    valid_categories = get_categories()
    
    if category not in valid_categories:
        flash(f'Категория "{category}" не найдена!', 'danger')
        return redirect(url_for('articles'))
    
    articles = get_articles(category=category)
    return render_template('articles.html', articles=articles, current_category=category)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)