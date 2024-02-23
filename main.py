import telebot, sqlite3, time
from telebot import types
from parsing import parser

#Подсчёт пользователей
class DB:
    def __init__(self):
        self.connect = sqlite3.connect('db.db')
        self.cursor = self.connect.cursor()
        self.cursor.execute('''
CREATE TABLE IF NOT EXISTS users 
                            (id integer primary key, name_user, userid)
                            ''')
        self.connect.commit()

    #Добавление контакта в базу данных
    def add_to_users(self, name_user, userid):
        self.cursor.execute("SELECT * FROM users WHERE userid=?", (userid,))
        result = self.cursor.fetchone()
        if result is None:
            self.cursor.execute('''
    INSERT INTO users (name_user, userid) VALUES(?, ?)''', (name_user, userid))
        self.connect.commit()


id_user = 1641006916
bot = telebot.TeleBot('токен')

while 1:
    try:
        bot.send_message(id_user, "Бот онлайн!")

        @bot.message_handler(commands=['start'])
        def starting(chat):
            bot.send_message(chat.chat.id, f'''Привет, {chat.from_user.first_name}! 
Чтобы посмотреть перечень команд нажмите меню''')
            idUSER = f'Имя и фамилия: {chat.from_user.first_name}, {chat.from_user.last_name};'
            nameUSER = f'Никнейм: {chat.from_user.username}'
            db = DB()
            db.add_to_users(idUSER, nameUSER)

            
        @bot.message_handler(commands=['help'])
        def help(chat):
            bot.send_message(chat.chat.id, '''<b>Привет! Я бот для подбора аниме и манги</b>
                            
1.Чтобы начать искать аниме или мангу вам нужно ввести /search и следовать дальнейшим инструкциям. 
2.Чтобы посмотреть аниме или мангу в избранном нужно ввести /favorites
Всё просто :)
                    
По вопросам и предложениям обращаться: @Landik_48
Также приглашаю в свой <a href="https://t.me/programm_chel">тг канал</a>, где публикуются все мои разработки и актуальная информация про бота
Разработчику на чай: Тинькофф 2200700941801077
                        
Все данные взяты с сайта animego.org''', parse_mode= 'html')
            
        @bot.message_handler(commands=['favorites'])
        def favourites(chat):
            connect = sqlite3.connect('db.db')
            cursor = connect.cursor()

            cursor.execute("SELECT * FROM favorites WHERE id_user=?", (chat.from_user.id,))
            rows = cursor.fetchall()

            if not rows:
                bot.send_message(chat.from_user.id, 'Упс... У вас ничего не добавлено в избранное!')

            button = types.InlineKeyboardMarkup()
            btn_fav = types.InlineKeyboardButton("Удалить из избранного", callback_data='favorite_del')
            
            button.row(btn_fav) 
            
            for row in rows:
                time.sleep(0.2)
                bot.send_photo(chat.from_user.id, photo=row[4],caption=f'''<b>Жанр: {row[3]}</b>
                            
        {row[1]}''', parse_mode= 'html', reply_markup=button)

        @bot.callback_query_handler(func = lambda callback: callback.data == 'favorite_del')
        def delete_favorite(callback):
            text = callback.message.caption.splitlines()
            text = '\n'.join(text[2:])
            id_user = str(callback.from_user.id)
            bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)

            connect = sqlite3.connect('db.db')
            cursor = connect.cursor()
            cursor.execute("DELETE FROM favorites WHERE anime=? and id_user=?", (text,id_user,))
            connect.commit()

            bot.send_message(callback.from_user.id, 'Успешно!')

            
        #Начало подбора аниме и манги
        list_choice_animeRU = ['Безумие','Боевые искусства','Вампиры','Военное','Гарем','Демоны','Детектив','Детское','Дзёсей','Драма',
                            'Игры','Исторический','Комедия','Космос','Магия','Машины','Меха','Музыка','Пародия','Повседневность',
                            'Полиция','Приключения','Психологическое','Романтика','Самураи','Сверхъестественное','Сёдзе','Сёдзе Ай', 'Сёнен', 'Сёнен-Ай',
                            'Спорт','Супер сила', 'Сэйнен','Триллер','Ужасы','Фантастика','Фэнтези','Школа','Экшен','Этти']

        list_choice_mangaRU = ['Безумие','Боевые искусства','Вампиры','Военное','Гарем','Демоны','Детектив','Детское','Дзёсей', 'Додзинси','Драма',
                            'Игры','Исторический','Комедия','Космос','Магия','Машины','Меха','Музыка','Пародия','Повседневность',
                            'Полиция','Приключения','Психологическое','Романтика','Самураи','Сверхъестественное','Сёдзе','Сёдзе Ай', 'Сёнен', 'Сёнен-Ай', 'Смена пола',
                            'Спорт','Супер сила', 'Сэйнен','Триллер','Ужасы','Фантастика','Фэнтези','Школа','Экшен','Этти']
        global_choice = None


        @bot.message_handler(commands=['search'])
        def search(chat):
            button = types.InlineKeyboardMarkup()

            btn1 = types.InlineKeyboardButton("Аниме", callback_data='anime')
            btn2 = types.InlineKeyboardButton("Манга", callback_data='manga')

            button.row(btn1, btn2)

            bot.send_message(chat.from_user.id, "Выбери: аниме или манга?", reply_markup=button)

        #Подбор аниме
        @bot.callback_query_handler(func = lambda callback: callback.data == 'anime')
        def choice_genre_anime(callback):
            global global_choice
            bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
            global_choice = 'аниме'

            button = types.InlineKeyboardMarkup()
            buttons = {}
            i = 0
            while i < 40:
                buttons["btn{}".format(i+1)] = types.InlineKeyboardButton(list_choice_animeRU[i], callback_data = list_choice_animeRU[i])
                i += 1

            for i in range(40):
                i+=1
                button.row(buttons[f'btn{i}'])

            bot.send_message(callback.from_user.id, "Выбери жанр", reply_markup=button)

        #Подбор манги
        @bot.callback_query_handler(func = lambda callback: callback.data == 'manga')
        def choice_genre_manga(callback):
            global global_choice
            bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
            global_choice = 'манга'

            button = types.InlineKeyboardMarkup()
            buttons = {}
            i = 0
            while i < 42:
                buttons["btn{}".format(i+1)] = types.InlineKeyboardButton(list_choice_mangaRU[i], callback_data = list_choice_mangaRU[i])
                i += 1

            for i in range(42):
                i+=1
                button.row(buttons[f'btn{i}'])

            bot.send_message(callback.from_user.id, "Выбери жанр", reply_markup=button)

        @bot.callback_query_handler(func = lambda callback: True)
        def choice_anime_or_manga(callback):
            global global_choice
            conditions = {
                'callback.data == "Безумие" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-dementia/apply?sort=rating&direction=desc", choice="Безумие")',
                'callback.data == "Боевые искусства" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-martial-arts/apply?sort=rating&direction=desc", choice="Боевые искусства")',
                'callback.data == "Вампиры" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-vampire/apply?sort=rating&direction=desc", choice="Вампиры")',
                'callback.data == "Военное" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-military/apply?sort=rating&direction=desc", choice="Военное")',
                'callback.data == "Гарем" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-harem/apply?sort=rating&direction=desc", choice="Гарем")',
                'callback.data == "Демоны" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-demons/apply?sort=rating&direction=desc", choice="Демоны")',
                'callback.data == "Детектив" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-mystery/apply?sort=rating&direction=desc", choice="Детектив")',
                'callback.data == "Детское" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-kids/apply?sort=rating&direction=desc", choice="Детское")',
                'callback.data == "Дзёсей" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-josei/apply?sort=rating&direction=desc", choice="Дзёсей")',
                'callback.data == "Драма" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-drama/apply?sort=rating&direction=desc", choice="Драма")',
                'callback.data == "Игры" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-game/apply?sort=rating&direction=desc", choice="Игры")',
                'callback.data == "Исторический" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-historical/apply?sort=rating&direction=desc", choice="Исторический")',
                'callback.data == "Комедия" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-comedy/apply?sort=rating&direction=desc", choice="Комедия")',
                'callback.data == "Космос" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-space/apply?sort=rating&direction=desc", choice="Космос")',
                'callback.data == "Магия" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-magic/apply?sort=rating&direction=desc", choice="Магия")',
                'callback.data == "Машины" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-cars/apply?sort=rating&direction=desc", choice="Машины")',
                'callback.data == "Меха" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-mecha/apply?sort=rating&direction=desc", choice="Меха")',
                'callback.data == "Музыка" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-music/apply?sort=rating&direction=desc", choice="Музыка")',
                'callback.data == "Пародия" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-parody/apply?sort=rating&direction=desc", choice="Пародия")',
                'callback.data == "Повседневность" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-slice-of-life/apply?sort=rating&direction=desc", choice="Повседневность")',
                'callback.data == "Полиция" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-police/apply?sort=rating&direction=desc", choice="Полиция")',
                'callback.data == "Приключения" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-adventure/apply?sort=rating&direction=desc", choice="Приключения")',
                'callback.data == "Психологическое" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-psychological/apply?sort=rating&direction=desc", choice="Психологическое")',
                'callback.data == "Романтика" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-romance/apply?sort=rating&direction=desc", choice="Романтика")',
                'callback.data == "Самураи" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-samurai/apply?sort=rating&direction=desc", choice="Самураи")',
                'callback.data == "Сверхъестественное" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-supernatural/apply?sort=rating&direction=desc", choice="Сверхъестественное")',
                'callback.data == "Сёдзе" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-shoujo/apply?sort=rating&direction=desc", choice="Сёдзе")',
                'callback.data == "Сёдзе Ай" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-shoujo-ai/apply?sort=rating&direction=desc", choice="Сёдзе Ай")',
                'callback.data == "Сёнен" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-shounen/apply?sort=rating&direction=desc", choice="Сёнен")',
                'callback.data == "Сёнен-Ай" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-shounen-ai/apply?sort=rating&direction=desc", choice="Сёнен-Ай")',
                'callback.data == "Спорт" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-sports/apply?sort=rating&direction=desc", choice="Спорт")',
                'callback.data == "Супер сила" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-super-power/apply?sort=rating&direction=desc", choice="Супер сила")',
                'callback.data == "Сэйнен" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-seinen/apply?sort=rating&direction=desc", choice="Сэйнен")',
                'callback.data == "Триллер" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-thriller/apply?sort=rating&direction=desc", choice="Триллер")',
                'callback.data == "Ужасы" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-horror/apply?sort=rating&direction=desc", choice="Ужасы")',
                'callback.data == "Фантастика" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-sci-fi/apply?sort=rating&direction=desc", choice="Фантастика")',
                'callback.data == "Фэнтези" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-fantasy/apply?sort=rating&direction=desc", choice="Фэнтези")',
                'callback.data == "Школа" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-school/apply?sort=rating&direction=desc", choice="Школа")',
                'callback.data == "Экшен" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-action/apply?sort=rating&direction=desc", choice="Экшен")',
                'callback.data == "Этти" and global_choice == "аниме"' : 'parser(url="https://animego.org/anime/filter/genres-is-ecchi/apply?sort=rating&direction=desc", choice="Этти")', 
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
                'callback.data == "Безумие" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-dementia/apply?sort=rating&direction=desc", choice="Безумие")',
                'callback.data == "Боевые искусства" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-martial-arts/apply?sort=rating&direction=desc", choice="Боевые искусства")',
                'callback.data == "Вампиры" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-vampire/apply?sort=rating&direction=desc", choice="Вампиры")',
                'callback.data == "Военное" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-military/apply?sort=rating&direction=desc", choice="Военное")',
                'callback.data == "Гарем" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-harem/apply?sort=rating&direction=desc", choice="Гарем")',
                'callback.data == "Демоны" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-demons/apply?sort=rating&direction=desc", choice="Демоны")',
                'callback.data == "Детектив" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-mystery/apply?sort=rating&direction=desc", choice="Детектив")',
                'callback.data == "Детское" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-kids/apply?sort=rating&direction=desc", choice="Детское")',
                'callback.data == "Дзёсей" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-josei/apply?sort=rating&direction=desc", choice="Дзёсей")',
                'callback.data == "Додзинси" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-doujinshi/apply?sort=rating&direction=desc", choice="Додзинси")',
                'callback.data == "Драма" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-drama/apply?sort=rating&direction=desc", choice="Драма")',
                'callback.data == "Игры" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-game/apply?sort=rating&direction=desc", choice="Игры")',
                'callback.data == "Исторический" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-historical/apply?sort=rating&direction=desc", choice="Исторический")',
                'callback.data == "Комедия" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-comedy/apply?sort=rating&direction=desc", choice="Комедия")',
                'callback.data == "Космос" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-space/apply?sort=rating&direction=desc", choice="Космос")',
                'callback.data == "Магия" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-magic/apply?sort=rating&direction=desc", choice="Магия")',
                'callback.data == "Машины" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-cars/apply?sort=rating&direction=desc", choice="Машины")',
                'callback.data == "Меха" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-mecha/apply?sort=rating&direction=desc", choice="Меха")',
                'callback.data == "Музыка" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-music/apply?sort=rating&direction=desc", choice="Музыка")',
                'callback.data == "Пародия" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-parody/apply?sort=rating&direction=desc", choice="Пародия")',
                'callback.data == "Повседневность" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-slice-of-life/apply?sort=rating&direction=desc", choice="Повседневность")',
                'callback.data == "Полиция" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-police/apply?sort=rating&direction=desc", choice="Полиция")',
                'callback.data == "Приключения" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-adventure/apply?sort=rating&direction=desc", choice="Приключения")',
                'callback.data == "Психологическое" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-psychological/apply?sort=rating&direction=desc", choice="Психологическое")',
                'callback.data == "Романтика" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-romance/apply?sort=rating&direction=desc", choice="Романтика")',
                'callback.data == "Самураи" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-samurai/apply?sort=rating&direction=desc", choice="Самураи")',
                'callback.data == "Сверхъестественное" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-supernatural/apply?sort=rating&direction=desc", choice="Сверхъестественное")',
                'callback.data == "Сёдзе" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-shoujo/apply?sort=rating&direction=desc", choice="Сёдзе")',
                'callback.data == "Сёдзе Ай" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-shoujo-ai/apply?sort=rating&direction=desc", choice="Сёдзе Ай")',
                'callback.data == "Сёнен" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-shounen/apply?sort=rating&direction=desc", choice="Сёнен")',
                'callback.data == "Сёнен-Ай" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-shounen-ai/apply?sort=rating&direction=desc", choice="Сёнен-Ай")',
                'callback.data == "Смена пола" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-gender-bender/apply?sort=rating&direction=desc", choice="Смена пола")',
                'callback.data == "Спорт" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-sports/apply?sort=rating&direction=desc", choice="Спорт")',
                'callback.data == "Супер сила" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-super-power/apply?sort=rating&direction=desc", choice="Супер сила")',
                'callback.data == "Сэйнен" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-seinen/apply?sort=rating&direction=desc", choice="Сэйнен")',
                'callback.data == "Триллер" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-thriller/apply?sort=rating&direction=desc", choice="Триллер")',
                'callback.data == "Ужасы" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-horror/apply?sort=rating&direction=desc", choice="Ужасы")',
                'callback.data == "Фантастика" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-sci-fi/apply?sort=rating&direction=desc", choice="Фантастика")',
                'callback.data == "Фэнтези" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-fantasy/apply?sort=rating&direction=desc", choice="Фэнтези")',
                'callback.data == "Школа" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-school/apply?sort=rating&direction=desc", choice="Школа")',
                'callback.data == "Экшен" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-action/apply?sort=rating&direction=desc", choice="Экшен")',
                'callback.data == "Этти" and global_choice == "манга"' : 'parser(url="https://animego.org/manga/filter/genres-is-ecchi/apply?sort=rating&direction=desc", choice="Этти")', 
            }
            
            for condition, action in conditions.items():
                if eval(condition):
                    eval(action)
                    bot.delete_message(callback.message.chat.id, callback.message.message_id - 0)
                    bot.send_message(callback.from_user.id, '_Вот что я для вас нашёл:_', parse_mode= 'MarkdownV2')

                    connect = sqlite3.connect('db.db')
                    cursor = connect.cursor()
                    
                    if global_choice == 'аниме':
                        cursor.execute("SELECT * FROM anime WHERE choice=?", (eval(action),))
                        rows = cursor.fetchall()

                        button = types.InlineKeyboardMarkup()
                        btn_fav = types.InlineKeyboardButton("Добавить в избранное", callback_data='favorite')
                        
                        button.row(btn_fav) 

                        for row in rows:
                            time.sleep(0.2)
                            bot.send_photo(callback.from_user.id, photo=row[5], caption = f'''<b>Название:</b> {row[2]}
<b>Рейтинг:</b> {row[3]}
<b>Описание:</b> {row[4]}''', parse_mode= 'html', reply_markup=button)
                        break
                    
                    elif global_choice == 'манга':
                        cursor.execute("SELECT * FROM manga WHERE choice=?", (eval(action),))
                        rows = cursor.fetchall()

                        button = types.InlineKeyboardMarkup()
                        btn_fav = types.InlineKeyboardButton("Добавить в избранное", callback_data='favorite')
                        
                        button.row(btn_fav) 

                        for row in rows:
                            time.sleep(0.2)
                            bot.send_photo(callback.from_user.id, photo=row[5], caption = f'''<b>Название:</b> {row[2]}
<b>Рейтинг:</b> {row[3]}
<b>Описание:</b> {row[4]}''', parse_mode= 'html', reply_markup=button)
                        break


                elif callback.data == "favorite":
                    bot.delete_message(callback.message.chat.id, callback.message.message_id - 0) 
                    favorite_add(callback)
                    break


                
        @bot.message_handler(commands=['COMMAND_NOT(gghgfay3v3b7tbv3t3bh)'])
        def favorite_add(callback):
            global global_choice
            anime = callback.message.caption
            image = callback.message.photo[-1].file_id
            id_user = callback.from_user.id

            connect = sqlite3.connect('db.db')
            cursor = connect.cursor()
            
            cursor.execute("SELECT * FROM favorites WHERE anime=?", (anime,))
            result = cursor.fetchone()
            if result is None:
                cursor.execute('''
        INSERT INTO favorites (id_user, anime, choice, image) VALUES(?, ?, ?, ?)''', (id_user, anime, global_choice, image))
            connect.commit() 

            bot.send_photo(callback.from_user.id, photo=image, caption = f'''<i><b>Рекомендация аниме:</b></i> 
"{anime}" 
<b><i>успешно добавлена в избранное!</i></b>''', reply_markup=types.ReplyKeyboardRemove(), parse_mode= 'html')
        #Конец подбора аниме и манги

        bot.polling(none_stop = True)

    except Exception as _ex: 
        bot.send_message(id_user, f'<b>Бот будет перезапущен по ошибке</b>: {_ex}', parse_mode='html')
        print(_ex)
