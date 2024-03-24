# SID Zero

SID (Synthetic Information Diffusion) is a robot like the [Open Interpreter O1](https://github.com/OpenInterpreter/open-interpreter), albeit with the unfortunate differences of having fewer capabilities and more of a malicious personality, and just being overall much worse.

SID uses language models, multimodal models, and audio + visual I/O to chat with the user with awareness of their environment.

The client maintains the user-robot interaction and runs the audio & visual I/O, while the server runs the language/multimodal models.

# Setup

## Client

We use a Raspberry Pi 4 with USB camera & microphone attachments.

### Installation
Install [ffmpeg](https://evermeet.cx/ffmeg/). Then, install client requirements:
```bash
pip install -r client_requirements.txt
```

Set environment variable `SID_SERVER` to the url of the computation server (e.g. for your desktop this could be `http://192.168...`)

Then, start the client
```bash
python client.py
```

## Server
We use a windows desktop computer with a RTX 3060 GPU, over a [private home network](https://arcadian.cloud/windows/2022/12/08/how-to-allow-icmp-ping-through-windows-firewall/).

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

- default LLM: `mistral:7b-instruct-v0.2-q4_0`

- Online RAG LLM: perplexity `sonar-small-online`

- Multimodal vision-language model: `llava:7b-v1.6-mistral-q4_0`

- Speech to text: `vosk-model-small-en-us-0.15`

- Text to speech: `piper --model en_US-lessac-medium`

