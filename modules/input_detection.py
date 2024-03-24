import ollama

def detect_input(text: str, chat: str, debug=True):
    if debug: print("judging inputness...")
    mistral_system_prompt = """You are a classifier
You decide based on a chat context whether the new text is addressed from the user to the robot (named Sid) or not.
You never answer with any nonboolean text. You ONLY output 'Answer: yes' or 'Answer: no', NOTHING else.
"""
    mistral_prompt = f"""Chat so far: {chat}
New text: {text}
Is the new text addressed from the user to the robot?
Answer:"""

    ollama_response_generator = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'system','content': mistral_system_prompt},
            {'role': 'user','content': mistral_prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=5, temperature=0.0)
    )
    for chunk in ollama_response_generator:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']
