from collections import deque
import io
import json
import os
import queue
import requests
import simpleaudio as sa
import sounddevice as sd
import soundfile as sf
import subprocess
import threading
from vosk import Model, KaldiRecognizer
vosk_speech_to_text = KaldiRecognizer(Model("vosk-model-small-en-us-0.15"), 16000)


class SIDClient:
	"""Client to run interactive SID session"""
	def __init__(self, short_term_memory: str = "short_term_memory", chatsize = 10):
		self.listening = True
		self.audio_queue = queue.Queue()
		self.chat = deque(maxlen=chatsize)
		self.actions = []
		self.short_term_memory = short_term_memory

	def listen(self, audio_data, *args) -> None:
		"""callback function for sounddevice listener"""
		if self.listening: self.audio_queue.put(bytes(audio_data))

	def hear(self, text: str, keyword: str = "yes") -> bool:
		"""returns whether the input detection module result contains the detection keyword"""
		data = {"text": text, "chat": str(list(self.chat))}
		response = requests.post(f'{os.environ["SID_SERVER"]}/detect_input/', data=data, timeout=20)
		return any(keyword in line.decode('utf-8').lower() for line in response.iter_lines())

	def speak(self, text: str) -> None:
		"""run the speak module remotely"""
		data = {"text": text}
		response = requests.post(f'{os.environ["SID_SERVER"]}/speak/', data=data, timeout=20)
		audio_data = io.BytesIO()
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				audio_data.write(chunk)
		audio_data.seek(0)
		audio_array, sample_rate = sf.read(audio_data, dtype='int16')
		play_obj = sa.play_buffer(audio_array, 1, 2, sample_rate)
		play_obj.wait_done()

	def react(self) -> None:
		"""to react is to act if an audio input is detected"""
		if self.listening and vosk_speech_to_text.AcceptWaveform(self.audio_queue.get()):
			print("Current chat:\n\n", "\n".join(self.chat), "\n######################")
			user_message = json.loads(vosk_speech_to_text.Result())["text"]
			if user_message != "" and self.hear(user_message):
				self.chat.append(f"user: {user_message}")
				self.act()

	def act(self) -> None:
		"""act based on most recent user message in chat (default: 'respond')"""
		modules = ["search", "calculate", "roast"]
		s = self.chat[-1]
		module = next((m for m in modules if m in s and "user:" in s), "respond")
		request = f'{os.environ["SID_SERVER"]}/{module}/'
		if module == "roast":
			image_filename = f"{self.short_term_memory}/view.jpg"
			subprocess.run(f"libcamera-still -o {image_filename} --awb auto", shell=True)
			with open(image_filename, "rb") as f:
				response = requests.post(request, files={"image": f}, timeout=20)
		else:
			data = {"chat": str(list(self.chat))}
			print("requesting server module", module, "with data:\n", data)
			response = requests.post(request, data=data, timeout=20)
		result = ''.join([line.decode('utf-8') for line in response.iter_lines()])
		self.actions.append({"status": "done", "result": result})

	def acknowledge(self) -> None:
		"""if any actions are done, speak aloud the result"""
		for action in self.actions:
			if action["status"] == "done":
				self.chat.append(f"robot: {action['result']}")
				self.speak(action["result"])
				action["status"] = "acknowledged"

	def main_loop(self) -> None:
		while True:
			self.react()
			self.acknowledge()


if __name__ == "__main__":
	sid_client = SIDClient()
	threading.Thread(target=sid_client.main_loop).start()
	with sd.RawInputStream(callback=sid_client.listen, samplerate=16000, channels=1, dtype="int16"):
		print("Recording...")
		while True:
			pass
			