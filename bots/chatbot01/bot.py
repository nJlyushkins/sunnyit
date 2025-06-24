# В файле bot.py
import sqlite3
import json
import sys
import os

# Абсолютный путь к базе данных (замените на реальный путь)
DB_PATH = r'C:\Users\Андрей\Documents\Projects\Django\sunnyit\bots\chatbot01\users.db'  # Укажите правильный путь
TOKEN = "vk1.a.MU-ccGdPVTQBG1PG7jsf41YF1qySzw_wuMlO3WAAoTREqq1fFSDF0Ur2PaqJbYCbnyW_3UFQKJafVixAZL8EdU7APTvJNr73zsbQ2p3kBbhULj6EpfFp9eUU73K2mVULFO6U9zmWmC1VojpxcScOB46O-ZKck9Q4kr7EgxDqep4_S0KaBEXeKYtzB5RnPZjyl0JxSgBx2sH6tPovZQ0GxQ"

def get_users_with_states():
    """Возвращает список пользователей с их состояниями."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT u.id, u.vk_id, u.full_name, s.name FROM Users u JOIN States s ON u.state = s.id')
        users = cursor.fetchall()
        return [{'id': user[0], 'vk_id': user[1], 'full_name': user[2], 'state': user[3]} for user in users]
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()

def get_states_description():
    """Возвращает описание всех состояний."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, name FROM States')
        states = cursor.fetchall()
        return [{'id': state[0], 'name': state[1]} for state in states]
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()

def get_messages():
    """Возвращает список всех сообщений с их медиа."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT m.id, m.text, m.state_id, s.name FROM Messages m JOIN States s ON m.state_id = s.id')
        messages = cursor.fetchall()
        cursor.execute('SELECT id, message_id, type, url FROM Media')
        media = {row[1]: {'type': row[2], 'url': row[3]} for row in cursor.fetchall()}
        result = []
        for msg in messages:
            msg_data = {
                'id': msg[0],
                'text': msg[1],
                'state_id': msg[2],
                'state_name': msg[3],
                'media': [media.get(msg[0], {}) for _ in range(5)]  # До 5 медиа-файлов
            }
            result.append(msg_data)
        return result
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []
    finally:
        conn.close()

def get_message_by_id(message_id):
    """Возвращает сообщение по его ID с медиа."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT m.id, m.text, m.state_id, s.name FROM Messages m JOIN States s ON m.state_id = s.id WHERE m.id = ?', (message_id,))
        message = cursor.fetchone()
        if not message:
            return {'success': False, 'error': f'Message with ID {message_id} not found'}
        cursor.execute('SELECT id, type, url FROM Media WHERE message_id = ?', (message_id,))
        media = [{'id': row[0], 'type': row[1], 'url': row[2]} for row in cursor.fetchall()[:5]]  # До 5 медиа
        return {
            'success': True,
            'data': {
                'id': message[0],
                'text': message[1],
                'state_id': message[2],
                'state_name': message[3],
                'media': media
            }
        }
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def update_message(message_id, text, state_id):
    """Обновляет текст и состояние сообщения."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Messages SET text = ?, state_id = ? WHERE id = ?', (text, state_id, message_id))
        conn.commit()
        return {'success': True, 'message': f'Message {message_id} updated'}
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def add_message(text, state_id):
    """Добавляет новое сообщение."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Messages (text, state_id) VALUES (?, ?)', (text, state_id))
        message_id = cursor.lastrowid
        conn.commit()
        return {'success': True, 'message_id': message_id}
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def add_media(message_id, media_type, url):
    """Добавляет медиа к сообщению (до 5 штук)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM Media WHERE message_id = ?', (message_id,))
        if cursor.fetchone()[0] >= 5:
            return {'success': False, 'error': 'Maximum 5 media items allowed'}
        cursor.execute('INSERT INTO Media (message_id, type, url) VALUES (?, ?, ?)', (message_id, media_type, url))
        conn.commit()
        return {'success': True, 'media_id': cursor.lastrowid}
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def add_user(vk_id, full_name, state_id):
    """Добавляет нового пользователя в базу данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT OR IGNORE INTO Users (vk_id, full_name, state) VALUES (?, ?, ?)', (vk_id, full_name, state_id))
        conn.commit()
        return {'success': True, 'message': f'User {vk_id} added'}
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}", file=sys.stderr)
        return {'success': False, 'error': str(e)}
    finally:
        conn.close()

def handle_event(event_data):
    """Обрабатывает входящее событие от VK и возвращает заглушку как ответ."""
    print(f"Received event: {json.dumps(event_data)}")  # Для отладки
    if event_data.get('type') == 'message_new':
        user_id = event_data.get('object', {}).get('message', {}).get('from_id')
        text = event_data.get('object', {}).get('message', {}).get('text', '')
        if user_id:
            # Добавляем пользователя, если его нет
            add_user(user_id, 'Unknown User', 1)  # Состояние по умолчанию
            # Заглушка ответа (замените на реальную логику)
            return {'response': f"Заглушка ответа на сообщение: {text}"}
    return {'response': 'Заглушка для других событий'}

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'get_users':
                print(json.dumps(get_users_with_states()))
            elif sys.argv[1] == 'get_states':
                print(json.dumps(get_states_description()))
            elif sys.argv[1] == 'get_messages':
                print(json.dumps(get_messages()))
            elif sys.argv[1] == 'get_message_by_id' and len(sys.argv) == 3:
                print(json.dumps(get_message_by_id(int(sys.argv[2]))))
            elif sys.argv[1] == 'update_message' and len(sys.argv) == 5:
                print(json.dumps(update_message(sys.argv[2], sys.argv[3], int(sys.argv[4]))))
            elif sys.argv[1] == 'add_message' and len(sys.argv) == 4:
                print(json.dumps(add_message(sys.argv[2], int(sys.argv[3]))))
            elif sys.argv[1] == 'add_media' and len(sys.argv) == 5:
                print(json.dumps(add_media(int(sys.argv[2]), sys.argv[3], sys.argv[4])))
            elif sys.argv[1] == 'add_user' and len(sys.argv) == 5:
                print(json.dumps(add_user(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))))
            else:
                print(json.dumps({'success': False, 'error': 'Invalid action'}))
        else:
            print("Bot is running...")
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))