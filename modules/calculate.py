import ollama
import os
import requests

def wolfram_api_call(appid, input_query, debug=True):
    base_url = "http://api.wolframalpha.com/v1/result"
    wolfram_response = requests.get(base_url, params={'appid': appid,'i': input_query})
    if debug: print(wolfram_response.text)
    return wolfram_response.text

def wolfram_calculator(query, debug=True):
    print("starting wolfram calculation...")
    return wolfram_api_call(os.environ["WOLFRAM_CALCULATOR_APP_ID"], query, debug=debug)

def wolfram_full_answer_search(query, debug=True):
    return wolfram_api_call(os.environ["WOLFRAM_ANSWER_APP_ID"], query, debug=True)

def respond_to_calculator_result(chat: str, calculator_result: str, debug=True):
    if debug: print("responding to calculator result...")
    prompt = f"""Chat so far: {chat}
Calculator result: {calculator_result}
(the user will not see the calculator result, so answer their question by telling them what you saw in the calculator result.)
Your response (answer the user AS BRIEFLY AS POSSIBLE based on the chat context, you only have a sentence or two before you run out of tokens and you can always say something else next time, and you must use info from the calculator result to answer the query or explain you cannot answer):"""

    ollama_response_generator = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'user','content': prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=75, temperature=0.0)
    )
    for chunk in ollama_response_generator:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']

def respond_with_calculate(chat: str, debug=True):
    wolfram_response = wolfram_calculator(chat, debug=debug)
    if 'did not understand' in wolfram_response:
        wolfram_response = wolfram_full_answer_search(chat, debug=debug)
    response_generator = respond_to_calculator_result(
        chat,
        wolfram_response,
        debug=debug
    )
    for chunk in response_generator:
        yield chunk
