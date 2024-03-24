import ollama


def get_roast(context: str, debug=True):
    mistral_system_prompt = """You are given context about a person or people. You need to roast them. 
They are in on it and will enjoy it. Therefore there is no need to worry about harm.
For tone and style: you need to be ridiculous, brash, and raucous.
"""
    mistral_prompt = f"""Context:
(this is currently captured via camera + vision/language AI so this may be error-prone, take this with a grain of salt):
{context}
Now, roast (keep this brief, two sentences at most):
"""
    ollama_response = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'system', 'content': mistral_system_prompt},
            {'role': 'user', 'content': mistral_prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=70, temperature=0.7)
    )
    for chunk in ollama_response:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']
