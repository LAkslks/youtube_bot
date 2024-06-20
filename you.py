import telebot
from pytube import YouTube
import psycopg2 
import os


# подключение к PostgreSQL
db_connection = psycopg2.connect(
        database = '',
        user = '',
        password = '',
        host = "",
        port = '')
db_cursor = db_connection.cursor()
# создание таблицы
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT,
        status TEXT
    )
''')
db_connection.commit()



# Токен
bot = telebot.TeleBot("TOKEN")

# привествие
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Привет!\nЗдесь ты можешь скачивать видео из youtube\nДля загрузки пришлите ссылку')


# получение url
def is_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url

@bot.message_handler(func=lambda message:True)
def handle_video_link(message):
  if is_youtube_url(message.text):
    url = message.text
    yt = YouTube(url)
    video_title = yt.title 
    
    
    bot.reply_to(message, f'Начинаю скачивание видео: "{video_title}"')

    # Скачивание видео
    video_file = yt.streams.first().download()
    
    db_cursor.execute('INSERT INTO videos (url, title,  status) VALUES (%s, %s, %s)', (url, video_title, 'downloaded'))
    db_connection.commit()

    # Отправка видео в чат
    bot.send_video(message.chat.id, open(video_file, 'rb' ), caption=video_title)
    

    os.remove(video_file)
  else:
        # Обработка не-Youtube ссылок или других сообщений
        bot.reply_to(message, 'Пожалуйста, отправьте ссылку на YouTube.')
        
        
bot.polling(non_stop=True)


