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

cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS raspisanie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    time TEXT NOT NULL,
    subject TEXT NOT NULL,
    teacher_name TEXT NOT NULL,
    video_link TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id)
)
''')


               
# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()

print("База данных и таблица успешно созданы!")