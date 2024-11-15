import sqlite3

# Создаем или подключаемся к базе данных
connection = sqlite3.connect('data.db')

# Создаем курсор для выполнения SQL-запросов
cursor = connection.cursor()

# Создаем таблицу факультетов
cursor.execute('''
CREATE TABLE IF NOT EXISTS faculties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')


# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

print("База данных и таблица успешно созданы!")