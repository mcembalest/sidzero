from collections import deque
import json
import os
import queue
import requests
import sounddevice as sd
import soundfile as sf
import subprocess
import threading
from vosk import Model, KaldiRecognizer
vosk_speech_to_text = KaldiRecognizer(Model("vosk-model-small-en-us-0.15"), 16000)


def piper_tts(message: str, filepath: str) -> None:
	"""use piper text to speech via command line subprocess to read aloud the message"""
	message = message.replace("'", "").replace('"', '')
	command = f"echo '{message}' | piper --model en_US-lessac-medium --output_file {filepath}"
	subprocess.run(command, shell=True, check=True)
	data, samplerate = sf.read(filepath)
	sd.play(data, samplerate)
	sd.wait()


class SIDClient:
	"""Client to run interactive SID session while running jobs on a server"""
	def __init__(self):
		self.listening = True
		self.audio_queue = queue.Queue()
		self.chat = deque(maxlen=10)
		self.pending_jobs, self.finished_jobs = [], []
		self.modules = ["search", "calculate", "roast"]
		self.short_term_memory_dir = "sids_short_term_memory"

	def speak(self, message: str) -> None:
		"""use piper text to speech to read aloud the message"""
		self.listening = False
		piper_tts(message, f"{self.short_term_memory_dir}/speech.wav")
		self.listening = True

	def listen(self, audio_data, *args) -> None:
		"""callback function for sounddevice listener to add to audio_queue"""
		if self.listening: self.audio_queue.put(bytes(audio_data))

	def hear(self, text: str, keyword: str = "yes") -> bool:
		"""returns whether the input detection module result contains the detection keyword"""
		data = {"text": text, "chat": str(list(self.chat))}
		response = requests.post(f'{os.environ["SID_SERVER"]}/detect_input/', data=data, timeout=20)
		return any(keyword in line.decode('utf-8').lower() for line in response.iter_lines())

	def check_for_input(self) -> None:
		"""call the module launcher if an audio input is detected"""
		if self.listening and vosk_speech_to_text.AcceptWaveform(self.audio_queue.get()):
			print("Current chat:\n\n", "\n".join(self.chat), "\n######################")
			user_message = json.loads(vosk_speech_to_text.Result())["text"]
			if user_message != "" and self.hear(user_message):
				self.chat.append(f"user: {user_message}")
				self.module_launcher()

	def module_launcher(self) -> None:
		"""launch jobs from keywords in most recent message in chat (default: 'respond')"""
		module = next(
			(m for m in self.modules if m in self.chat[-1] and "user:" in self.chat[-1]), 
			"respond"
		)
		request = f'{os.environ["SID_SERVER"]}/{module}/'
		if module == "roast":
			image_filename = f"{self.short_term_memory_dir}/view.jpg"
			subprocess.run(f"libcamera-still -o {image_filename} --awb auto", shell=True)
			with open(image_filename, "rb") as f:
				response = requests.post(request, files={"image": f}, timeout=20)
		else:
			data = {"chat": str(list(self.chat))}
			print("requesting server module", module, "with data:\n", data)
			response = requests.post(request, data=data, timeout=20)
		result = ''.join([line.decode('utf-8') for line in response.iter_lines()])
		self.pending_jobs.append({"status": "done", "result": result})

	def check_for_output(self) -> None:
		"""if any jobs are done, speak aloud the result and log the finished job"""
		for job in [job for job in self.pending_jobs if job["status"] == "done"]:
			self.chat.append(f"robot: {job['result']}")
			self.speak(job["result"])
			self.pending_jobs.remove(job)
			self.finished_jobs.append(job)

	def main_loop(self) -> None:
		"""check for inputs (audio) & outputs (server responses) to be processed"""
		while True:
			self.check_for_input()
			self.check_for_output()


if __name__ == "__main__":
	sid_client = SIDClient()
	threading.Thread(target=sid_client.main_loop).start()
	with sd.RawInputStream(callback=sid_client.listen, samplerate=16000, channels=1, dtype="int16"):
		print("Recording...")
		while True:
			pass
			