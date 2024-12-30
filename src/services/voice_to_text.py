# src/services/voice_to_text.py
import os
import tempfile
import requests
from telegram import Update
from telegram.ext import ContextTypes

async def transcribe_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Descarga el archivo de voz de Telegram y lo envía a un servicio de STT (Speech To Text).
    Devuelve el texto transcrito.
    """
    # 1. Obtener file_id y descargar el archivo temporalmente
    file_id = update.message.voice.file_id
    voice_file = await context.bot.get_file(file_id)

    # 2. Guardar el archivo localmente
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"{file_id}.ogg")
    await voice_file.download_to_drive(temp_path)

    # 3. LLamar a un servicio de STT. Esto es solo un placeholder:
    #    Ajusta según la API que uses (Google, OpenAI, IBM, etc.).
    #    Por ejemplo, si usas un modelo local, podrías hacer algo como:
    # text = my_local_stt_model.transcribe(temp_path)

    text = "Aquí iría el resultado de la transcripción de audio"  # Placeholder

    # 4. Eliminar el archivo temporal si ya no lo necesitas
    #    (opcional, pero recomendado para no llenar el servidor de archivos)
    # os.remove(temp_path)

    return text
