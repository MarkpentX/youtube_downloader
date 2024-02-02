import bcrypt
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube


def write_password(login, password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)

    with open('passwords.txt', 'ab') as file:
        file.write(login.encode('utf-8') + b'::' + hashed + b'\n')


def check_login(login, password):
    pwd_bytes = password.encode('utf-8')
    # Открываем файл для чтения
    with open('passwords.txt', 'r') as file:
        # Читаем строки из файла
        lines = file.readlines()

    # Обрабатываем каждую строку и извлекаем логин и хеш пароля
    for line in lines:
        # Разделяем строку по '::'
        parts = line.strip().split('::')
        # Проверяем, что у нас есть две части (логин и хеш пароля)
        if len(parts) == 2:
            stored_login, stored_password_hash = parts

            # Проверяем соответствие логина и хеша пароля
            if login == stored_login:
                # Проверяем пароль
                if bcrypt.checkpw(pwd_bytes, stored_password_hash.encode('utf-8')):
                    return True  # Логин и пароль совпадают

    return False  # Логин или пароль не найдены


def download_video(url, filename):
    try:
        video = YouTube(url)
        video.streams.get_highest_resolution().download(filename=filename)
        return True
    except Exception as e:
        print(e)
        return False


def download_audio(url, filename):
    try:
        result = download_video(url, filename)
        video_clip = VideoFileClip(filename)
        # get the audio
        audio_clip = video_clip.audio

        audio_path = filename.replace('.mp4', '.mp3')

        audio_clip.write_audiofile(audio_path)

        video_clip.close()
        audio_clip.close()
        return True
    except Exception as e:
        print(e)
        return False
