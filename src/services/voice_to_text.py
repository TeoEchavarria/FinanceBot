import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from utils.logger import LoggingUtil
from pydub import AudioSegment

logger = LoggingUtil.setup_logger()

async def transcribe_voice(update: Update, context: ContextTypes.DEFAULT_TYPE, time_user : int) -> str:
    file_id = update.message.voice.file_id
    voice_file = await context.bot.get_file(file_id)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # Descargar el archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=True, suffix=".ogg") as tf:
        await voice_file.download_to_drive(tf.name)
        tf.seek(0)
        audio = AudioSegment.from_file(tf.name)
        duration_ms = len(audio)
        duration_seconds = duration_ms / 1000
        # Usar la API de Whisper para transcribir
        if duration_seconds > time_user:
            return None, -1
        try:
            with open(tf.name, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            return transcript.text, duration_seconds
        except Exception as e:
            logger.error(f"Error transcribiendo audio con Whisper: {e}")
            raise RuntimeError("No se pudo transcribir el audio.")