import os
import tempfile
from collections.abc import Callable

from core.models import TranslationJob, PipelineResult
from core.exceptions import VideoTranslatorError
from infrastructure import downloader, transcriber, synthesizer, video, separator
from infrastructure.translators import get_translator
from infrastructure.storage import LocalStorage


class TranslationPipeline:

    def __init__(self) -> None:
        self.storage = LocalStorage()

    def run(
        self,
        job: TranslationJob,
        on_progress: Callable[[float, str], None] | None = None,
    ) -> PipelineResult:

        def progress(pct: float, msg: str) -> None:
            if on_progress:
                on_progress(pct, msg)

        try:
            with tempfile.TemporaryDirectory() as tmp:

                progress(0.05, "Loading video...")
                video_path = downloader.download(job.url, tmp)

                progress(0.15, "Audio Extraction...")
                audio_path = os.path.join(tmp, "audio.wav")
                video.extract_audio(video_path, audio_path)

                progress(0.25, "Separating the voice from the background noise...")
                sep_dir = os.path.join(tmp, "separated")
                os.makedirs(sep_dir, exist_ok=True)
                vocals_path, background_path = separator.separate(audio_path, sep_dir)

                progress(0.38, "Speech Recognition...")
                
                segments = transcriber.transcribe_segments(vocals_path, job.source_lang)
                if not segments:
                    raise VideoTranslatorError("No voice was found in the video")

                transcript = " ".join(s.text for s in segments)

                progress(0.48, "Translation of segments...")
                translator      = get_translator(job.backend, job.custom_url)
                translations:   list[str] = []
                audio_segments: list[tuple[float, float, str]] = []

                for i, seg in enumerate(segments):
                    translated = translator.translate(seg.text, job.target_lang, job)
                    translations.append(translated)

                    seg_audio = os.path.join(tmp, f"seg_{i}.mp3")

                    slot_dur = seg.end - seg.start
                    word_count = len(translated.split())
                    est_dur = word_count / 2.5
                    if slot_dur > 0 and est_dur > 0:
                        ratio = est_dur / slot_dur
                        rate_pct = max(-50, min(100, int((ratio - 1) * 100)))
                        rate_str = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
                    else:
                        rate_str = "+0%"

                    synthesizer.synthesize(translated, job.target_voice, seg_audio, rate=rate_str)
                    audio_segments.append((seg.start, seg.end, seg_audio))

                    pct = 0.48 + 0.30 * ((i + 1) / len(segments))
                    progress(pct, f"Segment {i + 1}/{len(segments)}...")

                progress(0.82, "Synchronization by timestamps...")
                voice_sync = os.path.join(tmp, "voice_sync.mp3")
                video_dur  = video.get_duration(video_path)
                video.build_sync_audio(audio_segments, video_dur, tmp, voice_sync)

                progress(0.88, "A mix of vocals with the original background...")
                final_audio = os.path.join(tmp, "final_audio.mp3")
                video.mix_voice_with_background(voice_sync, background_path, final_audio)

                progress(0.94, "Video compilation...")
                out_path = os.path.join(tmp, "output.mp4")
                video.merge(video_path, final_audio, out_path)

                final_path = self.storage.save(out_path)
                progress(1.0, "Done!")

                return PipelineResult(
                    video_path=final_path,
                    transcript=transcript,
                    translation=" ".join(translations),
                )

        except VideoTranslatorError:
            raise
        except Exception as e:
            raise VideoTranslatorError(str(e)) from e