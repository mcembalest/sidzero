from modules import describe_image, detect_input, respond, respond_with_calculate, respond_with_search, speak
import simpleaudio as sa
import wave


def test_detect_input():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting detect_input module")
    snippets = ["doorbell", "Hey robot whats up", "burger", "What food is that?"]
    chats = [[], [], [], ["user: give me some food recs", "robot: oh i have a good suggestion food"]]
    for s, c in zip(snippets, chats):
        print('\n\n>>>>>', s, c)
        detection_generator = detect_input(s, c, debug=False)
        for chunk in detection_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_respond():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting respond module")
    chats = [
        ["user: Hey robot whats up"],
        [
            "user: give me some food recs",
            "robot: oh i have a good suggestion for food, but its really really spicy",
            "user: What food is that?"
        ]
    ]
    for c in chats:
        print('\n\n>>>>>', c)
        response_generator = respond(c, attitude = "mean, insulting", debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_respond_with_calculate():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting respond_with_calculate module")
    queries = ["how many 3s are in 2^16", 'how far is it from nyc to LA']
    for q in queries:
        print('\n\n>>>>>', q)
        response_generator = respond_with_calculate(q, debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_describe_image():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting describe_image module")
    image_files = ["img/test/kfc.jpg", "img/test/emerald_starters.jpg"]
    for img in image_files:
        print('\n\n>>>>>', img)
        response_generator = describe_image(img, focus="everything you can see")
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def test_search():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting search module")
    queries = [
        "what is the current status of nikki haley in the 2024 presidential election",
        "what did dune 2 get on rotten tomatoes",
        "when is half life 3 coming out"
    ]
    for q in queries:
        print('\n\n>>>>>', q)
        response_generator = respond_with_search(q, debug=False)
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print("\n\n***")


def play_audio(audio_data):
    # Read WAV data from the BytesIO object
    with wave.open(audio_data, 'rb') as wav_file:
        num_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frames = wav_file.readframes(wav_file.getnframes())

    # Play the audio using simpleaudio
    play_obj = sa.play_buffer(frames, num_channels, sample_width, sample_rate)
    play_obj.wait_done()


def test_speak():
    print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~\ntesting speak module")
    texts = [
        "Guess what! I just saw the lazy brown dog jumped over the quick fox",
        "Apples really are so crunchy and delicious in the summertime, aren't they?"
    ]
    for t in texts:
        print('\n\n>>>>>', t)
        play_audio(speak(t))
        print("\n\n***")


if __name__ == "__main__":
    test_speak()
