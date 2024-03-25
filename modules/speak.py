import numpy as np
from optimum.bettertransformer import BetterTransformer
from pydub import AudioSegment
import io
from transformers import AutoProcessor, BarkModel
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("suno/bark-small")
bark = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float16).to(device)
bark = BetterTransformer.transform(bark, keep_original_model=False)


def speak(message: str, voice="v2/en_speaker_6"):
    inputs = processor(message, voice_preset=voice).to(device)
    with torch.inference_mode():
        output = bark.generate(**inputs, do_sample=True)
    audio_samples = (output.squeeze().cpu().numpy() * 32767).astype(np.int16)

    # Convert NumPy array to WAV format using pydub
    audio_segment = AudioSegment(
        audio_samples.tobytes(),
        frame_rate=24000,
        sample_width=audio_samples.dtype.itemsize,
        channels=1
    )
    audio_io = io.BytesIO()
    audio_segment.export(audio_io, format="wav")
    audio_io.seek(0)
    return audio_io
