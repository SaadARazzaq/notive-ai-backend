import asyncio
import logging

import pyaudio

from voice_assistant.config import CHANNELS, FORMAT, RATE

logger = logging.getLogger(__name__)


class AudioPlayer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, output=True, start=False
        )
        self.is_playing = False

    async def play_audio_chunk(self, audio_chunk: bytes):
        if not self.is_playing:
            self.stream.start_stream()
            self.is_playing = True

        self.stream.write(audio_chunk)

        # Allow other tasks to run
        await asyncio.sleep(0)

    async def stop_playback(self):
        if self.is_playing:
            # Add a small delay of silence at the end
            silence_duration = 0.2  # 200ms
            silence_frames = int(RATE * silence_duration)
            silence = b"\x00" * (silence_frames * CHANNELS * 2)
            self.stream.write(silence)

            await asyncio.sleep(0.5)

            self.stream.stop_stream()
            self.is_playing = False
            logger.debug("Audio playback completed")

    def close(self):
        self.stream.close()
        self.p.terminate()


audio_player = AudioPlayer()

