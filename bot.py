import telebot
from flask import Flask, request
import os

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Diccionario en memoria (usa una base de datos si lo llevarás a producción)
file_storage = []

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot corriendo..."

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "🎮 Bienvenido a All Games Here. Puedes enviar archivos .rar para subirlos.")

@bot.message_handler(content_types=["document"])
def handle_docs(message):
    file_info = bot.get_file(message.document.file_id)
    file_ext = os.path.splitext(message.document.file_name)[-1].lower()
    if file_ext != ".rar":
        bot.reply_to(message, "❌ Solo se permiten archivos .rar.")
        return

    file_storage.append({
        "file_name": message.document.file_name,
        "file_id": message.document.file_id
    })
    bot.reply_to(message, f"✅ Archivo '{message.document.file_name}' almacenado correctamente.")

@bot.message_handler(commands=["listar"])
def list_files(message):
    if not file_storage:
        bot.reply_to(message, "📂 No hay archivos almacenados aún.")
        return
    lista = "\n".join(f"📁 {f['file_name']}" for f in file_storage)
    bot.reply_to(message, f"📄 Archivos disponibles:\n{lista}")

@bot.message_handler(commands=["descargar"])
def send_file(message):
    name = message.text.split(" ", 1)
    if len(name) < 2:
        bot.reply_to(message, "❗ Usa el comando así: /descargar nombre.rar")
        return
    filename = name[1].strip().lower()
    found = [f for f in file_storage if f['file_name'].lower() == filename]
    if not found:
        bot.reply_to(message, "❌ Archivo no encontrado.")
        return
    bot.send_document(message.chat.id, found[0]["file_id"])

if __name__ == "__main__":
    URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=URL)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
