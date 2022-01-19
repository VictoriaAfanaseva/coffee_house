from flask import Flask, render_template, url_for, request, redirect, session, abort, flash
from datetime import datetime
import psycopg2, psycopg2.extras
import datetime


app = Flask(__name__) # создание приложения, которое является экземпляром класса фласк

app.config['SECRET_KEY'] = 'gospodipamagite' #Секретный ключ необходим для обеспечения безопасности сеансов на стороне клиента

#Данные для подключения к базе данных
host_db = "localhost"
port_db = "5432"
database_db = "coffee_house"
user_db = "postgres"
password_db = "12345678"

global role
role = 0

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
    global role
    role = 0
    return render_template("exitacc.html", menu=menu) # Отобразить страницу выхода

@app.route("/menu", methods=['POST', 'GET']) # Декоратор маршрута для страницы "Меню кофейни"
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
    if role == 1:
        return render_template('menu_coffe_barista.html', title="Меню", menu=menu, menu_cf=menu_cf, menu_cf_len=menu_cf_len,
                               data=data)
    elif 'userLogged' in session:
        username = session['userLogged']
    if request.method == "POST": # Вызов метода
        for r in data:
            if f'tocart{r[0]}-{r[1]}-{r[2]}' in request.form:
                conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                        password="12345678")
                crsr = conn.cursor()
                crsr.execute(f'INSERT INTO cart_cf (ph_number_cl, product_id, name_product, price) VALUES (\'{username}\', \'{r[0]}\', \'{r[1]}\', \'{r[2]}\')')
                conn.commit()
                conn.close()
                redirect('/')
                return render_template('menu_coffe.html', title="Меню", menu=menu, menu_cf=menu_cf,
                                       menu_cf_len=menu_cf_len, data=data, excepti="Товар добавлен в корзину!")

    return render_template('menu_coffe.html', title="Меню", menu=menu,menu_cf=menu_cf, menu_cf_len=menu_cf_len, data=data)


@app.route('/register', methods=['POST', 'GET']) # Декоратор маршрута для страницы регистрации
def register():
    if request.method == "POST": # Вызов метода
        login = request.form['loginreg'] # Получение логина
        name_user = request.form['namereg']  # Получение имени
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
            crsr.execute(f'INSERT INTO clients_cf (ph_number_cl, passwd_cl, name_clients_cf) VALUES (\'{login}\',\'{password}\',\'{name_user}\')')
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
    global role
    if role == 1:
        return lk_barista()
    elif 'userLogged' in session:
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                password="12345678")
        crsr = conn.cursor()
        crsr.execute('SELECT * FROM clients_cf')
        db = crsr.fetchall()
        for r in db:
            if r[0] == session['userLogged']:
                ph_number = r[1]
                name_cl = r[2]
                bonus_cl = r[4]

        crsr.execute('SELECT * FROM order_cf')
        db = crsr.fetchall()
        cart_item=db

        crsr.execute('SELECT * FROM order_cf_products')
        menu_cf = crsr.fetchall()
        menu_cf_len = len(menu_cf)
        return render_template("lk.html", username=session['userLogged'], ph_number=ph_number,name_cl=name_cl,
                               bonus_cl=bonus_cl, items=cart_item, menu_cf_len= menu_cf_len, menu_cf=menu_cf)
    else:
        return render_template("login.html", sess='userLogged' in session)

@app.route("/cart", methods=['POST', 'GET']) # Декоратор маршрута для корзины
def cart():
    global role
    if role == 1:
        return lk_barista()
    elif 'userLogged' in session:
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
        crsr = conn.cursor()
        crsr.execute('SELECT * FROM cart_cf')
        db = crsr.fetchall()
        data=db
        username = session['userLogged']
        summ_price = 0
        for r in data:
            if r[0] == session['userLogged']:
                summ_price = summ_price + r[4]
        if request.method == "POST":  # Вызов метода
            for r in data:
                if f'addorder{username}' in request.form:
                    #в чек, без состава чека
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                            password="12345678")
                    crsr = conn.cursor()
                    now = datetime.datetime.now()
                    current_time = now.strftime("%d-%m-%Y %H:%M")
                    crsr.execute(
                        f'INSERT INTO order_cf (phone_number, date, price_order) VALUES (\'{username}\',\'{current_time}\',\'{summ_price}\')')
                    conn.commit()
                    conn.close()

                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                            password="12345678")
                    crsr = conn.cursor()
                    crsr.execute('SELECT * FROM order_cf')
                    order_data = crsr.fetchall()
                    for rr in order_data:
                        if rr[0] == session['userLogged']:
                            order_data_id = rr[3]
                    crsr.execute('SELECT * FROM cart_cf')
                    data = crsr.fetchall()
                    for rr in data:
                        if rr[0] == session['userLogged']:
                            #в состав чека
                            conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                                    password="12345678")
                            crsr = conn.cursor()
                            crsr.execute(
                                f'INSERT INTO order_cf_products (order_id, product_id, name) VALUES (\'{order_data_id}\',\'{rr[1]}\',\'{rr[2]}\')')
                            conn.commit()
                            conn.close()

                    #очистка корзины
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
                    crsr = conn.cursor()
                    crsr.execute(f'DELETE FROM cart_cf WHERE ph_number_cl=\'{username}\'')
                    conn.commit()
                    conn.close()

                    #вывод пустой корзины
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
                    crsr = conn.cursor()
                    crsr.execute('SELECT * FROM cart_cf')
                    db = crsr.fetchall()
                    data = db
                    username = session['userLogged']
                    summ_price = 0
                    for r in data:
                        if r[0] == session['userLogged']:
                            summ_price = summ_price + r[4]
                    return render_template("cart.html", username=session['userLogged'], title='Ваша корзина', data=data,
                                           summ_price=summ_price, excepti="Заказ оформлен!")
                elif f'delcart{r[0]}-{r[1]}-{r[2]}-{r[3]}-{r[4]}' in request.form:
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres", password="12345678")
                    crsr = conn.cursor()
                    crsr.execute(f'DELETE FROM cart_cf WHERE ph_number_cl=\'{r[0]}\' AND product_id=\'{r[1]}\' AND name_product=\'{r[2]}\' AND id=\'{r[3]}\' AND price=\'{r[4]}\'')
                    conn.commit()
                    conn.close()
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                            password="12345678")
                    crsr = conn.cursor()
                    crsr.execute('SELECT * FROM cart_cf')
                    db = crsr.fetchall()
                    data = db
                    username = session['userLogged']
                    summ_price = 0
                    for r in data:
                        if r[0] == session['userLogged']:
                            summ_price = summ_price + r[4]
                    return render_template("cart.html", username=session['userLogged'], title='Ваша корзина', data=data,
                                           summ_price=summ_price, excepti="Товар удален из корзины!")





        return render_template("cart.html", username=session['userLogged'], title='Ваша корзина', data=data, summ_price=summ_price)
    else:
        return render_template("login.html", sess='userLogged' in session)

