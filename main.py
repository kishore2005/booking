import flet as ft
import sqlitecloud
import threading
import time
import pyperclip

# Initialize pygame mixer


def fetch_bookings_with_usernames():
    conn = sqlitecloud.connect(
        "sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE"
    )
    cursor = conn.cursor()
    cursor.execute('''
        SELECT bookings.id, users.username, products.name, bookings.status, bookings.geolocation
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        JOIN products ON bookings.product_id = products.id
    ''')
    bookings = cursor.fetchall()
    conn.close()
    return bookings


def update_booking_status(booking_id, status):
    conn = sqlitecloud.connect(
        "sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE"
    )
    cursor = conn.cursor()
    cursor.execute('UPDATE bookings SET status = ? WHERE id = ?',
                   (status, booking_id))
    conn.commit()
    conn.close()


def show_bookings(page):
    bookings = fetch_bookings_with_usernames()
    booking_containers = []

    for booking in bookings:
        booking_id, username, product_name, status, geolocation = booking

        def on_status_change(e, booking_id=booking_id):
            new_status = e.control.value
            update_booking_status(booking_id, new_status)
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Status updated to {new_status}"), open=True)

        def copy_geolocation(e, geolocation=geolocation):
            print(f"Copying geolocation: {geolocation}")  # Debugging statement
            pyperclip.copy(geolocation)
            page.snack_bar = ft.SnackBar(
                ft.Text("Geolocation copied to clipboard"), open=True)

        status_dropdown = ft.Dropdown(
            value=status,
            options=[
                ft.dropdown.Option("Processing"),
                ft.dropdown.Option("Out for Delivery"),
                ft.dropdown.Option("Delivered")
            ],
            on_change=on_status_change)

        booking_details = [
            ft.Text(f"Username: {username}",
                    size=20,
                    weight=ft.FontWeight.BOLD),
            ft.Text(f"Product: {product_name}",
                    size=20,
                    weight=ft.FontWeight.BOLD),
            ft.Row(controls=[
                ft.Text(f"Geolocation: {geolocation}",
                        size=20,
                        weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.icons.COPY, on_click=copy_geolocation)
            ]), status_dropdown
        ]

        booking_container = ft.Container(
            content=ft.Card(
                content=ft.Column(
                    booking_details,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                elevation=0,
            ),
            padding=50,  # Increased padding for a larger container
            alignment=ft.alignment.center,
        )

        booking_containers.append(booking_container)

    scrollable_column = ft.Column(
        controls=booking_containers,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=20,  # Increased spacing between containers
        alignment=ft.MainAxisAlignment.START,
    )

    page.clean()  # Clear the page before adding new content
    page.add(scrollable_column)


def poll_for_updates(page):
    previous_bookings_count = len(fetch_bookings_with_usernames())

    while True:
        current_bookings_count = len(fetch_bookings_with_usernames())

        previous_bookings_count = current_bookings_count

        show_bookings(page)
        time.sleep(10)  # Poll every 10 seconds


def main(page: ft.Page):
    page.title = "Booking Display"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.appbar = ft.AppBar(title=ft.Text("Bookings"),
                            center_title=True,
                            bgcolor="#000000")

    show_bookings(page)

    # Simplified test for clipboard functionality
    def copy_text(e):
        print("Copying text to clipboard")  # Debugging statement
        pyperclip.copy("Test text")
        page.snack_bar = ft.SnackBar(ft.Text("Text copied to clipboard"),
                                     open=True)

    page.add(ft.IconButton(icon=ft.icons.COPY, on_click=copy_text))

    # Start the polling mechanism
    threading.Thread(target=poll_for_updates, args=(page, ),
                     daemon=True).start()


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
