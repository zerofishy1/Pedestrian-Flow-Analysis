import shutil
import os

# Создание папок для загрузки и результатов, если их нет
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
RESULT_JSON = os.path.join(RESULT_FOLDER, 'results.json')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Функция для очистки папки
def clear_upload_folder():
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Удаляем файл или ссылку
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Удаляем папку
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {e}")

# Очистка папки перед запуском приложения
clear_upload_folder()

from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import json
from main import process_video  # Импорт алгоритма обработки из main.py

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)
        if file:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
            return redirect(request.url)

    # Получаем список файлов в папке uploads
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        # Сохраняем загруженное видео
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Вызываем функцию обработки видео из main.py
        process_video(filepath)

        # Читаем результаты обработки из JSON
        if os.path.exists(RESULT_JSON):
            with open(RESULT_JSON, 'r', encoding='utf-8') as f:
                results = json.load(f)
        else:
            results = {}

        # Рендерим страницу с результатами сразу после обработки
        return render_template('upload.html', results=results)

    # Если метод GET, показываем пустую страницу или с ранее сохраненными результатами
    if os.path.exists(RESULT_JSON):
        with open(RESULT_JSON, 'r', encoding='utf-8') as f:
            results = json.load(f)
    else:
        results = {}

    return render_template('upload.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
