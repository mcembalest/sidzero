from collections import deque
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


def server_detection(modulename: str, text: str, chat: deque, detection_keyword: str = "yes") -> bool:
	"""returns whether the server response contains the detection keyword"""
	return any(
		line is not None and detection_keyword in line.decode('utf-8') 
		for line in get_server_response(modulename, {"text": text, "chat": str(list(chat))}).iter_lines()
	)


def server_message(modulename: str, chat: deque) -> str:
	"""return the response message from the server"""
	return ''.join([
		line.decode('utf-8') if line else '' 
		for line in get_server_response(modulename, {"chat": str(list(chat))}).iter_lines()
	])


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

	def module_launcher(self) -> None:
		"""launch jobs from keywords in most recent message in chat"""
		if "calculate" in self.chat[-1] and "user:" in self.chat[-1]:
			message_result = server_message("calculate", self.chat)
		elif "search" in self.chat[-1] and "user:" in self.chat[-1]:
			message_result = server_message("search", self.chat)
		else:
			message_result = server_message("dialog", self.chat)
		self.pending_jobs.append({"status": "done", "command": self.chat[-1], "result": message_result})

	def check_pending_jobs(self) -> None:
		"""if any jobs are done, speak aloud the result and log the finished job"""
		for job in [job for job in self.pending_jobs if job["status"] == "done"]:
			self.chat.append(f"robot: {job['message']}")
			self.speak(job["message"])
			self.finished_jobs.append(job)

	def main_loop(self) -> None:
		"""listen to the user, run jobs on a remote server, and speak aloud the results"""
		while True:
			if self.listening and vosk_speech_to_text.AcceptWaveform(self.audio_queue.get()):
				print("Current chat:", "\n".join(self.chat), "\n######################")
				user_message = vosk_speech_to_text.Result()["text"]
				if user_message != "" and server_detection("detect_input", user_message, self.chat):
					self.chat.append(f"user: {user_message}")
					self.module_launcher()
			self.check_pending_jobs()


if __name__ == "__main__":
	sid_client = SIDClient()
	threading.Thread(target=sid_client.main_loop).start()
	with sd.RawInputStream(callback=sid_client.listen, samplerate=16000, channels=1, dtype="int16"):
		print("Recording...")
		while True:
			pass
