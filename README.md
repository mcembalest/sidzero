# SID Zero

SID Zero (Synthetic Information Diffusion v0.1) is a robot like the [Open Interpreter O1](https://github.com/OpenInterpreter/open-interpreter), albeit less capable and with a more malicious personality.

SID is a raspberry pi with a camera & microphone plugged via HDMI into a TV. When running, audio is captured via the microphone and transcribed into text to chat with an LLM running locally on a desktop computer. We use a multimodal vision-language model to give SID descriptions of the people & objects in the visible environment (albeit with plenty of hallucinations). It can, for example, try to roast your outfit:

https://github.com/mcembalest/sidzero/assets/70534565/9058e99f-8614-4306-8c18-fa2598c4958c

After running computation on the desktop, we stream the LLM response spoken aloud to be played as audio output:

https://github.com/mcembalest/sidzero/assets/70534565/9c8b5f7f-6785-434d-823d-4ce319628fe1


# Models Used

- default LLM: `mistral:7b-instruct-v0.2-q4_0` with Ollama

- Multimodal vision-language model: `vikhyatk/moondream2` with HuggingFace transformers

- Speech to text: `vosk-model-small-en-us-0.15` with the vosk python SDK

- Text to speech: `suno/bark-small` with HuggingFace transformers

## Additional models

- (also connected with an online RAG LLM: `sonar-small-online` via the `pplx` api

# Setup

## Client

The client maintains the user-robot interaction and runs the audio & visual I/O. We use a Raspberry Pi 4, connect a webcam for visual input, a micrphone for audio input, and a monitor for visual display & audio output.

Install [ffmpeg](https://evermeet.cx/ffmeg/) and a [speech to text model](https://alphacephei.com/vosk/models). Then, install client requirements:
```bash
pip install -r client_requirements.txt
```

Set environment variable `SID_SERVER` to the url of the computation server (e.g. for your desktop this could be `http://192.168...`)

Then, start the client
```bash
python client.py
```

## Server
The server runs the speech/language/multimodal models. We use a windows desktop computer with a RTX 3060 GPU, over a [private home network](https://arcadian.cloud/windows/2022/12/08/how-to-allow-icmp-ping-through-windows-firewall/).

Download a [text to speech model](https://huggingface.co/models?other=text-to-audio), a [language model](https://ollama.com/library), and a [multimodal vision/language model](https://huggingface.co/models?pipeline_tag=image-text-to-text). Then, install server requirements:
```bash
pip install -r server_requirements.txt
```

Set environment variables for tool modules you want to use, e.g. `PPLX_API_KEY`, `WOLFRAM_CALCULATOR_APP_ID`, etc

Then, start the server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

# Roadmap

- async client
  - we want the client to be able to launch a job that may take a while without blocking the chat
- latency improvements
  - the text to speech can be faster, and ollama seems to slow down when not refreshed every so often
- personality control
  - we want SID to be evil, but this is for entertainment, not real insult or harm
