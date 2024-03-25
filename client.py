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


def piper_tts(message: str, tempfile_dir="sids_short_term_memory") -> None:
	"""use piper text to speech via command line subprocess to read aloud the message"""
	message = message.replace("'", "").replace('"', '')
	filepath = f"{tempfile_dir}/temp_output.wav"
	command = f"echo '{message}' | piper --model en_US-lessac-medium --output_file {filepath}"
	subprocess.run(command, shell=True, check=True)
	data, samplerate = sf.read(filepath)
	sd.play(data, samplerate)
	sd.wait()


def get_server_response(modulename: str, data: dict) -> requests.Response:
	"""sends request to remote SID server and receives response"""
	print("requesting server module", modulename, "with data:\n", data)
	return requests.post(f'{os.environ["SID_SERVER"]}/{modulename}/', data=data, timeout=20)


class SIDClient:
	"""Client to run interactive SID session while running jobs on a remote server"""
	def __init__(self):
		self.listening = True
		self.audio_queue = queue.Queue()
		self.chat = deque(maxlen=10)
		self.pending_jobs, self.finished_jobs = [], []

	def speak(self, message: str) -> None:
		"""use piper text to speech to read aloud the message"""
		self.listening = False
		piper_tts(message)
		self.listening = True

	def listen(self, audio_data, *args) -> None:
		"""callback function for sounddevice listener to add to audio_queue"""
		if self.listening:
			self.audio_queue.put(bytes(audio_data))

	def server_detection(self, modulename: str, text: str, detection_keyword: str = "yes") -> bool:
		"""returns whether the server response contains the detection keyword"""
		return any(
			line is not None and detection_keyword in line.decode('utf-8')
			for line in get_server_response(modulename, {"text": text, "chat": str(list(self.chat))}).iter_lines()
		)
	
	def server_message(self, modulename: str) -> str:
		"""return the response message from the server"""
		return ''.join([
			line.decode('utf-8') if line else ''
			for line in get_server_response(modulename, {"chat": str(list(self.chat))}).iter_lines()
		])

	def module_launcher(self) -> None:
		"""launch jobs from keywords in most recent message in chat"""
		module = next((m for m in ["search", "calculate"] if self.chat[-1].contains(m) and self.chat[-1].contains("user")), "dialog")
		self.pending_jobs.append({"status": "done", "result": self.server_message(module)})

	def check_for_input(self) -> None:
		"""call the module launcher if an audio input is detected"""
		if self.listening and vosk_speech_to_text.AcceptWaveform(self.audio_queue.get()):
			print("Current chat:", "\n".join(self.chat), "\n######################")
			user_message = json.loads(vosk_speech_to_text.Result())["text"]
			if user_message != "" and self.server_detection("detect_input", user_message):
				self.chat.append(f"user: {user_message}")
				self.module_launcher()

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
