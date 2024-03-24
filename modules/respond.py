import ollama

def respond(chat: str, attitude: str, debug=True):
    if debug: print("responding...")
    mistral_system_prompt = f"""You are a malicious robot named Sid. 
You still follow instructions first, and give attitude second.
You respond with this attitude: {attitude}
"""
    mistral_prompt = f"""Chat so far: {chat}
Your response (answer the user AS BRIEFLY AS POSSIBLE based on the chat context, you only have a sentence or two before you run out of tokens and you can always say something else next time):"""

    ollama_response_generator = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'system','content': mistral_system_prompt},
            {'role': 'user','content': mistral_prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=70, temperature=0.7)
    )
    for chunk in ollama_response_generator:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']
