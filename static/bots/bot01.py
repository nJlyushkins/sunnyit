import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import sqlite3
import os
from django.utils import timezone
import logging
import time

class Dispatcher:
    def __init__(self, group_id, token):
        try:
            self.api = vk_api.VkApi(token=token).get_api()
        except Exception as e:
            raise Exception("Error with API")
        self.name = "bot01"
        self.group_id = group_id
        try:
            from django.conf import settings
        except:
            raise Exception("Error with including lib django.conf")
        try:
            self.dbPath = str(settings.BASE_DIR) + (str('/main/database/') + str(f'{self.name}DB.db'))
        except Exception as e:
            raise Exception(f"Error with paths: {str(e)}")
        try:
            self.check()
        except:
            raise Exception("Error with creating database")
        _lib = 'static.data.'+self.name
        data = __import__(_lib, globals=globals(), locals=locals(),fromlist=['Images','Messages','Keyboards'])
        self.messages = data.Messages()
        self.keyboards = data.Keyboards()
        self.images = data.Images(self.name)
        self.logger = logging.getLogger("callback")

    def check(self):
        try:
            if not os.path.exists(self.dbPath):
                with sqlite3.connect(self.dbPath) as db:
                    db.execute(
                        "CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, state TEXT, last_activity TEXT, rights INTEGER DEFAULT 0, respond INTEGER DEFAULT 1);")
        except:
            raise Exception("Error with creating database")

    def getUserDb(self, user_id):
        with sqlite3.connect(self.dbPath) as conn:
            cur = conn.cursor()
            userDB = cur.execute(f"SELECT * FROM users WHERE user_id={user_id}").fetchall()
            if len(userDB) == 0:
                cur.execute(f"INSERT INTO users (user_id,state,last_activity) VALUES ({user_id},'none','0')")
                userDB = cur.execute(f"SELECT * FROM users WHERE user_id={user_id}").fetchall()
            cur.execute(f"UPDATE users SET last_activity = '{timezone.now()}' WHERE user_id = {user_id}")
        return userDB[0]

    def getAdmins(self):
        with sqlite3.connect(self.dbPath) as conn:
            cur = conn.cursor()
            userDB = cur.execute(f"SELECT * FROM users WHERE rights=1").fetchall()
        return userDB

    def notifyAdmins(self,msg, keyboard):
        admins = self.getAdmins()
        for admin in admins:
            self.api.messages.send(user_id=admin[1], random_id=0, message=msg, keyboard=keyboard)
        return True
    def changeUserValue(self, user_id, name, value):
        with sqlite3.connect(self.dbPath) as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE users SET {name} = {value} WHERE user_id = {user_id}")
        return True

    def answer(self, request):
        res = None
        try:
            request_type = str(request['type']).split('_')
        except Exception as e:
            self.logger.error(str(e))
            raise e
        if (request_type[0] == "message"):
            if (request_type[1] == "new"):
                try:
                    user_id = request['object']['message']['from_id']
                    msg_text = str(request['object']['message']['text']).lower()
                    peer_id = request['object']['message']['peer_id']
                    user_db = self.getUserDb(user_id)
                    rights = user_db[4]
                    respond = user_db[5]
                except Exception as e:
                    raise Exception("Error with getting user data: " + str(e))
                try:
                    user = self.api.users.get(user_ids=user_id)
                    if(respond == 1):
                        res = self.clientDialogHandler(user_id, user[0], user_db, msg_text, peer_id)
                        #if(rights == 0):
                        #    res = self.clientDialogHandler(user_id, user[0], user_db, msg_text, peer_id)
                        #else:
                        #    res = self.adminDialogHandler(user_id,user[0], user_db, msg_text)
                except Exception as e:
                    self.logger.error(str(e))
                    raise Exception("Error with getting user and handling: " + str(e))
            if request_type[1] == "event":
                try:
                    user_id = request['object']['user_id']
                    payload = request['object']['payload']
                    msg_id = request['object']['conversation_message_id']
                    peer_id = request['object']['peer_id']
                    user_db = self.getUserDb(user_id)
                    rights = user_db[4]
                except Exception as e:
                    raise Exception("Error with getting user data: " + str(e))
                try:
                    user = self.api.users.get(user_ids=user_id)[0]
                    if(rights == 1):
                        res = self.adminCallbackHandler(user, user_id,payload,peer_id,msg_id)
                    else:
                        res = self.clientCallbackHandler(user, user_id,payload,peer_id,msg_id)
                except Exception as e:
                    self.logger.error(str(e))
                    raise Exception("Error with getting user and handling in events: " + str(e))
        return res

    def clientCallbackHandler(self,user, user_id,payload,peer_id,msg_id):
        res = None
        try:
          pass
        except Exception as e:
          self.logger.error('Error in clientCallbackHandler ('+str(user_id)+'): ' + str(e))
        return res

    def adminCallbackHandler(self,user, user_id,payload,peer_id,msg_id):
        res = None
        try:
            if (payload['btn_type'] == 'question'):
                if (payload['action'] == 'close'):
                    client_id = payload['user_id']
                    msg = self.messages.get('init', {'first_name': user['first_name']})
                    keyboard = self.keyboards.get('init')
                    if msg:
                        res = self.api.messages.send(user_id=client_id, random_id=0, message=msg, keyboard=keyboard)
                        self.changeUserValue(client_id, "state", "'init'")
                        self.changeUserValue(client_id, "respond", 1)
                    self.api.messages.edit(peer_id=peer_id,cmid=msg_id,message=f'Обращение с [id{client_id}|пользователем] закрыто!')
        except Exception as e:
            self.logger.error('Error in adminCallbackHandler ('+str(user_id)+'): ' + str(e))
        return res

    def clientDialogHandler(self, user_id, user, user_db, text, peer_id):
        res = None
        self.logger.info('Message: ' + str(text))
        if user_db[2] == 'none':
            msg = self.messages.get('init',{'first_name':user['first_name']})
            keyboard = self.keyboards.get('init')
            if msg:
                res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard=keyboard)
                self.changeUserValue(user_id,"state","'init'")
        elif user_db[2] == 'err':
            if 'да' in text:
                msg = (f"Новое обращение от пользователя: [id{user_id}|{user['first_name']} {user['last_name']}]"
                       f"\nСсылка на чат: https://vk.com/gim{self.group_id}?sel={user_id}")
                keyboard = VkKeyboard(inline=True)
                keyboard.add_callback_button('Закрыть обращение',payload={'btn_type':'question','action':'close','user_id':user_id})
                self.notifyAdmins(msg, keyboard.get_keyboard())
                self.changeUserValue(user_id, "respond", 0)
            else:
                msg = self.messages.get('init', {'first_name': user['first_name']})
                keyboard = self.keyboards.get('init')
                if msg:
                    res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard=keyboard)
                    self.changeUserValue(user_id, "state", "'init'")
        elif text == 'reset':
            self.changeUserValue(user_id,"state","'none'")
        elif 'записаться' in text or 'заполнить' in text:
            msg = self.messages.get('sign')
            keyboard = self.keyboards.get('sign')
            res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard = keyboard)
            self.changeUserValue(user_id, "state", "'sign'")
        elif 'адреса' in text:
            msg = self.messages.get('address')
            keyboard = self.keyboards.get('address')
            res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard = keyboard)
            self.changeUserValue(user_id, "state", "'address'")
        elif 'faq' in text:
            msg = self.messages.get('faq')
            keyboard = self.keyboards.get('faq')
            res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard = keyboard)
            self.changeUserValue(user_id, "state", "'faq'")
        elif 'цена' in text:
            image = self.images.get(['price1'], peer_id, VkUpload(self.api))
            keyboard = self.keyboards.get('price')
            res = self.api.messages.send(user_id=user_id, random_id=0, message='', keyboard = keyboard, attachment=image)
            self.changeUserValue(user_id, "state", "'price'")
        elif 'назад' in text:
            msg = self.messages.get('init',{'first_name':user['first_name']})
            keyboard = self.keyboards.get('init')
            if msg:
                res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard=keyboard)
                self.changeUserValue(user_id,"state","'init'")
        else:
            if user_db[2] == 'sign' and (text[0] == '7' or text[0] == '8' or text[1] == '7'):
                msg = self.messages.get('contact')
                res = self.api.messages.send(user_id=user_id,random_id=0,message=msg)
                msg = (f"Новое обращение от пользователя: [id{user_id}|{user['first_name']} {user['last_name']}]"
                       f"\nСсылка на чат: https://vk.com/gim{self.group_id}?sel={user_id}")
                keyboard = VkKeyboard(inline=True)
                keyboard.add_callback_button('Закрыть обращение',
                                             payload={'btn_type': 'question', 'action': 'close',
                                                      'user_id': user_id})
                self.notifyAdmins(msg, keyboard.get_keyboard())
                self.changeUserValue(user_id, "state", "'contact'")
                self.changeUserValue(user_id, "respond", "0")
            else:
                msg = self.messages.get('err')
                keyboard = self.keyboards.get('err')
                res = self.api.messages.send(user_id=user_id, random_id=0, message=msg, keyboard=keyboard)
                self.changeUserValue(user_id, "state", "'err'")

        return res

    def adminDialogHandler(self,user_id,user,user_db,text):
        res = None
        _lib = 'static.data.'+self.name
        data = __import__(_lib, globals=globals(), locals=locals())
        if user_db[2] == 'none':
            msg = data.Messages.get('init',{'first_name':user.first_name})
            if msg:
                res = self.api.messages.send(user_id=user_id, random_id=0, message=msg)
                self.changeUserValue(user_id,"state","'init'")
        return res