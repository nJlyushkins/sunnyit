from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api import VkUpload
import logging


class Images:
    def __init__(self, bot_name):
        try:
            from django.conf import settings
        except:
            raise Exception("Error with including lib django.conf")
        self.basePath = str(settings.BASE_DIR) + (str('/../static/botimages/') + str(bot_name) + '/')
        self.images = {
            'price1': 'price1.png'
        }
        self.logger = logging.getLogger('callback')

    def get(self, keys, peer_id, upload: VkUpload):
        try:
            imgs = []
            for key in keys:
                img = self.basePath + self.images[key]
                imgs.append(img)
            self.logger.info('Images: ')
            self.logger.info(imgs)
        except:
            return False
        try:
            upload_images = upload.photo_messages(imgs, peer_id)
            pics = []
            for img in upload_images:
                pic = 'photo{}_{}'.format(img['owner_id'], img['id'])
                pics.append(pic)
            self.logger.info('Pictures: ')
            self.logger.info(pics)
            res = ','.join(map(str, pics))
            self.logger.info('Res: ' + str(res))
        except Exception as e:
            raise Exception("Error with uploading images: " + str(e))
        return res


class Messages:
    def __init__(self):
        self.messages = {
            'init': "Здравствуйте, {first_name} 🤚"
                    "\n\nДобро пожаловать в школу графического дизайна Айвиум! Давайте я расскажу немного больше о нас."
                    "\n\nВ школе Айвиум ребята осваивают одну из самых востребованных профессий уже с ранних лет, а также:"
                    "\n✅ Развивают свои творческие навыки;"
                    "\n✅ Учатся работе в графических редакторах;"
                    "\n✅ Разрабатывают свои первые проекты;"
                    "\n✅ Получают обратную связь, ценные знания и советы от опытных преподавателей."
                    "\n\nКруто? Мы тоже так думаем!"
                    "\n\nХотите узнать больше о занятиях, расписании или об условиях обучения? Выбирайте соответствующий раздел на панели или напишите интересующий вопрос здесь. "
                    "\nНаш помощник ответит вам в ближайшее время!",
            'address': "Ул. Кочетова, д. 35, корп. 3, вход со двора",
            'sign': "✅ Пробное занятие БЕСПЛАТНОЕ"
                     "\n\nНа пробном занятии ребенок сможет познакомиться с нашими преподавателями, с методикой обучения и направлениями развития своих навыков."
                     "\nВы сможете понять для себя, подходим мы вам или нет 😊"
                     "\n\nЕсли вы готовы записаться на занятие, отправьте ваш номер телефона, и администратор свяжется с вами для уточнения деталей 👇",
            'faq': "Ответы на часто задаваемые вопросы:"
                   "\n\n✓ Расписание: \nПятница 18:00, суббота 12:00 и 14:00. Возможно расширение расписания под запрос."
                   "\n\n✓ Сколько детей в группе: \nДо 4 человек."
                   "\n\n✓ Как происходит оплата: \nАбонемент оплачивается авансом на месяц вперед, после чего ребенок может приходить на занятия по своему расписанию без дополнительного согласования с администратором."
                   "\n\n✓ Как оплатить абонемент: \nпо ссылке от администратора или в письме по электронной почте, наличными или переводом на карту."
                   "\n\n✓ Сколько длится курс: \nКурсов как таковых нет, есть направления для развития. "
                   "\nШкола работает по асинхронной методике, поэтому скорость прохождения программы индивидуальна и зависит от ребенка. Некоторые направления рассчитаны на 2-3 года занятий и всегда есть возможность для усложнения программы."
                   "\n\n✓ Три основных блока программы: \n - Изучение функционала графического редактора; \n - Изучение теории графического дизайна; \n - Работа над созданием собственных дизайнов (разных видов полиграфической продукции, оформление личных страниц и т.п.)."
                   "\n\n✓ Можно ли получить налоговый вычет: \nК сожалению, нет."
                   "\n\n✓ Что делать, если ребенок заболел, как переносятся занятия: \nЗанятия не сгорают, они восстанавливаются в конце абонемента по справке от врача. "
                   "\nЕсли занятия пропущены по любым другим причинам, кроме болезни, их можно отработать в других группах в пределах срока действия текущего абонемента.",
            'err': "К сожалению я не могу ответить на ваш вопрос, вас связать с администратором?",
            'contact': "Ваши контакты отправлены администратору, ожидайте звонка в ближайшее время 😌"
        }

    def get(self, key, args=None):
        try:
            res = self.messages[key]
        except:
            return False
        if (args):
            for k, v in args.items():
                _var = "{" + k + "}"
                if _var in res:
                    res = res.replace(_var, v)
        return res


