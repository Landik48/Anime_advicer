import requests, sqlite3
from bs4 import BeautifulSoup

#Создание базы данных
connect = sqlite3.connect('db.db', check_same_thread=False)
cursor = connect.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS anime 
                            (id integer primary key, choice text, name text, top text, description text, image text)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS favorites 
                                (id integer primary key, anime text, id_user text, choice text, image text)
                                ''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS manga 
                                (id integer primary key, choice text, name text, top text, description text, image text)
                                ''')
connect.commit()

def parser(url, choice):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if 'manga' in url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        data = soup.find_all("div", class_='col-12 col-md-6', limit=20)

        for i in data:
            name = i.find("div", class_='h5 font-weight-normal mb-1')
            description = i.find("div", class_='description d-none d-sm-block')
            top = i.find("div", class_='p-rate-flag__text')
            

            if name is None:
                break
            else: name = name.text

            if top is None:
                top = 'отсутствует'
            else: top = top.text

            if description is None:
                description = 'отсутствует'
            else: 
                description = description.text.split()
                description = " ".join(description)

            image = i.find("div", class_='anime-grid2-lazy lazy')['data-original']
            
            cursor.execute("SELECT * FROM manga WHERE name=? and choice=?", (name, choice,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute('''
        INSERT INTO manga (choice, name, top, description, image) VALUES(?, ?, ?, ?, ?)''', 
        (choice, name, top, description, image))
            connect.commit()
        return choice

    elif 'anime' in url: 
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        data = soup.find_all("div", class_='col-12', limit=20)

        for i in data:
            name = i.find("div", class_='h5 font-weight-normal mb-1')
            description = i.find("div", class_='description d-none d-sm-block')
            top = i.find("div", class_='p-rate-flag__text')

            if name is None:
                break
            else: name = name.text

            if top is None:
                top = 'отсутствует'
            else: top = top.text

            if description is None:
                description = 'отсутствует'
            else: 
                description = description.text.split()
                description = " ".join(description)

            image = i.find("div", class_='anime-list-lazy lazy')['data-original']

            cursor.execute("SELECT * FROM anime WHERE name=? and choice=?", (name, choice,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute('''
        INSERT INTO anime (choice, name, top, description, image) VALUES(?, ?, ?, ?, ?)''', 
        (choice, name, top, description, image))
            connect.commit()
        return choice