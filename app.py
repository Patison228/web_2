from flask import Flask, render_template, request
import re
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Получаем данные из формы
        username = request.form.get('username', '').strip()
        usermail = request.form.get('usermail', '').strip()
        textmess = request.form.get('textmess', '').strip()
        errors = {}

        if not username:
            errors['username'] = 'Поле "Имя" обязательно для заполнения'
        elif len(username) < 2:
            errors['username'] = 'Имя должно содержать минимум 2 символа'

        if not usermail:
            errors['usermail'] = 'Поле "Email" обязательно для заполнения'
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, usermail):
                errors['usermail'] = 'Введите корректный email адрес'

        if not textmess:
            errors['textmess'] = 'Поле "Сообщение" обязательно для заполнения'
        elif len(textmess) < 10:
            errors['textmess'] = 'Сообщение должно содержать минимум 10 символов'

        if errors:
            return render_template('feedback.html', 
                                 errors=errors, 
                                 username=username, 
                                 usermail=usermail, 
                                 textmess=textmess)
        
        return render_template('page_after_feedback.html',
                             username=username, 
                             usermail=usermail, 
                             textmess=textmess)
    
    else:
        return render_template('feedback.html')

if __name__ == '__main__':
    app.run(debug=True)