class Keyboards:

    def __init__(self):
        self.keyboards = {
            'init': VkKeyboard(one_time=False, inline=False),
            'sign': VkKeyboard(one_time=False, inline=False),
            'address': VkKeyboard(one_time=False, inline=False),
            'faq': VkKeyboard(one_time=False, inline=False),
            'price': VkKeyboard(one_time=False, inline=False),
            'try': VkKeyboard(inline=True),
            'trial': VkKeyboard(inline=True),
            'err': VkKeyboard(one_time=True, inline=False),
        }

        self.keyboards['init'].add_button('Записаться', VkKeyboardColor.POSITIVE)
        self.keyboards['init'].add_line()
        self.keyboards['init'].add_button('Цена', VkKeyboardColor.PRIMARY)
        self.keyboards['init'].add_button('Адреса', VkKeyboardColor.PRIMARY)
        self.keyboards['init'].add_line()
        self.keyboards['init'].add_button('FAQ')

        self.keyboards['sign'].add_openlink_button('Оставить заявку',
                                                   'https://vk.com/app6013442_-191194616?form_id=7#form_id=7')
        self.keyboards['sign'].add_line()
        self.keyboards['sign'].add_button('Цена', VkKeyboardColor.PRIMARY)
        self.keyboards['sign'].add_button('Адреса', VkKeyboardColor.PRIMARY)
        self.keyboards['sign'].add_line()
        self.keyboards['sign'].add_button('Назад в меню')

        self.keyboards['address'].add_button('Записаться', VkKeyboardColor.POSITIVE)
        self.keyboards['address'].add_line()
        self.keyboards['address'].add_button('Цена', VkKeyboardColor.PRIMARY)
        self.keyboards['address'].add_button('FAQ', VkKeyboardColor.PRIMARY)
        self.keyboards['address'].add_line()
        self.keyboards['address'].add_button('Назад в меню')

        self.keyboards['faq'].add_button('Записаться', VkKeyboardColor.POSITIVE)
        self.keyboards['faq'].add_line()
        self.keyboards['faq'].add_button('Цена', VkKeyboardColor.PRIMARY)
        self.keyboards['faq'].add_button('Адреса', VkKeyboardColor.PRIMARY)
        self.keyboards['faq'].add_line()
        self.keyboards['faq'].add_button('Назад в меню')

        self.keyboards['price'].add_button('Записаться', VkKeyboardColor.POSITIVE)
        self.keyboards['price'].add_line()
        self.keyboards['price'].add_button('FAQ', VkKeyboardColor.PRIMARY)
        self.keyboards['price'].add_button('Адреса', VkKeyboardColor.PRIMARY)
        self.keyboards['price'].add_line()
        self.keyboards['price'].add_button('Назад в меню')

        self.keyboards['err'].add_button('Да', VkKeyboardColor.POSITIVE)
        self.keyboards['err'].add_button('Нет', VkKeyboardColor.NEGATIVE)

        self.keyboards['try'].add_callback_button('Узнать про пробную запись',
                                                  payload={'btn_type': 'info', 'info': 'trial'})

    def get(self, key):
        try:
            res = self.keyboards[key].get_keyboard()
        except:
            return False
        return res