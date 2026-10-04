import asyncio

from core.exceptions import SynthesisError


async def _synthesize_async(text: str, voice: str, output_path: str, rate: str = "+0%") -> None:
    import edge_tts
    await edge_tts.Communicate(text, voice, rate=rate).save(output_path)


def synthesize(text: str, voice: str, output_path: str, rate: str = "+0%") -> None:
    """Generates an MP3 file from text via Microsoft Edge TTS."""
    try:
        asyncio.run(_synthesize_async(text, voice, output_path, rate))
    except Exception as e:
        raise SynthesisError(f"Edge TTS: {e}") from e

