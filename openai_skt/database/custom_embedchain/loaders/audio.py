import asyncio
from functools import partial

import aiofiles
import openai
from pdf2image import convert_from_path

from embedchain.helper_classes.json_serializable import register_deserializable
# from embedchain.loaders.base_loader import BaseLoader
from embedchain.utils import clean_string

from database.custom_embedchain.loaders.base_loader import BaseLoader

@register_deserializable
class AudioLoader(BaseLoader):
    def load_data(self, url):
        audio_file= open(url, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        meta_data = {
            "url": url,
        }

        return [
            {
                "content": transcript.text,
                "meta_data": meta_data,
            }
        ]

    async def async_load_data(self, url):
        loop = asyncio.get_event_loop()
        async with aiofiles.open(url, "rb") as f:
            audio = await f.read()

            # functools.partial을 사용하여 openai.Audio.transcribe 메서드에 인수를 전달
            transcribe_func = partial(openai.Audio.transcribe, "whisper-1", audio)
            transcript = await loop.run_in_executor(None, transcribe_func)

        meta_data = {
            "url": url,
        }    
        return [
            {
                "content": transcript.text,
                "meta_data": meta_data,
            }
        ]

if __name__ == "__main__":
    audio_loader = AudioLoader()
    audio_loader.load_data("X2Download.app - 월세=월급, 미친 집값의 나라에서 한국인이 발견한 기회 _ 고투조이 변성민 (128 kbps).mp3")