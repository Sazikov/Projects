import tkinter as tk
from Database import DatabaseManager
from Interface import AuthWindow


def main():
    root = tk.Tk()
    root.title("Система управления магазином")
    root.geometry("1920x1024")

    # Инициализация менеджера базы данных
    db = DatabaseManager(
        dbname="pg_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

    auth_window = AuthWindow(root, db)

    root.mainloop()


if __name__ == "__main__":
    main()