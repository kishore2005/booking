import flet as ft
import sqlitecloud
import threading
import time

def create_users_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_password_options_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            option TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO password_options (option) VALUES
        ('compound 1'),
        ('compound 2'),
        ('compound 3')
    ''')
    conn.commit()
    conn.close()

def drop_bookings_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS bookings')
    conn.commit()
    conn.close()

def create_bookings_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Processing',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def fetch_password_options():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT option FROM password_options')
    options = cursor.fetchall()
    conn.close()
    return [option[0] for option in options]

def add_password_option(option):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO password_options (option) VALUES (?)', (option,))
    conn.commit()
    conn.close()

def fetch_products():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT id, image, name, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def signup(username, password):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def signin(username, password):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def book_product(user_id, product_id):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bookings (user_id, product_id, status) VALUES (?, ?, ?)', (user_id, product_id, 'Processing'))
    conn.commit()
    conn.close()

def update_booking_status(booking_id, status):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
    conn.commit()
    conn.close()

def fetch_bookings(user_id):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT product_id, status FROM bookings WHERE user_id = ?', (user_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def show_products(page, user):
    products = fetch_products()
    bookings = fetch_bookings(user[0])
    booking_dict = {booking[0]: booking[1] for booking in bookings}
    product_containers = []

    for product in products:
        product_id, product_image_url, product_name, product_price = product
        status = booking_dict.get(product_id)

        def on_book(e, product_id=product_id, product_name=product_name):
            book_product(user[0], product_id)
            page.snack_bar = ft.SnackBar(ft.Text(f"Product {product_name} booked successfully!"), open=True)
            refresh_data(page, user)

        product_details = [
            ft.Image(src=product_image_url, width=300, height=300),
            ft.Text(product_name, size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(f"₹{product_price}", size=25, color=ft.colors.GREEN, text_align=ft.TextAlign.CENTER),
        ]

        if status:
            product_details.append(ft.Text(f"Status: {status}", size=20, color=ft.colors.BLUE, text_align=ft.TextAlign.CENTER))

        product_details.append(ft.ElevatedButton(text="Book Now", on_click=on_book, style=ft.ButtonStyle(bgcolor=ft.colors.BLUE, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10), elevation=5, padding=16)))


        product_container = ft.Container(
            content=ft.Card(
                content=ft.Column(
                    product_details,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                elevation=5,
            ),
            padding=30,
            alignment=ft.alignment.center
        )

        product_containers.append(product_container)

    scrollable_column = ft.Column(
        controls=product_containers,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
    )

    page.add(scrollable_column)

def refresh_data(page, user):
    page.clean()
    show_products(page, user)

def main(page: ft.Page):
    page.title ="GAS BOOKING"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

  

    page.appbar = ft.AppBar(
        title=ft.Text("GAS BOOKING"),
        center_title=True,
        bgcolor="#000000"
    )

    def on_signin(e):
        username = username_input.value
        password = password_dropdown.value
        user = signin(username, password)
        if user:
            page.client_storage.set("user", {"username": username, "password": password})
            page.clean()
            show_products(page, user)
            # Start the polling mechanism
            def poll():
                while True:
                    refresh_data(page, user)
                    time.sleep(60)  # Poll every 10 seconds
            threading.Thread(target=poll, daemon=True).start()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Invalid username or password"), open=True)

    def on_signup(e):
        username = username_input.value
        password = password_dropdown.value
        signup(username, password)
        page.snack_bar = ft.SnackBar(ft.Text("Signup successful! Please sign in."), open=True)

    username_input = ft.TextField(label="Username")
    password_options = fetch_password_options()
    password_dropdown = ft.Dropdown(
        label="Password",
        options=[ft.dropdown.Option(option) for option in password_options]
    )

    signin_button = ft.ElevatedButton(text="Sign In", on_click=on_signin)
    signup_button = ft.ElevatedButton(text="Sign Up", on_click=on_signup)

    auth_form = ft.Column(
        controls=[
            username_input,
            password_dropdown,
            signin_button,
            signup_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    stored_user = page.client_storage.get("user")
    
    if stored_user:
        user = signin(stored_user["username"], stored_user["password"])
        if user:
            show_products(page, user)
            # Start the polling mechanism
            def poll():
                while True:
                    refresh_data(page, user)
                    time.sleep(60)  # Poll every 10 seconds
            threading.Thread(target=poll, daemon=True).start()
        else:
            page.add(auth_form)
    else:
        page.add(auth_form)

create_users_table()
create_password_options_table()
drop_bookings_table()  # Drop the existing bookings table if it exists
create_bookings_table()

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
