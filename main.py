from flask import Flask, render_template, url_for, request, redirect, session, abort, flash
import psycopg2, psycopg2.extras

app = Flask(__name__) # создание приложения, которое является экземпляром класса фласк

app.config['SECRET_KEY'] = 'gospodipamagite' #Секретный ключ необходим для обеспечения безопасности сеансов на стороне клиента

#Данные для подключения к базе данных
host_db = "localhost"
port_db = "5432"
database_db = "coffee_house"
user_db = "postgres"
password_db = "12345678"

#Меню, добавляемое в шапку каждой страницы сайте
menu = [{"name": "Меню", "url": "menu_coffe"},
        {"name": "Адреса заведений", "url": "adress"},
        {"name": "Обратная связь", "url": "contact"},
        {"name": "Регистрация", "url": "register"},
        {"name": "Личный кабинет", "url": "lk"},
        {"name": "Выход", "url": "exitacc"}]


@app.route("/") # Декоратор маршрута для главной страницы
def index():  # Начало функции декоратора
    if 'userLogged' in session:
        return render_template("index.html", sess='userLogged' in session, username=session['userLogged'])
    else:
        return render_template("login.html", sess='userLogged' in session)
    #return render_template('index.html', menu=menu) # Функция, позвовляющая отобразить шаблон с заданным контекстом

@app.route("/adress") # Декоратор маршрута для страницы "О кофейне"
def about():
    return render_template('adress.html', title="Адреса заведений", menu=menu)

@app.route("/contact",  methods=["POST", "GET"]) # Декоратор маршрута для страницв обратной связи
# Использованы методы GET и POST, позволяющие получать и отправлять данные
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title="Обратная связь", menu=menu)

@app.errorhandler(404) # Декоратор маршрута для страницы 404
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu), 404


@app.route('/login', methods=['POST', 'GET']) # Декоратор маршрута для страницы авторизации
def logging():

    if request.method == "POST":
        login1 = request.form['login']  # Получение логина из формы
        password1 = request.form['password']  # Получение пароля из формы
        # подключение к базе данных
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                password="12345678")
        crsr = conn.cursor()
        # Выборка из БД необходимых данных
        crsr.execute('SELECT ph_number_cl, passwd_cl FROM clients_cf')
        dannie = crsr.fetchall()
        b = 0
        # Цикл перебора данных из таблицы для проверки правильности пароля и логина
        for r in dannie:
            if login1 == r[0] and password1 == r[1]:
                b = 1  # Флаг В если такой логин и пароль существуют
        if b == 1: # Если логин и пароль существует
            session['userLogged'] = login1
            # Авторизировать пользователя, перейти на главную страницу и отобразить сообщение
            # об успешном входе
            return render_template("index.html", excepti="Вы успешно вошли!",
                                   sess='userLogged' in session,
                                   username=session['userLogged'], menu=menu)
        else:
            # Иначе сообщить об ошибке (неверный логин\пароль))
            return render_template("login.html", excepti="Такого аккаунта не существует или введён неверный пароль", title="Авторизация", menu=menu)
    else:   # отобразить форму авторизации
        return render_template("login.html", title="Авторизация", menu=menu)

@app.route('/exitacc') # Декоратор маршрута для страницы выхода
def exacc():
    session.pop('userLogged', None) # Произвести обнуления сессии пользователя
    return render_template("exitacc.html", menu=menu) # Отобразить страницу выхода

@app.route("/menu") # Декоратор маршрута для страницы "Меню кофейни"
def menu_coffe():
    # Подключение к БД
    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
    crsr = conn.cursor()
    # Выборка из БД необходимых данных
    crsr.execute('SELECT * FROM menu')
    menu_cf = crsr.fetchall()
    data = menu_cf
    # Вычисление длинны массива
    menu_cf_len = len(menu_cf)
    # Отображение страницы меню
    return render_template('menu_coffe.html', title="Меню", menu=menu,menu_cf=menu_cf, menu_cf_len=menu_cf_len, items=data)


@app.route('/register', methods=['POST', 'GET']) # Декоратор маршрута для страницы регистрации
def register():
    if request.method == "POST": # Вызов метода
        login = request.form['loginreg'] # Получение логина
        password = request.form['passwordreg'] # Получение пароля
        repassword = request.form['repasswordreg'] # Получение повтора пароля
        if not login or not password or not repassword: # Если поля пустые
            return render_template("register.html", excepti="Не оставляйте пустые поля", title="Регистрация", menu=menu)
        if password != repassword: # Если пароли не равны
            return render_template("register.html", excepti="Пароли не совпадают", title="Регистрация", menu=menu)
        else:
            # Подключение к БД
            conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
            crsr = conn.cursor()
            # Сканирование таблицы данных клиентов
            crsr.execute('SELECT * FROM clients_cf')
            # Сохранения массива с данными
            dataus = crsr.fetchall()
            # Флаг для учета совпадения логинов
            b = 1
            # ПЦикл перебора всех логинов в таблице
            for logus in dataus:
                if login == logus[0]:
                    b = 0
                    # Закрытие соединения
                    conn.close()
                    # Отображение страницы
                    return render_template("register.html", excepti="Такой логин уже существует", title="Регистрация", menu=menu)
        if b == 1:
            # Добавление кортежа в таблицу
            crsr.execute(f'INSERT INTO clients_cf (ph_number_cl, passwd_cl) VALUES (\'{login}\',\'{password}\')')
            # Коммит
            conn.commit()
            # Закрытие соединения
            conn.close()
            # Перенаправление
            redirect('/')
            # Отображение страницы
            return render_template("login.html", excepti="Вы успешно зарегистрированы!", title="Авторизация", menu=menu)
    else:
        # Отображение страницы
        return render_template("register.html", title="Регистрация", menu=menu)

@app.route("/lk") # Декоратор маршрута для страницы профиля пользователя
def lk():
    if 'userLogged' in session:
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                password="12345678")
        crsr = conn.cursor()
        crsr.execute('SELECT * FROM clients_cf')
        db = crsr.fetchall()
        for r in db:
            if r[0] == session['userLogged']:
                ph_number = r[1]
        return render_template("lk.html", username=session['userLogged'], ph_number=ph_number)
    else:
        return render_template("login.html", sess='userLogged' in session)


if __name__ == "__main__":
    app.run(debug=True)
