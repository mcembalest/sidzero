# SID Zero

SID Zero (Synthetic Information Diffusion v0.1) is a robot like the [Open Interpreter O1](https://github.com/OpenInterpreter/open-interpreter), albeit less capable and with a more malicious personality. It uses audio + visual I/O and language/multimodal models to chat with the user with awareness of their environment.

# Setup

## Client

The client maintains the user-robot interaction and runs the audio & visual I/O. We use a Raspberry Pi 4, connect a webcam for visual input, a micrphone for audio input, and a monitor for visual display & audio output.

### Installation
Install [ffmpeg](https://evermeet.cx/ffmeg/), a [vosk speech to text](https://alphacephei.com/vosk/models) and [piper text to speech](https://github.com/rhasspy/piper/blob/master/VOICES.md) model. Then, install client requirements:
```bash
pip install -r client_requirements.txt
```

Set environment variable `SID_SERVER` to the url of the computation server (e.g. for your desktop this could be `http://192.168...`)

Then, start the client
```bash
python client.py
```

## Server
The server runs the language/multimodal models. We use a windows desktop computer with a RTX 3060 GPU, over a [private home network](https://arcadian.cloud/windows/2022/12/08/how-to-allow-icmp-ping-through-windows-firewall/).

### Installation
Install server requirements:
```bash
pip install -r server_requirements.txt
```

Set environment variables for tool modules you want to use, e.g. `PPLX_API_KEY`, `WOLFRAM_CALCULATOR_APP_ID`, etc

Then, start the server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

# Capabilities

## Dialog

Uses mistral & llava to chat with the user, describe the camera view, and roast you based on your outfit

## Calculate

Uses the Wolfram API to answer numerical questions

## Search

Uses the Perplexity API to answer questions answerable with a quick internet search

# Models Used

- default LLM: `mistral:7b-instruct-v0.2-q4_0` with Ollama

- Online RAG LLM: `sonar-small-online` with the pplx api

- Multimodal vision-language model: `llava:7b-v1.6-mistral-q4_0` with Ollama

- Speech to text: `vosk-model-small-en-us-0.15` with vosk

- Text to speech: `en_US-lessac-medium` with piper

# Roadmap

- async client
  - we want the client to be able to launch a job that may take a while without blocking the chat
- latency improvements
  - the text to speech is relatively slow, and ollama slows down when not refreshed every so often
- personality control
  - we want SID to be evil, but this is for entertainment, not real insult or harm
