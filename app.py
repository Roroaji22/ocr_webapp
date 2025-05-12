from flask import Flask, render_template, request
from PIL import Image
import pytesseract
import os
import speech_recognition as sr
from pydub import AudioSegment


app = Flask(__name__)

# Lokasi tesseract.exe (ubah sesuai lokasi instalasi kamu)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Fungsi untuk ekstraksi teks dari gambar (OCR)
def ocr_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Fungsi untuk ekstraksi teks dari audio (Speech-to-Text)
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        # Cek apakah file audio berformat MP3, jika iya, konversi ke WAV
        if audio_path.endswith('.mp3'):
            sound = AudioSegment.from_mp3(audio_path)
            audio_path = audio_path.replace('.mp3', '.wav')
            sound.export(audio_path, format='wav')

        # Pastikan file audio dalam format yang tepat, konversi jika perlu
        elif not audio_path.endswith('.wav'):
            raise ValueError("Format file audio tidak didukung. Harap upload file MP3 atau WAV.")

        # Ekstraksi suara menjadi teks
        with sr.AudioFile(audio_path) as source:
            print("Mendengarkan audio...")
            audio_data = recognizer.record(source, duration=60)
            print("Mengenali teks...")
            text = recognizer.recognize_google(audio_data, language="id-ID")
            return text

    except sr.UnknownValueError:
        return "Google tidak dapat memahami audio."
    except sr.RequestError as e:
        return f"Error dari Google API: {e}"
    except ValueError as e:
        return str(e)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload/image', methods=['GET', 'POST'])
def upload_image():
    text = ""
    image_filename = ""
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file.filename != '':
            image_filename = image_file.filename
            image_path = os.path.join('static', image_filename)
            image_file.save(image_path)
            text = ocr_from_image(image_path)
    return render_template('index.html', text=text, image_filename=image_filename)

@app.route('/upload/audio', methods=['GET', 'POST'])
def upload_audio():
    text = ""
    audio_filename = ""
    if request.method == 'POST':
        audio_file = request.files['file']
        if audio_file.filename != '':
            audio_filename = audio_file.filename
            audio_path = os.path.join('static', audio_filename)
            audio_file.save(audio_path)
            text = speech_to_text(audio_path)
    return render_template('index.html', text=text, audio_filename=audio_filename)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


if __name__ == '__main__':
    app.run(debug=True)
