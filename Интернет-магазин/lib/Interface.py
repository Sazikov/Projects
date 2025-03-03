import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from Database import DatabaseManager


class AuthWindow:
    def __init__(self, master, db_manager):
        self.master = master
        self.master.title("Авторизация")
        self.master.geometry("1920x1024")

        self.db = db_manager

        self.users = {
            'owner': {'password': 'owner', 'role': 'Владелец', 'phone': '1234567890'},
            'admin': {'password': 'admin', 'role': 'Администратор', 'phone': '9876543210'},
            'customer': {'password': 'customer', 'role': 'Покупатель', 'phone': '5555555555'}
        }

        self.create_auth_widgets()

    def create_auth_widgets(self):
        # Очищаем окно
        for widget in self.master.winfo_children():
            widget.destroy()

        # Логин
        ttk.Label(self.master, text="Логин:").pack(pady=5)
        self.login_entry = ttk.Entry(self.master)
        self.login_entry.pack(pady=5)

        # Пароль
        ttk.Label(self.master, text="Пароль:").pack(pady=5)
        self.password_entry = ttk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)

        # Кнопка входа
        ttk.Button(self.master, text="Войти", command=self.login).pack(pady=10)

        # Кнопка регистрации
        ttk.Button(self.master, text="Регистрация", command=self.show_registration).pack(pady=5)

    def show_registration(self):
        """Отображение окна регистрации"""
        # Очищаем окно
        for widget in self.master.winfo_children():
            widget.destroy()

        # Заголовок
        ttk.Label(self.master, text="Регистрация", font=('Arial', 14)).pack(pady=10)

        # Логин
        ttk.Label(self.master, text="Логин:").pack(pady=5)
        login_entry = ttk.Entry(self.master)
        login_entry.pack(pady=5)

        # Пароль
        ttk.Label(self.master, text="Пароль:").pack(pady=5)
        password_entry = ttk.Entry(self.master, show="*")
        password_entry.pack(pady=5)

        # Подтверждение пароля
        ttk.Label(self.master, text="Подтверждение пароля:").pack(pady=5)
        confirm_password_entry = ttk.Entry(self.master, show="*")
        confirm_password_entry.pack(pady=5)

        # Телефон
        ttk.Label(self.master, text="Телефон:").pack(pady=5)
        phone_entry = ttk.Entry(self.master)
        phone_entry.pack(pady=5)


        # Роль
        ttk.Label(self.master, text="Роль:").pack(pady=5)
        role_var = tk.StringVar(value="Клиент")
        role_combo = ttk.Combobox(self.master, textvariable=role_var, state="readonly")
        role_combo['values'] = ['Клиент', 'Администратор', 'Менеджер магазина']
        role_combo.pack(pady=5)

        # Кнопка регистрации
        def register():
            """Обработка регистрации"""
            # Проверки
            if not all([
                login_entry.get(),
                password_entry.get(),
                confirm_password_entry.get(),
                phone_entry.get(),
            ]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Проверка совпадения паролей
            if password_entry.get() != confirm_password_entry.get():
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return

            # Проверка существования логина
            if login_entry.get() in self.users:
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
                return

            # Проверка корректности телефона
            if not phone_entry.get().isdigit():
                messagebox.showerror("Ошибка", "Телефон должен содержать только цифры")
                return

            result = self.db.add_user(
                login_entry.get(),
                password_entry.get(),
                role_var.get(),
                phone_entry.get()
            )

            if result:
                messagebox.showinfo("Успех", "Пользователь зарегистрирован")
                self.create_auth_widgets()
            else:
                messagebox.showerror("Ошибка", "Не удалось зарегистрировать пользователя")

        # Кнопка регистрации
        ttk.Button(self.master, text="Зарегистрироваться", command=register).pack(pady=10)

        # Кнопка возврата
        ttk.Button(self.master, text="Назад", command=self.create_auth_widgets).pack(pady=5)

    def login(self):
        """Вход в систему с использованием DatabaseManager"""
        login = self.login_entry.get()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            user = self.db.authenticate_user(login, password)

            if user:
                user_id, role_name = user

                self.master.destroy()

                root = tk.Tk()
                DatabaseApp(root, role_name, user_id, self.db)
                root.mainloop()
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при входе: {str(e)}")


class DatabaseApp:
    def __init__(self, root, user_role, user_id, db_manager):  # Добавляем user_id в параметры
        self.root = root
        self.db = db_manager
        self.user_id = user_id

        # Получаем название роли по её ID
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT Name 
                        FROM Role 
                        WHERE Id = %s
                    """, (user_role,))
                    role_info = cursor.fetchone()

                    if role_info:
                        role_name = role_info[0]
                        self.user_role = role_name
                        self.root.title(f"Управление магазином - {role_name}")
                    else:
                        self.user_role = "Пользователь"
                        self.root.title(f"Управление магазином - Пользователь")
        except Exception as e:
            print(f"Ошибка при получении информации о роли: {e}")
            self.user_role = "Пользователь"
            self.root.title(f"Управление магазином - Пользователь")

        self.root.geometry("1280x800")

        # Создание главного фрейма
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True)

        # Создание панели с информацией о пользователе и кнопкой выхода
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill='x', padx=10, pady=5)

        try:
            # Получаем информацию о конкретном пользователе по его ID
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT Login, Phone
                        FROM Users
                        WHERE Id_user = %s
                    """, (self.user_id,))
                    user_details = cursor.fetchone()

                    if user_details:
                        login, phone = user_details
                        user_info_text = f"Пользователь: {login} | Телефон: {phone}"
                    else:
                        user_info_text = f"Пользователь: {self.user_role}"

                    ttk.Label(top_frame, text=user_info_text, font=('Arial', 10)).pack(side='left')
        except Exception as e:
            print(f"Ошибка при получении деталей пользователя: {e}")
            ttk.Label(top_frame, text=f"Пользователь: {self.user_role}", font=('Arial', 10)).pack(side='left')

        # Кнопка выхода
        exit_button = ttk.Button(top_frame, text="Выйти", command=self.logout)
        exit_button.pack(side='right')

        # Создание вкладок с учетом роли
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(expand=True, fill='both')

        # Создаем вкладки на основе роли
        self.create_tabs()


    def logout(self):
        """Выход из системы"""
        self.root.destroy()

        # Создаем новое окно авторизации
        root = tk.Tk()
        AuthWindow(root, self.db)
        root.mainloop()

    def create_tabs(self):
        """Создание вкладок с учетом роли"""
        tabs_config = {
            'Администратор': [
                self.create_products_tab,
                self.create_shops_tab,
                self.create_users_tab,
                self.create_orders_tab,
                self.create_reports_tab
            ],
            'Менеджер магазина': [
                self.create_products_tab,
                self.create_users_tab,
                self.create_orders_tab,
                self.create_order_tab
            ],
            'Клиент': [
                self.create_orders_tab,
                self.create_order_tab
            ]
        }

        # Получаем список вкладок для текущей роли
        tabs_to_create = tabs_config.get(self.user_role, [])

        # Создаем вкладки
        for create_tab_func in tabs_to_create:
            create_tab_func()

    def create_order_tab(self):
        """Создание вкладки для создания нового заказа"""
        order_frame = ttk.Frame(self.notebook)
        self.notebook.add(order_frame, text="Создать заказ")

        # Список доступных товаров
        ttk.Label(order_frame, text="Доступные товары:", font=('Arial', 12)).pack(pady=10)

        # Таблица товаров
        products_tree = ttk.Treeview(order_frame,
                                     columns=('ID', 'Название', 'Категория', 'Цена', 'Количество'),
                                     show='headings')
        products_tree.heading('ID', text='ID')
        products_tree.heading('Название', text='Название')
        products_tree.heading('Категория', text='Категория')
        products_tree.heading('Цена', text='Цена')
        products_tree.heading('Количество', text='Количество')
        products_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Список для хранения полной информации о товарах
        available_products = []

        # Загрузка товаров из базы данных
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            p.Id_product, 
                            c.Name || ' ' || p.Id_product as product_name, 
                            c.Name as category, 
                            p.Price, 
                            pr.Quantity
                        FROM Product p
                        JOIN Category c ON p.Id_category = c.Id
                        JOIN Presence pr ON p.Id_product = pr.Id_product
                        JOIN Shop s ON pr.Id_shop = s.Id
                        WHERE pr.Quantity > 0
                    """)

                    products = cursor.fetchall()
                    available_products = products

                    for product in available_products:
                        products_tree.insert('', 'end', values=product)
        except Exception as e:
            import traceback
            print(f"Полная информация об ошибке: {e}")
            traceback.print_exc()
            messagebox.showerror("Ошибка", f"Не удалось загрузить товары: {e}")

        # Если список пуст, выводим сообщение
        if not available_products:
            messagebox.showwarning("Внимание", "Нет доступных товаров")

        # Фрейм для выбора товара и количества
        selection_frame = ttk.Frame(order_frame)
        selection_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(selection_frame, text="Выберите товар:").grid(row=0, column=0, padx=5, pady=5)

        # Комбобокс для выбора товара
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(selection_frame, textvariable=product_var, state="readonly")

        # Заполнение комбобокса названиями товаров
        product_combo['values'] = [f"{item[1]} (Цена: {item[3]})" for item in available_products]
        product_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(selection_frame, text="Количество:").grid(row=1, column=0, padx=5, pady=5)
        quantity_entry = ttk.Entry(selection_frame)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Список товаров в заказе
        order_tree = ttk.Treeview(order_frame,
                                  columns=('ID', 'Название', 'Категория', 'Цена', 'Количество', 'Сумма'),
                                  show='headings')
        order_tree.heading('ID', text='ID')
        order_tree.heading('Название', text='Название')
        order_tree.heading('Категория', text='Категория')
        order_tree.heading('Цена', text='Цена')
        order_tree.heading('Количество', text='Количество')
        order_tree.heading('Сумма', text='Сумма')
        order_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Метка для общей суммы
        total_var = tk.StringVar(value="Общая сумма: 0.00 руб.")
        ttk.Label(order_frame, textvariable=total_var, font=('Arial', 12)).pack(pady=5)

        # Кнопка добавления товара в заказ
        def add_to_order():
            try:
                # Проверяем выбран ли товар
                if not product_var.get():
                    messagebox.showerror("Ошибка", "Выберите товар")
                    return

                # Извлекаем название товара
                selected_product_name = product_var.get().split(" (")[0]

                # Находим выбранный товар в available_products
                selected_product = None
                for item in available_products:
                    if item[1] == selected_product_name:
                        selected_product = item
                        break

                if not selected_product:
                    messagebox.showerror("Ошибка", "Товар не найден")
                    return

                # Проверяем количество
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Ошибка", "Количество должно быть положительным")
                    return

                # Проверяем доступное количество
                if quantity > selected_product[4]:
                    messagebox.showerror("Ошибка", f"Недостаточно товара. Доступно: {selected_product[4]}")
                    return

                # Рассчитываем сумму
                total_price = float(selected_product[3]) * quantity

                # Добавляем товар в заказ
                order_tree.insert('', 'end', values=(
                    selected_product[0],  # ID
                    selected_product[1],  # Название
                    selected_product[2],  # Категория
                    selected_product[3],  # Цена
                    quantity,
                    round(total_price, 2)
                ))

                # Обновляем общую сумму
                current_total = float(total_var.get().split(": ")[1].replace(" руб.", ""))
                new_total = current_total + total_price
                total_var.set(f"Общая сумма: {new_total:.2f} руб.")

                # Очищаем поля ввода
                product_var.set('')
                quantity_entry.delete(0, tk.END)

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное количество")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        # Кнопка создания заказа
        def create_order():
            try:
                # Проверяем, есть ли товары в заказе
                order_items = order_tree.get_children()
                if not order_items:
                    messagebox.showerror("Ошибка", "Добавьте товары в заказ")
                    return

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Получаем ID пользователя
                        cursor.execute("SELECT get_user_id_by_role(%s)", (self.user_role,))
                        user_id = cursor.fetchone()[0]

                        # Создаем заказ
                        cursor.execute("CALL create_order(%s, %s)", (user_id, None))
                        cursor.execute("SELECT lastval()")  # Получаем ID созданного заказа
                        order_id = cursor.fetchone()[0]

                        # Добавляем товары в заказ
                        for item in order_items:
                            item_values = order_tree.item(item)['values']
                            product_id = item_values[0]
                            quantity = item_values[4]

                            cursor.execute(
                                "CALL add_order_item(%s, %s, %s)",
                                (order_id, product_id, quantity)
                            )

                        # Обновляем таблицу доступных товаров
                        products_tree.delete(*products_tree.get_children())
                        cursor.execute("SELECT * FROM get_available_products()")
                        updated_products = cursor.fetchall()

                        for product in updated_products:
                            products_tree.insert('', 'end', values=product)

                        # Очищаем таблицу заказа
                        order_tree.delete(*order_tree.get_children())

                        # Обновляем общую сумму
                        total_var.set("Общая сумма: 0.00 руб.")

                        conn.commit()
                        messagebox.showinfo("Успех", f"Заказ #{order_id} создан")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать заказ: {e}")

        # Кнопка удаления товара из заказа
        def remove_from_order():
            try:
                # Получаем выбранный элемент в таблице заказа
                selected_item = order_tree.selection()

                if not selected_item:
                    messagebox.showerror("Ошибка", "Выберите товар для удаления")
                    return

                # Получаем значения удаляемого товара
                item_values = order_tree.item(selected_item[0])['values']

                # Рассчитываем сумму удаляемого товара
                item_total = float(item_values[5])

                # Удаляем товар из таблицы
                order_tree.delete(selected_item[0])

                # Обновляем общую сумму
                current_total = float(total_var.get().split(": ")[1].replace(" руб.", ""))
                new_total = current_total - item_total
                total_var.set(f"Общая сумма: {new_total:.2f} руб.")

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        # Добавляем кнопку удаления в существующий код
        ttk.Button(selection_frame, text="Добавить в заказ", command=add_to_order).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(selection_frame, text="Удалить из заказа", command=remove_from_order).grid(row=2, column=1, padx=5,
                                                                                              pady=5)
        ttk.Button(selection_frame, text="Создать заказ", command=create_order).grid(row=2, column=2, padx=5, pady=5)

    def create_products_tab(self):
        """Создание вкладки товаров"""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Товары")

        # Таблица товаров
        self.products_tree = ttk.Treeview(products_frame,
                                          columns=('ID', 'Category', 'Price', 'Shop', 'Quantity'),
                                          show='headings'
                                          )
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Category', text='Категория')
        self.products_tree.heading('Price', text='Цена')
        self.products_tree.heading('Shop', text='Магазин')
        self.products_tree.heading('Quantity', text='Количество')
        self.products_tree.pack(expand=True, fill='both')

        # Загрузка товаров
        def load_products():
            """
            Внутренняя функция для загрузки списка товаров.
            Получает данные из БД и обновляет таблицу товаров.
            """
            try:
                # Очищаем текущие записи
                for item in self.products_tree.get_children():
                    self.products_tree.delete(item)

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Используем хранимую функцию
                        cursor.execute("SELECT * FROM get_products_list()")
                        products = cursor.fetchall()

                        if not products:
                            messagebox.showinfo("Информация", "Список товаров пуст")
                            return

                        # Заполняем таблицу
                        for product in products:
                            self.products_tree.insert('', 'end', values=product)

            except psycopg2.Error as e:
                messagebox.showerror("Ошибка базы данных", f"Не удалось загрузить товары: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")

        # Метод добавления товара
        def add_product():
            add_product_window = tk.Toplevel(self.root)
            add_product_window.title("Добавление товара")
            add_product_window.geometry("300x500")

            # Загрузка категорий и магазинов
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Загрузка категорий
                        cursor.execute("SELECT Name FROM Category")
                        categories = [cat[0] for cat in cursor.fetchall()]

                        # Загрузка магазинов
                        cursor.execute("SELECT Name FROM Shop")
                        shops = [shop[0] for shop in cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить справочники: {e}")
                categories = []
                shops = []

            # Поля ввода
            ttk.Label(add_product_window, text="Категория:").pack()
            category_var = tk.StringVar()
            category_combo = ttk.Combobox(add_product_window, textvariable=category_var, values=categories,
                                          state="readonly")
            category_combo.pack()

            ttk.Label(add_product_window, text="Цена:").pack()
            price_entry = ttk.Entry(add_product_window)
            price_entry.pack()

            ttk.Label(add_product_window, text="Магазин:").pack()
            shop_var = tk.StringVar()
            shop_combo = ttk.Combobox(add_product_window, textvariable=shop_var, values=shops, state="readonly")
            shop_combo.pack()

            ttk.Label(add_product_window, text="Количество:").pack()
            quantity_entry = ttk.Entry(add_product_window)
            quantity_entry.pack()

            def save_product():
                try:
                    # Проверка заполненности полей
                    if not all([category_var.get(), price_entry.get(), shop_var.get(), quantity_entry.get()]):
                        messagebox.showerror("Ошибка", "Заполните все поля")
                        return

                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Получаем ID категории
                            cursor.execute("SELECT Id FROM Category WHERE Name = %s", (category_var.get(),))
                            category_id = cursor.fetchone()[0]

                            # Добавляем продукт
                            cursor.execute("""
                                INSERT INTO Product (Price, Id_category) 
                                VALUES (%s, %s) 
                                RETURNING Id_product
                            """, (float(price_entry.get()), category_id))
                            product_id = cursor.fetchone()[0]

                            # Получаем ID магазина
                            cursor.execute("SELECT Id FROM Shop WHERE Name = %s", (shop_var.get(),))
                            shop_id = cursor.fetchone()[0]

                            # Добавляем наличие товара
                            cursor.execute("""
                                INSERT INTO Presence (Id_product, Id_shop, Quantity)
                                VALUES (%s, %s, %s)
                            """, (product_id, shop_id, int(quantity_entry.get())))

                            conn.commit()

                    # Обновляем список товаров
                    load_products()
                    add_product_window.destroy()
                    messagebox.showinfo("Успех", "Товар добавлен")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось добавить товар: {e}")

            ttk.Button(add_product_window, text="Сохранить", command=save_product).pack()

        # Метод редактирования товара
        def edit_product():
            selected_item = self.products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для редактирования")
                return

            # Получаем данные выбранного товара
            product_data = self.products_tree.item(selected_item[0])['values']

            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование товара")
            edit_window.geometry("300x500")

            # Загрузка категорий и магазинов
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Загрузка категорий
                        cursor.execute("SELECT Name FROM Category")
                        categories = [cat[0] for cat in cursor.fetchall()]

                        # Загрузка магазинов
                        cursor.execute("SELECT Name FROM Shop")
                        shops = [shop[0] for shop in cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить справочники: {e}")
                categories = []
                shops = []

            # Поля ввода
            ttk.Label(edit_window, text="Категория:").pack()
            category_var = tk.StringVar(value=product_data[1])
            category_combo = ttk.Combobox(edit_window, textvariable=category_var, values=categories, state="readonly")
            category_combo.pack()

            ttk.Label(edit_window, text="Цена:").pack()
            price_entry = ttk.Entry(edit_window)
            price_entry.insert(0, str(product_data[2]))
            price_entry.pack()

            ttk.Label(edit_window, text="Магазин:").pack()
            shop_var = tk.StringVar(value=product_data[3])
            shop_combo = ttk.Combobox(edit_window, textvariable=shop_var, values=shops, state="readonly")
            shop_combo.pack()

            ttk.Label(edit_window, text="Количество:").pack()
            quantity_entry = ttk.Entry(edit_window)
            quantity_entry.insert(0, str(product_data[4]))
            quantity_entry.pack()

            def save_edited_product():
                try:
                    # Проверка заполненности полей
                    if not all([category_var.get(), price_entry.get(), shop_var.get(), quantity_entry.get()]):
                        messagebox.showerror("Ошибка", "Заполните все поля")
                        return

                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Получаем ID категории
                            cursor.execute("SELECT Id FROM Category WHERE Name = %s", (category_var.get(),))
                            category_id = cursor.fetchone()[0]

                            # Обновляем продукт
                            cursor.execute("""
                                UPDATE Product 
                                SET Price = %s, Id_category = %s 
                                WHERE Id_product = %s
                            """, (float(price_entry.get()), category_id, product_data[0]))

                            # Получаем ID магазина
                            cursor.execute("SELECT Id FROM Shop WHERE Name = %s", (shop_var.get(),))
                            shop_id = cursor.fetchone()[0]

                            # Проверяем существование записи в Presence
                            cursor.execute("""
                                SELECT COUNT(*) 
                                FROM Presence 
                                WHERE Id_product = %s AND Id_shop = %s
                            """, (product_data[0], shop_id))
                            exists = cursor.fetchone()[0]

                            # Обновляем или вставляем наличие товара
                            if exists > 0:
                                cursor.execute("""
                                    UPDATE Presence 
                                    SET Quantity = %s 
                                    WHERE Id_product = %s AND Id_shop = %s
                                """, (int(quantity_entry.get()), product_data[0], shop_id))
                            else:
                                cursor.execute("""
                                    INSERT INTO Presence (Id_product, Id_shop, Quantity)
                                    VALUES (%s, %s, %s)
                                """, (product_data[0], shop_id, int(quantity_entry.get())))

                            conn.commit()

                        # Обновляем список товаров
                        load_products()
                        edit_window.destroy()
                        messagebox.showinfo("Успех", "Товар обновлен")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обновить товар: {e}")

            ttk.Button(edit_window, text="Сохранить", command=save_edited_product).pack()


        # Метод удаления товара
        def delete_product():
            selected_item = self.products_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите товар для удаления")
                return

            # Получаем ID товара
            product_data = self.products_tree.item(selected_item[0])['values']
            product_id = product_data[0]

            # Подтверждение удаления
            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить товар {product_data[1]}?"):
                try:
                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Проверяем, есть ли товар в заказах
                            cursor.execute("""
                                SELECT COUNT(*) 
                                FROM Order_items 
                                WHERE Id_product = %s
                            """, (product_id,))
                            order_count = cursor.fetchone()[0]

                            if order_count > 0:
                                messagebox.showerror("Ошибка",
                                                     f"Невозможно удалить товар. Товар участвует в {order_count} заказах.")
                                return

                            # Удаляем наличие товара
                            cursor.execute("DELETE FROM Presence WHERE Id_product = %s", (product_id,))

                            # Удаляем товар
                            cursor.execute("DELETE FROM Product WHERE Id_product = %s", (product_id,))

                            conn.commit()

                        # Обновляем список товаров
                        load_products()
                        messagebox.showinfo("Успех", "Товар удален")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить товар: {e}")

        # Кнопки управления товарами
        btn_frame = ttk.Frame(products_frame)
        btn_frame.pack(fill='x')

        # Доступ к управлению товарами только для Владельца и Администратора
        ttk.Button(btn_frame, text="Добавить товар", command=add_product).pack(side='left')
        ttk.Button(btn_frame, text="Редактировать товар", command=edit_product).pack(side='left')
        ttk.Button(btn_frame, text="Удалить товар", command=delete_product).pack(side='left')

        # Загружаем товары при создании вкладки
        load_products()

    def create_shops_tab(self):
        """Создание вкладки магазинов (только для Владельца)"""
        # Создаем фрейм для вкладки магазинов
        shops_frame = ttk.Frame(self.notebook)
        self.notebook.add(shops_frame, text="Магазины")

        # Создаем верхнюю панель для кнопок
        button_frame = ttk.Frame(shops_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        # Добавляем кнопки управления
        ttk.Button(button_frame, text="Добавить магазин", command=self.add_shop).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Редактировать магазин", command=self.edit_shop).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить магазин", command=self.delete_shop).pack(side='left', padx=5)

        # Создаем фрейм для таблицы
        tree_frame = ttk.Frame(shops_frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Создаем таблицу магазинов
        self.shops_tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Address', 'Manager'), show='headings')

        # Настраиваем заголовки столбцов
        self.shops_tree.heading('ID', text='ID')
        self.shops_tree.heading('Name', text='Название')
        self.shops_tree.heading('Address', text='Адрес')
        self.shops_tree.heading('Manager', text='Управляющий')

        # Настраиваем ширину столбцов
        self.shops_tree.column('ID', width=50, minwidth=50)
        self.shops_tree.column('Name', width=200, minwidth=100)
        self.shops_tree.column('Address', width=300, minwidth=150)
        self.shops_tree.column('Manager', width=150, minwidth=100)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.shops_tree.yview)
        self.shops_tree.configure(yscrollcommand=scrollbar.set)

        # Размещаем таблицу и полосу прокрутки
        self.shops_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Загружаем данные в таблицу
        self.load_shops_data()

        # Добавляем обработчик двойного клика
        self.shops_tree.bind('<Double-1>', lambda e: self.edit_shop())

        # Добавляем поиск
        search_frame = ttk.Frame(shops_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_shops)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)

    def search_shops(self, *args):
        """Поиск магазинов"""
        search_term = self.search_var.get().lower()
        pattern = f'%{search_term}%'
        self.shops_tree.delete(*self.shops_tree.get_children())

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM search_shops(%s, %s, %s)",
                                   (pattern, pattern, pattern))

                    for row in cursor.fetchall():
                        self.shops_tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске магазинов: {str(e)}")

    def refresh_shops_tab(self):
        """Обновление данных на вкладке магазинов"""
        self.search_var.set('')  # Сброс поиска
        self.load_shops_data()  # Перезагрузка данных

    def load_shops_data(self):
        """Загрузка данных о всех магазинах из БД"""
        self.shops_tree.delete(*self.shops_tree.get_children())
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM get_all_shops()")

                    shops = cursor.fetchall()
                    if not shops:
                        messagebox.showinfo("Информация", "Список магазинов пуст")
                        return

                    for row in shops:
                        self.shops_tree.insert('', 'end', values=row)

        except psycopg2.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Ошибка при загрузке данных: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")

    def get_managers(self):
        """Получение списка всех менеджеров через PostgreSQL функцию"""
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    # Вызываем функцию базы данных
                    cursor.execute("SELECT * FROM get_managers_list()")
                    return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении списка менеджеров: {str(e)}")
            return []

    def add_shop(self):
        """Диалог добавления нового магазина"""
        add_shop_window = tk.Toplevel(self.root)
        add_shop_window.title("Добавление магазина")
        add_shop_window.geometry("300x300")
        add_shop_window.grab_set()

        # Поля ввода
        ttk.Label(add_shop_window, text="Название магазина:").pack(pady=5)
        name_entry = ttk.Entry(add_shop_window)
        name_entry.pack(pady=5, padx=10, fill='x')

        ttk.Label(add_shop_window, text="Адрес:").pack(pady=5)
        address_entry = ttk.Entry(add_shop_window)
        address_entry.pack(pady=5, padx=10, fill='x')

        ttk.Label(add_shop_window, text="Управляющий:").pack(pady=5)

        # Получаем список менеджеров
        managers = self.get_managers()
        manager_dict = {manager[1]: manager[0] for manager in managers}

        manager_var = tk.StringVar()
        manager_combo = ttk.Combobox(add_shop_window,
                                     textvariable=manager_var,
                                     values=list(manager_dict.keys()),
                                     state='readonly')
        manager_combo.pack(pady=5, padx=10, fill='x')

        def save_shop():
            name = name_entry.get().strip()
            address = address_entry.get().strip()
            selected_manager = manager_var.get()

            if not all([name, address, selected_manager]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            try:
                manager_id = manager_dict[selected_manager]

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO shop (name, adress, id_user)
                            VALUES (%s, %s, %s)
                        """, (name, address, manager_id))

                self.load_shops_data()
                add_shop_window.destroy()
                messagebox.showinfo("Успех", "Магазин успешно добавлен")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении магазина: {str(e)}")

        ttk.Button(add_shop_window, text="Сохранить", command=save_shop).pack(pady=20)

    def edit_shop(self):
        """Редактирование магазина"""
        selected_item = self.shops_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите магазин для редактирования")
            return

        edit_shop_window = tk.Toplevel(self.root)
        edit_shop_window.title("Редактирование магазина")
        edit_shop_window.geometry("300x300")
        edit_shop_window.grab_set()

        current_values = self.shops_tree.item(selected_item)['values']
        shop_id = current_values[0]

        # Поля ввода
        ttk.Label(edit_shop_window, text="Название магазина:").pack(pady=5)
        name_entry = ttk.Entry(edit_shop_window)
        name_entry.insert(0, current_values[1])
        name_entry.pack(pady=5, padx=10, fill='x')

        ttk.Label(edit_shop_window, text="Адрес:").pack(pady=5)
        address_entry = ttk.Entry(edit_shop_window)
        address_entry.insert(0, current_values[2])
        address_entry.pack(pady=5, padx=10, fill='x')

        ttk.Label(edit_shop_window, text="Управляющий:").pack(pady=5)

        # Получаем список менеджеров
        managers = self.get_managers()
        manager_dict = {manager[1]: manager[0] for manager in managers}

        manager_var = tk.StringVar(value=current_values[3])
        manager_combo = ttk.Combobox(edit_shop_window,
                                     textvariable=manager_var,
                                     values=list(manager_dict.keys()),
                                     state='readonly')
        manager_combo.pack(pady=5, padx=10, fill='x')

        def save_edited_shop():
            name = name_entry.get().strip()
            address = address_entry.get().strip()
            selected_manager = manager_var.get()

            if not all([name, address, selected_manager]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            try:
                manager_id = manager_dict[selected_manager]

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            UPDATE shop 
                            SET name=%s, adress=%s, id_user=%s
                            WHERE id=%s
                        """, (name, address, manager_id, shop_id))

                self.load_shops_data()
                edit_shop_window.destroy()
                messagebox.showinfo("Успех", "Магазин успешно обновлен")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении магазина: {str(e)}")

        ttk.Button(edit_shop_window, text="Сохранить", command=save_edited_shop).pack(pady=20)

    def delete_shop(self):
        """Удаление выбранного магазина"""
        selected_item = self.shops_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите магазин для удаления")
            return

        shop_id = self.shops_tree.item(selected_item)['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот магазин?"):
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Проверка наличия товаров
                        cursor.execute("SELECT COUNT(*) FROM presence WHERE id_shop = %s", (shop_id,))
                        if cursor.fetchone()[0] > 0:
                            messagebox.showerror(
                                "Ошибка",
                                "Невозможно удалить магазин, так как в нем есть товары. "
                                "Сначала удалите все товары из магазина."
                            )
                            return

                        # Удаляем магазин
                        cursor.execute("DELETE FROM shop WHERE id = %s", (shop_id,))
                self.load_shops_data()
                messagebox.showinfo("Успех", "Магазин успешно удален")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении магазина: {str(e)}")

    def check_shop_exists(self, name, address, exclude_id=None):
        """Проверка существования магазина с таким же названием и адресом"""
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    if exclude_id:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM shop 
                            WHERE name = %s AND adress = %s AND id != %s
                        """, (name, address, exclude_id))
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM shop 
                            WHERE name = %s AND adress = %s
                        """, (name, address))
                    return cursor.fetchone()[0] > 0
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при проверке существования магазина: {str(e)}")
            return False

    def validate_shop_data(self, name, address, manager_id):
        """Валидация данных магазина"""
        if not name or not address or not manager_id:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return False

        if len(name) > 100:
            messagebox.showerror("Ошибка", "Название магазина слишком длинное (максимум 100 символов)")
            return False

        if len(address) > 255:
            messagebox.showerror("Ошибка", "Адрес слишком длинный (максимум 255 символов)")
            return False

        return True

    def refresh_shops_tab(self):
        """Обновление данных на вкладке магазинов"""
        self.load_shops_data()



    def create_users_tab(self):
        """Создание вкладки пользователей (только для Владельца и Администратора)"""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Пользователи")

        # Таблица пользователей
        self.users_tree = ttk.Treeview(users_frame, columns=('ID', 'Login', 'Role', 'Phone'), show='headings')
        self.users_tree.heading('ID', text='ID')
        self.users_tree.heading('Login', text='Логин')
        self.users_tree.heading('Role', text='Роль')
        self.users_tree.heading('Phone', text='Телефон')
        self.users_tree.pack(expand=True, fill='both')

        # Загрузка пользователей из базы данных
        def load_users():
            try:
                # Очищаем текущие записи
                for item in self.users_tree.get_children():
                    self.users_tree.delete(item)

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Вызываем функцию базы данных для получения пользователей
                        cursor.execute("SELECT * FROM get_all_users_with_roles()")
                        users = cursor.fetchall()

                        # Заполняем таблицу
                        for user in users:
                            self.users_tree.insert('', 'end', values=user)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")

        # Метод добавления пользователя
        def add_user():
            # Создаем диалоговое окно для ввода данных
            add_window = tk.Toplevel()
            add_window.title("Добавить пользователя")
            add_window.geometry("300x400")

            # Поля ввода
            ttk.Label(add_window, text="Логин:").pack()
            login_entry = ttk.Entry(add_window)
            login_entry.pack()

            ttk.Label(add_window, text="Пароль:").pack()
            password_entry = ttk.Entry(add_window, show="*")
            password_entry.pack()

            ttk.Label(add_window, text="Телефон:").pack()
            phone_entry = ttk.Entry(add_window)
            phone_entry.pack()

            ttk.Label(add_window, text="Роль:").pack()
            # Загружаем список ролей
            role_var = tk.StringVar()
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT Name FROM Role")
                        roles = [role[0] for role in cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить роли: {e}")
                roles = []

            role_combo = ttk.Combobox(add_window, textvariable=role_var, values=roles, state="readonly")
            role_combo.pack()

            # Функция сохранения нового пользователя
            def save_user():
                try:
                    login = login_entry.get()
                    password = password_entry.get()
                    phone = phone_entry.get()
                    role = role_var.get()

                    # Валидация данных
                    if not all([login, password, phone, role]):
                        messagebox.showerror("Ошибка", "Заполните все поля")
                        return

                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Получаем ID роли
                            cursor.execute("SELECT Id FROM Role WHERE Name = %s", (role,))
                            role_id = cursor.fetchone()[0]

                            # Добавляем пользователя
                            cursor.execute("""
                                INSERT INTO Users (Login, Password, RoleID, Phone)
                                VALUES (%s, %s, %s, %s)
                            """, (login, password, role_id, phone))

                            conn.commit()

                    # Обновляем список пользователей
                    load_users()
                    add_window.destroy()
                    messagebox.showinfo("Успех", "Пользователь добавлен")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}")

            # Кнопка сохранения
            ttk.Button(add_window, text="Сохранить", command=save_user).pack()

        # Метод редактирования пользователя
        def edit_user():
            # Получаем выбранного пользователя
            selected_item = self.users_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите пользователя для редактирования")
                return

            # Получаем данные выбранного пользователя
            user_data = self.users_tree.item(selected_item[0])['values']

            # Создаем диалоговое окно редактирования
            edit_window = tk.Toplevel()
            edit_window.title("Редактировать пользователя")
            edit_window.geometry("300x400")

            # Поля ввода с текущими значениями
            ttk.Label(edit_window, text="Логин:").pack()
            login_entry = ttk.Entry(edit_window)
            login_entry.insert(0, user_data[1])
            login_entry.pack()

            ttk.Label(edit_window, text="Новый пароль:").pack()
            password_entry = ttk.Entry(edit_window, show="*")
            password_entry.pack()

            ttk.Label(edit_window, text="Телефон:").pack()
            phone_entry = ttk.Entry(edit_window)
            phone_entry.insert(0, user_data[3])
            phone_entry.pack()

            ttk.Label(edit_window, text="Роль:").pack()
            # Загружаем список ролей
            role_var = tk.StringVar(value=user_data[2])
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT Name FROM Role")
                        roles = [role[0] for role in cursor.fetchall()]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить роли: {e}")
                roles = []

            role_combo = ttk.Combobox(edit_window, textvariable=role_var, values=roles, state="readonly")
            role_combo.pack()

            # Функция сохранения изменений
            def save_changes():
                try:
                    login = login_entry.get()
                    password = password_entry.get()
                    phone = phone_entry.get()
                    role = role_var.get()

                    # Валидация данных
                    if not all([login, phone, role]):
                        messagebox.showerror("Ошибка", "Заполните все поля")
                        return

                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Получаем ID роли
                            cursor.execute("SELECT Id FROM Role WHERE Name = %s", (role,))
                            role_id = cursor.fetchone()[0]

                            # Подготавливаем запрос на обновление
                            if password:  # Если пароль указан
                                cursor.execute("""
                                                UPDATE Users 
                                                SET Login = %s, 
                                                    Password = %s, 
                                                    RoleID = %s, 
                                                    Phone = %s
                                                WHERE Id_user = %s
                                            """, (login, password, role_id, phone, user_data[0]))
                            else:  # Если пароль не указан
                                cursor.execute("""
                                                UPDATE Users 
                                                SET Login = %s, 
                                                    RoleID = %s, 
                                                    Phone = %s
                                                WHERE Id_user = %s
                                            """, (login, role_id, phone, user_data[0]))

                            conn.commit()

                            # Обновляем список пользователей
                        load_users()
                        edit_window.destroy()
                        messagebox.showinfo("Успех", "Пользователь обновлен")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обновить пользователя: {e}")

            # Кнопка сохранения
            ttk.Button(edit_window, text="Сохранить", command=save_changes).pack()

        # Метод удаления пользователя
        def delete_user():
            # Получаем выбранного пользователя
            selected_item = self.users_tree.selection()
            if not selected_item:
                messagebox.showerror("Ошибка", "Выберите пользователя для удаления")
                return

            # Получаем ID пользователя
            user_data = self.users_tree.item(selected_item[0])['values']
            user_id = user_data[0]

            # Подтверждение удаления
            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя {user_data[1]}?"):
                try:
                    with self.db.connect() as conn:
                        with conn.cursor() as cursor:
                            # Удаляем пользователя
                            cursor.execute("DELETE FROM Users WHERE Id_user = %s", (user_id,))
                            conn.commit()

                    # Обновляем список пользователей
                    load_users()
                    messagebox.showinfo("Успех", "Пользователь удален")

                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {e}")

        # Кнопки управления пользователями
        btn_frame = ttk.Frame(users_frame)
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame, text="Добавить пользователя", command=add_user).pack(side='left')
        ttk.Button(btn_frame, text="Редактировать пользователя", command=edit_user).pack(side='left')
        ttk.Button(btn_frame, text="Удалить пользователя", command=delete_user).pack(side='left')

        # Загружаем пользователей при создании вкладки
        load_users()

    def add_user(self):
        """Диалог добавления нового пользователя"""
        add_user_window = tk.Toplevel(self.root)
        add_user_window.title("Добавление пользователя")
        add_user_window.geometry("300x400")

        # Поля ввода
        ttk.Label(add_user_window, text="Логин:").pack()
        login_entry = ttk.Entry(add_user_window)
        login_entry.pack()

        ttk.Label(add_user_window, text="Пароль:").pack()
        password_entry = ttk.Entry(add_user_window, show="*")
        password_entry.pack()

        ttk.Label(add_user_window, text="Роль:").pack()
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(add_user_window, textvariable=role_var)
        role_combo['values'] = ['Владелец', 'Администратор', 'Покупатель']
        role_combo.pack()

        ttk.Label(add_user_window, text="Телефон:").pack()
        phone_entry = ttk.Entry(add_user_window)
        phone_entry.pack()

        ttk.Label(add_user_window, text="Email:").pack()
        email_entry = ttk.Entry(add_user_window)
        email_entry.pack()

        def save_user():
            # Проверка заполненности полей
            if not all([login_entry.get(), password_entry.get(), role_var.get(),
                        phone_entry.get(), email_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Добавление пользователя в таблицу
            self.users_tree.insert('', 'end', values=(
                login_entry.get(),
                role_var.get(),
                phone_entry.get(),
                email_entry.get()
            ))
            add_user_window.destroy()

        ttk.Button(add_user_window, text="Сохранить", command=save_user).pack()

    def edit_user(self):
        """Редактирование пользователя"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите пользователя для редактирования")
            return

        edit_user_window = tk.Toplevel(self.root)
        edit_user_window.title("Редактирование пользователя")
        edit_user_window.geometry("300x400")

        # Получаем текущие значения
        current_values = self.users_tree.item(selected_item)['values']

        # Поля ввода
        ttk.Label(edit_user_window, text="Логин:").pack()
        login_entry = ttk.Entry(edit_user_window)
        login_entry.insert(0, current_values[0])
        login_entry.pack()

        ttk.Label(edit_user_window, text="Новый пароль:").pack()
        password_entry = ttk.Entry(edit_user_window, show="*")
        password_entry.pack()

        ttk.Label(edit_user_window, text="Роль:").pack()
        role_var = tk.StringVar(value=current_values[1])
        role_combo = ttk.Combobox(edit_user_window, textvariable=role_var)
        role_combo['values'] = ['Владелец', 'Администратор', 'Покупатель']
        role_combo.pack()

        ttk.Label(edit_user_window, text="Телефон:").pack()
        phone_entry = ttk.Entry(edit_user_window)
        phone_entry.insert(0, current_values[2])
        phone_entry.pack()

        ttk.Label(edit_user_window, text="Email:").pack()
        email_entry = ttk.Entry(edit_user_window)
        email_entry.insert(0, current_values[3])
        email_entry.pack()

        def save_edited_user():
            # Проверка заполненности полей
            if not all([login_entry.get(), role_var.get(),
                        phone_entry.get(), email_entry.get()]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Обновление пользователя в таблице
            self.users_tree.item(selected_item, values=(
                login_entry.get(),
                role_var.get(),
                phone_entry.get(),
                email_entry.get()
            ))
            edit_user_window.destroy()

        ttk.Button(edit_user_window, text="Сохранить", command=save_edited_user).pack()

    def delete_user(self):
        """Удаление выбранного пользователя"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления")
            return

        self.users_tree.delete(selected_item)

    def create_orders_tab(self):
        """Создание вкладки заказов"""
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text="Заказы")

        # Создаем основной фрейм с разделением
        main_frame = ttk.Frame(orders_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая часть - список заказов
        orders_list_frame = ttk.Frame(main_frame)
        orders_list_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        ttk.Label(orders_list_frame, text="Список заказов", font=('Arial', 12)).pack(pady=5)

        # Обертка для списка заказов
        orders_list_frame_wrapper = ttk.Frame(orders_list_frame)
        orders_list_frame_wrapper.pack(fill='both', expand=True)

        # Таблица заказов
        self.orders_tree = ttk.Treeview(orders_list_frame_wrapper,
                                        columns=('ID', 'Дата', 'Статус', 'Количество товаров', 'Сумма'),
                                        show='headings')

        # Скроллбары для списка заказов
        self.orders_list_scrollbar_y = ttk.Scrollbar(orders_list_frame_wrapper, orient='vertical',
                                                     command=self.orders_tree.yview)
        self.orders_list_scrollbar_x = ttk.Scrollbar(orders_list_frame_wrapper, orient='horizontal',
                                                     command=self.orders_tree.xview)

        # Конфигурация скроллбаров
        self.orders_tree.configure(yscrollcommand=self.orders_list_scrollbar_y.set,
                                   xscrollcommand=self.orders_list_scrollbar_x.set)

        # Размещение элементов
        self.orders_list_scrollbar_y.pack(side='right', fill='y')
        self.orders_list_scrollbar_x.pack(side='bottom', fill='x')
        self.orders_tree.pack(side='left', fill='both', expand=True)

        # Настройка заголовков
        self.orders_tree.heading('ID', text='ID')
        self.orders_tree.heading('Дата', text='Дата')
        self.orders_tree.heading('Статус', text='Статус')
        self.orders_tree.heading('Количество товаров', text='Количество товаров')
        self.orders_tree.heading('Сумма', text='Сумма')

        # Правая часть - детали заказа
        order_details_frame = ttk.Frame(main_frame)
        order_details_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        ttk.Label(order_details_frame, text="Детали заказа", font=('Arial', 12)).pack(pady=5)

        # Обертка для деталей заказа
        order_details_frame_wrapper = ttk.Frame(order_details_frame)
        order_details_frame_wrapper.pack(fill='both', expand=True)

        # Таблица деталей заказа
        self.order_details_tree = ttk.Treeview(order_details_frame_wrapper,
                                               columns=('Товар', 'Категория', 'Цена', 'Количество', 'Сумма'),
                                               show='headings')

        # Скроллбары для деталей заказа
        self.order_details_scrollbar_y = ttk.Scrollbar(order_details_frame_wrapper, orient='vertical',
                                                       command=self.order_details_tree.yview)
        self.order_details_scrollbar_x = ttk.Scrollbar(order_details_frame_wrapper, orient='horizontal',
                                                       command=self.order_details_tree.xview)

        # Конфигурация скроллбаров
        self.order_details_tree.configure(yscrollcommand=self.order_details_scrollbar_y.set,
                                          xscrollcommand=self.order_details_scrollbar_x.set)

        # Размещение элементов
        self.order_details_scrollbar_y.pack(side='right', fill='y')
        self.order_details_scrollbar_x.pack(side='bottom', fill='x')
        self.order_details_tree.pack(side='left', fill='both', expand=True)

        # Настройка заголовков
        self.order_details_tree.heading('Товар', text='Товар')
        self.order_details_tree.heading('Категория', text='Категория')
        self.order_details_tree.heading('Цена', text='Цена')
        self.order_details_tree.heading('Количество', text='Количество')
        self.order_details_tree.heading('Сумма', text='Сумма')

        # Функция загрузки заказов
        def load_orders():
            try:
                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        # Проверяем роль пользователя
                        if self.user_role in ['Администратор', 'Менеджер магазина']:
                            cursor.execute("""
                                SELECT 
                                    o.Id, 
                                    o.Date, 
                                    o.Status, 
                                    COUNT(oi.Id) as items_count,
                                    SUM(oi.Quantity * p.Price) as total_sum,
                                    u.Login as user_login
                                FROM Orders o
                                LEFT JOIN Order_items oi ON o.Id = oi.Id_order
                                LEFT JOIN Product p ON oi.Id_product = p.Id_product
                                JOIN Users u ON o.Id_user = u.Id_user
                                GROUP BY o.Id, o.Date, o.Status, u.Login
                                ORDER BY o.Date DESC
                            """)
                        else:
                            cursor.execute("""
                                SELECT 
                                    o.Id, 
                                    o.Date, 
                                    o.Status, 
                                    COUNT(oi.Id) as items_count,
                                    SUM(oi.Quantity * p.Price) as total_sum
                                FROM Orders o
                                LEFT JOIN Order_items oi ON o.Id = oi.Id_order
                                LEFT JOIN Product p ON oi.Id_product = p.Id_product
                                WHERE o.Id_user = %s
                                GROUP BY o.Id, o.Date, o.Status
                                ORDER BY o.Date DESC
                            """, (self.user_id,))

                        orders = cursor.fetchall()

                        for i in self.orders_tree.get_children():
                            self.orders_tree.delete(i)

                        # Обновляем столбцы, если это администратор или менеджер
                        if self.user_role in ['Администратор', 'Менеджер магазина']:
                            self.orders_tree['columns'] = (
                            'ID', 'Дата', 'Статус', 'Количество товаров', 'Сумма', 'Пользователь')
                            self.orders_tree.heading('Пользователь', text='Пользователь')
                            self.orders_tree.column('Пользователь', width=100, minwidth=100)

                            # Настройка ширины столбцов
                            self.orders_tree.column('ID', width=50, minwidth=50)
                            self.orders_tree.column('Дата', width=100, minwidth=100)
                            self.orders_tree.column('Статус', width=100, minwidth=100)
                            self.orders_tree.column('Количество товаров', width=150, minwidth=150)
                            self.orders_tree.column('Сумма', width=100, minwidth=100)
                            self.orders_tree.column('Пользователь', width=100, minwidth=100)

                        for order in orders:
                            self.orders_tree.insert('', 'end', values=order)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {e}")

        def load_order_details(event):
            try:
                selected_item = self.orders_tree.selection()
                if not selected_item:
                    return

                order_id = self.orders_tree.item(selected_item)['values'][0]

                with self.db.connect() as conn:
                    with conn.cursor() as cursor:
                        if self.user_role in ['Администратор', 'Менеджер магазина']:
                            cursor.execute("""
                                SELECT 
                                    p.Id_product,
                                    c.Name as category,
                                    p.Price,
                                    oi.Quantity,
                                    (p.Price * oi.Quantity) as total_sum
                                FROM Order_items oi
                                JOIN Product p ON oi.Id_product = p.Id_product
                                JOIN Category c ON p.Id_category = c.Id
                                WHERE oi.Id_order = %s
                            """, (order_id,))
                        else:
                            cursor.execute("""
                                SELECT Id_user 
                                FROM Users 
                                WHERE Login = (
                                    SELECT Login 
                                    FROM Users u
                                    JOIN Role r ON u.RoleID = r.Id 
                                    WHERE r.Name = %s 
                                    LIMIT 1
                                )
                            """, (self.user_role,))

                            user_id = cursor.fetchone()

                            if not user_id:
                                messagebox.showinfo("Информация", "Пользователь не найден")
                                return

                            # Проверяем, что заказ принадлежит текущему пользователю
                            cursor.execute("""
                                SELECT COUNT(*) 
                                FROM Orders 
                                WHERE Id = %s AND Id_user = %s
                            """, (order_id, user_id[0]))

                            if cursor.fetchone()[0] == 0:
                                messagebox.showwarning("Предупреждение", "Доступ к заказу запрещен")
                                return

                            # Загружаем детали заказа
                            cursor.execute("""
                                SELECT 
                                    p.Id_product,
                                    c.Name as category,
                                    p.Price,
                                    oi.Quantity,
                                    (p.Price * oi.Quantity) as total_sum
                                FROM Order_items oi
                                JOIN Product p ON oi.Id_product = p.Id_product
                                JOIN Category c ON p.Id_category = c.Id
                                WHERE oi.Id_order = %s
                            """, (order_id,))

                        order_details = cursor.fetchall()

                        for i in self.order_details_tree.get_children():
                            self.order_details_tree.delete(i)

                        for detail in order_details:
                            self.order_details_tree.insert('', 'end', values=detail)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить детали заказа: {e}")

        # Привязываем событие выбора заказа
        self.orders_tree.bind('<<TreeviewSelect>>', load_order_details)

        # Кнопка обновления списка заказов
        refresh_button = ttk.Button(orders_frame, text="Обновить список", command=load_orders)
        refresh_button.pack(side='bottom', pady=5)

        # Настройка ширины столбцов для таблицы заказов
        self.orders_tree.column('ID', width=50, minwidth=50)
        self.orders_tree.column('Дата', width=100, minwidth=100)
        self.orders_tree.column('Статус', width=100, minwidth=100)
        self.orders_tree.column('Количество товаров', width=150, minwidth=150)
        self.orders_tree.column('Сумма', width=100, minwidth=100)

        # Настройка ширины столбцов для таблицы деталей заказа
        self.order_details_tree.column('Товар', width=150, minwidth=150)
        self.order_details_tree.column('Категория', width=100, minwidth=100)
        self.order_details_tree.column('Цена', width=100, minwidth=100)
        self.order_details_tree.column('Количество', width=100, minwidth=100)
        self.order_details_tree.column('Сумма', width=100, minwidth=100)

        # Загружаем заказы при создании вкладки
        load_orders()

    def create_order(self):
        """Создание нового заказа"""
        create_order_window = tk.Toplevel(self.root)
        create_order_window.title("Создание заказа")
        create_order_window.geometry("500x600")

        # Список товаров
        ttk.Label(create_order_window, text="Список товаров:").pack()
        products_tree = ttk.Treeview(create_order_window,
                                     columns=('Product', 'Price', 'Quantity'),
                                     show='headings'
                                     )
        products_tree.heading('Product', text='Товар')
        products_tree.heading('Price', text='Цена')
        products_tree.heading('Quantity', text='Количество')
        products_tree.pack(expand=True, fill='both')

        # Добавление товара в заказ
        ttk.Label(create_order_window, text="Добавление товара:").pack()

        ttk.Label(create_order_window, text="Товар:").pack()
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(create_order_window, textvariable=product_var)
        product_combo['values'] = ['Ноутбук', 'Смартфон', 'Планшет']
        product_combo.pack()

        ttk.Label(create_order_window, text="Количество:").pack()
        quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(create_order_window, textvariable=quantity_var)
        quantity_entry.pack()

        def add_product_to_order():
            if not product_var.get() or not quantity_var.get():
                messagebox.showerror("Ошибка", "Выберите товар и количество")
                return

            # Условная цена товара
            prices = {'Ноутбук': 1000, 'Смартфон': 500, 'Планшет': 300}
            price = prices.get(product_var.get(), 0)

            products_tree.insert('', 'end', values=(
                product_var.get(),
                price,
                quantity_var.get()
            ))

            # Очистка полей
            product_var.set('')
            quantity_var.set('')

        def save_order():
            # Проверка наличия товаров в заказе
            if len(products_tree.get_children()) == 0:
                messagebox.showerror("Ошибка", "Добавьте товары в заказ")
                return

            # Расчет общей суммы
            total = sum(float(products_tree.item(item)['values'][1]) * int(products_tree.item(item)['values'][2])
                        for item in products_tree.get_children())

            # Добавление заказа в таблицу
            self.orders_tree.insert('', 'end', values=(
                self.user_role,  # Пользователь
                tk.simpledialog.askstring("Дата", "Введите дату заказа:"),
                'Новый',
                total
            ))

            create_order_window.destroy()

        ttk.Button(create_order_window, text="Добавить товар", command=add_product_to_order).pack()
        ttk.Button(create_order_window, text="Сохранить заказ", command=save_order).pack()

    def change_order_status(self):
        """Изменение статуса заказа"""
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите заказ")
            return

        status_window = tk.Toplevel(self.root)
        status_window.title("Изменение статуса")
        status_window.geometry("300x200")

        ttk.Label(status_window, text="Новый статус:").pack()
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_window, textvariable=status_var)
        status_combo['values'] = ['Новый', 'В обработке', 'Отправлен', 'Доставлен', 'Отменен']
        status_combo.pack()

        def update_status():
            if not status_var.get():
                messagebox.showerror("Ошибка", "Выберите статус")
                return

            # Обновление статуса в таблице
            current_values = list(self.orders_tree.item(selected_item)['values'])
            current_values[2] = status_var.get()
            self.orders_tree.item(selected_item, values=current_values)

            status_window.destroy()

        ttk.Button(status_window, text="Сохранить", command=update_status).pack()

    def view_order_details(self):
        """Просмотр деталей заказа"""
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите заказ")
            return

        details_window = tk.Toplevel(self.root)
        details_window.title("Детали заказа")
        details_window.geometry("400x300")

        # Отображение информации о заказе
        order_info = self.orders_tree.item(selected_item)['values']

        details_frame = ttk.Frame(details_window)
        details_frame.pack(padx=10, pady=10)

        info_labels = [
            f"Пользователь: {order_info[0]}",
            f"Дата: {order_info[1]}",
            f"Статус: {order_info[2]}",
            f"Общая сумма: {order_info[3]}"
        ]

        for label_text in info_labels:
            ttk.Label(details_frame, text=label_text).pack(anchor='w')

        # Таблица товаров в заказе
        items_tree = ttk.Treeview(details_window,
                                  columns=('Product', 'Price', 'Quantity', 'Total'),
                                  show='headings'
                                  )
        items_tree.heading('Product', text='Товар')
        items_tree.heading('Price', text='Цена')
        items_tree.heading('Quantity', text='Количество')
        items_tree.heading('Total', text='Сумма')
        items_tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Заглушка для товаров
        sample_items = [
            ('Ноутбук', 1000, 1, 1000),
            ('Смартфон', 500, 2, 1000)
        ]

        for item in sample_items:
            items_tree.insert('', 'end', values=item)

    def create_reports_tab(self):
        """Создание вкладки отчетов (только для Владельца)"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Отчеты")

        # Кнопки генерации отчетов
        btn_frame = ttk.Frame(reports_frame)
        btn_frame.pack(fill='x')

        report_types = [
            ("Отчет о продажах", self.generate_sales_report),
            ("Отчет о наличии товаров", self.generate_inventory_report),
            ("Финансовый отчет", self.generate_financial_report)
        ]

        for report_name, report_func in report_types:
            ttk.Button(btn_frame, text=report_name, command=report_func).pack(side='left', padx=5)

        # Область отображения отчета
        self.report_text = tk.Text(reports_frame, height=20, width=80)
        self.report_text.pack(expand=True, fill='both', padx=10, pady=10)

    def generate_sales_report(self):
        """Генерация отчета о продажах"""
        self.report_text.delete(1.0, tk.END)

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    # Проверяем количество выполненных заказов
                    cursor.execute(
                        "SELECT count_completed_orders(%s)",
                        (self.user_id,)
                    )
                    delivered_count = cursor.fetchone()[0]

                    if delivered_count == 0:
                        self.report_text.insert(tk.END, "Нет выполненных заказов в системе.")
                        return

                    # Получаем данные о продажах
                    cursor.execute(
                        "SELECT * FROM generate_sales_report_by_user(%s)",
                        (self.user_id,)
                    )
                    sales_data = cursor.fetchall()

                    # Проверяем права доступа и наличие данных
                    if not sales_data or sales_data[0][0] is None:
                        self.report_text.insert(tk.END, "Недостаточно прав для просмотра отчета.")
                        return

                    # Формируем отчет
                    report = "Отчет о продажах:\n\n"
                    report += "Пользователь | Количество заказов | Общая сумма\n"
                    report += "-" * 50 + "\n"

                    total_orders = 0
                    total_sales = 0.0

                    for login, order_count, total_amount in sales_data:
                        if total_amount > 0:
                            # Преобразуем Decimal в float для совместимости
                            total_amount_float = float(total_amount)
                            report += f"{login:<20} | {order_count:<18} | {total_amount_float:.2f} руб.\n"
                            total_orders += order_count
                            total_sales += total_amount_float

                    # Добавляем итоговую строку
                    report += "-" * 50 + "\n"
                    report += f"{'Итого:':<20} | {total_orders:<18} | {total_sales:.2f} руб.\n"

                    if report.count('\n') <= 3:
                        report += "Нет данных о продажах.\n"

                    # Вставляем отчет
                    self.report_text.insert(tk.END, report)

                    # Добавляем отладочную информацию
                    debug_info = "\n\nОтладочная информация:\n"
                    debug_info += f"Количество выполненных заказов: {delivered_count}\n"
                    debug_info += f"Количество записей в отчете: {len(sales_data)}\n"
                    debug_info += f"Роль пользователя: {self.user_role}\n"
                    self.report_text.insert(tk.END, debug_info)

        except Exception as e:
            error_message = f"Ошибка при генерации отчета о продажах: {str(e)}"
            messagebox.showerror("Ошибка", error_message)
            self.report_text.insert(tk.END, f"\nДетали ошибки:\n{error_message}")

    def generate_inventory_report(self):
        """Генерация отчета о наличии товаров"""
        self.report_text.delete(1.0, tk.END)

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    # Получаем данные о наличии товаров с учетом роли
                    cursor.execute(
                        "SELECT * FROM generate_inventory_report_by_user(%s)",
                        (self.user_id,)
                    )
                    inventory_data = cursor.fetchall()

                    # Проверяем права доступа и наличие данных
                    if not inventory_data or inventory_data[0][0] is None:
                        self.report_text.insert(tk.END, "Недостаточно прав для просмотра отчета.")
                        return

                    report = "Отчет о наличии товаров:\n\n"
                    report += "Категория | Магазин | Кол-во товаров | Общее количество\n"
                    report += "-" * 65 + "\n"

                    # Переменные для итоговой строки
                    total_product_count = 0
                    total_quantity = 0

                    for category, shop, product_count, quantity in inventory_data:
                        report += f"{category:<15} | {shop:<15} | {product_count:<14} | {quantity}\n"
                        total_product_count += product_count
                        total_quantity += quantity

                    # Добавляем итоговую строку
                    report += "-" * 65 + "\n"
                    report += f"{'Итого:':<15} | {'Все магазины':<15} | {total_product_count:<14} | {total_quantity}\n"

                    self.report_text.insert(tk.END, report)

                    # Добавляем отладочную информацию
                    debug_info = "\n\nОтладочная информация:\n"
                    debug_info += f"Количество записей в отчете: {len(inventory_data)}\n"
                    debug_info += f"Роль пользователя: {self.user_role}\n"
                    self.report_text.insert(tk.END, debug_info)

        except Exception as e:
            error_message = f"Ошибка при генерации отчета о наличии: {str(e)}"
            messagebox.showerror("Ошибка", error_message)
            self.report_text.insert(tk.END, f"\nДетали ошибки:\n{error_message}")

    def generate_financial_report(self):
        """Генерация финансового отчета"""
        self.report_text.delete(1.0, tk.END)

        try:
            with self.db.connect() as conn:
                with conn.cursor() as cursor:
                    # Получаем финансовые данные с учетом роли
                    cursor.execute(
                        "SELECT * FROM generate_financial_report_by_user(%s)",
                        (self.user_id,)
                    )
                    financial_data = cursor.fetchone()

                    # Формируем текстовый отчет
                    report = "Финансовый отчет:\n\n"
                    report += f"Общее количество заказов: {financial_data[0]}\n"
                    report += f"Общая выручка: {financial_data[1]:.2f} руб.\n"
                    report += f"Всего продано товаров: {financial_data[2]} шт.\n"
                    report += f"Средний чек: {financial_data[3]:.2f} руб.\n\n"

                    # Добавляем топ-категории
                    report += "Топ-5 категорий по выручке:\n"
                    report += "-" * 50 + "\n"
                    report += financial_data[4] + "\n"

                    # Добавляем отладочную информацию
                    debug_info = "\n\nОтладочная информация:\n"
                    debug_info += f"Роль пользователя: {self.user_role}\n"
                    debug_info += f"Количество заказов: {financial_data[0]}\n"

                    # Вставляем отчет
                    self.report_text.insert(tk.END, report)
                    self.report_text.insert(tk.END, debug_info)

        except Exception as e:
            error_message = f"Ошибка при генерации финансового отчета: {str(e)}"
            messagebox.showerror("Ошибка", error_message)
            self.report_text.insert(tk.END, f"\nДетали ошибки:\n{error_message}")