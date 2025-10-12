from flask import Flask, render_template, request
import re
from datetime import datetime, timedelta

app = Flask(__name__)

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
            'title': 'Грызть ногти - смертельно опасно!',
            'date': datetime.now() - timedelta(days=1),
            'preview': 'Не гры...',
            'content': 'Текст 2'
        },
        {
            'id': 3,
            'title': 'Чеченские ученые открыли стрельбу в центре города',
            'date': datetime.now() - timedelta(days=2),
            'preview': 'Последние новости из мира науки...',
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
            return render_template('feedback_wide.html', 
                                 errors=errors, 
                                 username=username, 
                                 usermail=usermail, 
                                 textmess=textmess)
        
        return render_template('post_feedback.html',
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


if __name__ == '__main__':
    app.run(debug=True)