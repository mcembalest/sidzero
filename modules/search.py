import json
import ollama
import os
import requests

def perplexity_api_call(messages, model='sonar-small-online'):
    perplexity_response_generator = requests.post(
        "https://api.perplexity.ai/chat/completions", 
        json={
            "model": model,
            "messages": messages,
            "stream": True
        }, 
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "Bearer " + os.environ["PPLX_API_KEY"]
        })
    for chunk in perplexity_response_generator:
        yield chunk

def perplexity_search(query, debug=True):
    messages = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": query}
    ]
    buffer = ""
    last_complete_response = ""
    for chunk in perplexity_api_call(messages, model='sonar-small-online'):
        buffer += chunk.decode('utf-8')
        while '}\r\n\r\n' in buffer:
            end_index = buffer.find('}\r\n\r\n') + 1
            json_str = buffer[:end_index].replace('data: ', '').strip()
            buffer = buffer[end_index + 1:]
            try:
                json_obj = json.loads(json_str)
                if 'choices' in json_obj and json_obj['choices']:
                    last_complete_response = json_obj['choices'][0]['message']['content']
            except json.JSONDecodeError:
                pass
    return last_complete_response

def write_search_query(chat: str, debug=True):
    if debug: print("writing search query...")
    system_prompt = """You are a writer of an internet search query based on some transcript.
You never answer with any dialog. You ONLY output a search query as a question
e.g. 'Search Query: what are 2024 oscar best picture movies?' or 'Search Query: what are montreal hotel recommendations?', NOTHING else.
"""
    prompt = f"""Chat so far: 
{chat}
Search Query:"""
    ollama_response_generator = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'system','content': system_prompt},
            {'role': 'user','content': prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=25, temperature=0.0)
    )
    
    for chunk in ollama_response_generator:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']

def respond_to_search_result(chat: str, search_query: str, search_result: str, debug=True):
    if debug: print("responding to search...")
    system_prompt = """You are a malicious robot named Sid. 
You are given an array of search results (possibly empty) to a search query from a robot chat session
You still follow instructions first, and give attitude second.
"""
    prompt = f"""Chat so far: {chat}
Search query: {search_query}
Search result: {search_result}
(the user will not see the search result, so answer their question by telling them what you saw in the search result.)
Your response (answer the user AS BRIEFLY AS POSSIBLE based on the chat & search context, you only have a sentence or two before you run out of tokens and you can always say something else next time, and you must use info from the search result to answer the query or explain you cannot answer):"""

    ollama_response_generator = ollama.chat(
        model="mistral",
        messages=[
            {'role': 'system','content': system_prompt},
            {'role': 'user','content': prompt}
        ],
        stream=True,
        options=ollama.Options(num_predict=75, temperature=0.7)
    )
    for chunk in ollama_response_generator:
        if debug: print(chunk['message']['content'], end='', flush=True)
        yield chunk['message']['content']

def respond_with_search(chat: list[str], debug=False):
    search_query = ''
    for chunk in write_search_query(chat, debug=debug):
        search_query += chunk
    perplexity_response = perplexity_search(search_query, debug=debug)
    for chunk in respond_to_search_result(chat, search_query, perplexity_response, debug=debug):
        yield chunk
