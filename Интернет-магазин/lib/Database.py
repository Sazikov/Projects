import psycopg2
from datetime import date
from decimal import Decimal

class DatabaseManager:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    def connect(self):
        return psycopg2.connect(**self.connection_params)


    def get_role_id(self, role_name):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM Role WHERE name = %s", (role_name,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Ошибка получения ID роли: {e}")
            return None

    def add_user(self, login, password, role_name, phone):
        role_id = self.get_role_id(role_name)

        if role_id is None:
            print(f"Роль '{role_name}' не найдена")
            return None

        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    # Проверка уникальности логина
                    cursor.execute("SELECT * FROM users WHERE login = %s", (login,))
                    if cursor.fetchone():
                        return None

                    cursor.execute("""
                        INSERT INTO users (login, password, roleid, phone) 
                        VALUES (%s, %s, %s, %s)
                    """, (login, password, role_id, phone))

                    conn.commit()

                    return True

        except psycopg2.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None

    def authenticate_user(self, login, password):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM authenticate_user(%s, %s)
                    """, (login, password))

                    user = cursor.fetchone()
                    return user

        except psycopg2.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None