@app.route("/lk_barista", methods=['POST', 'GET']) # Декоратор маршрута для страницы личного кабинета баристы
def lk_barista():
    global role
    if 'userLogged' in session and (role == 1):
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                password="12345678")
        crsr = conn.cursor()
        crsr.execute('SELECT * FROM barista_cf')
        db = crsr.fetchall()
        for r in db:
            if r[0] == session['userLogged']:
                id_barista_cf = r[2]
                name_barista_cf = r[1]
        crsr.execute('SELECT * FROM order_cf')
        db = crsr.fetchall()
        cart_item=db
        crsr.execute('SELECT * FROM order_cf_products')
        menu_cf = crsr.fetchall()
        menu_cf_len = len(menu_cf)
        crsr.execute('SELECT * FROM order_cf')
        datas = crsr.fetchall()
        if request.method == "POST":  # Вызов метода
            for r in datas:
                if f'complete{r[3]}-{r[1]}' in request.form:
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                            password="12345678")
                    crsr = conn.cursor()
                    crsr.execute(f'UPDATE order_cf SET status_order = \'Готов\' WHERE order_id = \'{r[3]}\'')
                    conn.commit()
                    conn.close()
                    return render_template("lk_barista.html", username=123, id_barista_cf=id_barista_cf,
                                    name_barista_cf=name_barista_cf,
                                    data=cart_item, menu_cf_len=menu_cf_len, menu_cf=menu_cf)
                elif f'accept_order{r[3]}-{r[1]}' in request.form:
                    conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                            password="12345678")
                    crsr = conn.cursor()
                    crsr.execute(f'UPDATE order_cf SET status_order = \'Готовится\' AND employee_id =\'{username}\' WHERE order_id = \'{r[3]}\'')
                    conn.commit()
                    conn.close()
                    return render_template("lk_barista.html", username=123, id_barista_cf=id_barista_cf,
                                           name_barista_cf=name_barista_cf,
                                           data=cart_item, menu_cf_len=menu_cf_len, menu_cf=menu_cf)

        return render_template("lk_barista.html", username=123, id_barista_cf=id_barista_cf, name_barista_cf=name_barista_cf,
                        data=cart_item, menu_cf_len= menu_cf_len, menu_cf=menu_cf)
    else:
        return render_template("login.html", sess='userLogged' in session)

@app.route('/login_barista', methods=['POST', 'GET']) # Декоратор маршрута для страницы авторизации
def login_barista():

    if request.method == "POST":
        login1 = request.form['login']  # Получение логина из формы
        password1 = request.form['password']  # Получение пароля из формы
        # подключение к базе данных
        conn = psycopg2.connect(host="localhost", port="5432", database="coffee_house", user="postgres",
                                password="12345678")
        crsr = conn.cursor()
        # Выборка из БД необходимых данных
        crsr.execute('SELECT id_barista_cf, passwd_barista_cf FROM barista_cf')
        dannie = crsr.fetchall()
        b = 0
        # Цикл перебора данных из таблицы для проверки правильности пароля и логина
        for r in dannie:
            if login1 == '123' and password1 == '123':
                b = 1  # Флаг В если такой логин и пароль существуют
        if b == 1: # Если логин и пароль существует
            session['userLogged'] = login1
            global role
            role = 1
            # Авторизировать пользователя, перейти на главную страницу и отобразить сообщение
            # об успешном входе
            return lk_barista()
        else:
            # Иначе сообщить об ошибке (неверный логин\пароль))
            return render_template("login_barista.html", excepti="Такого аккаунта не существует или введён неверный пароль", title="Вход для персонала", menu=menu)
    else:   # отобразить форму авторизации
        return render_template("login_barista.html", title="Вход для персонала", menu=menu)

if __name__ == "__main__":
    app.run(debug=True)
