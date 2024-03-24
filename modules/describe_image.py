import ollama


def get_image_description(image_filename, focus="", debug=True):
    llava_prompt = f"""You need to describe the image you see in front of you with the following focus:
{focus}
Now your description of the provided image:
"""
    llava_response = ollama.generate(
        'llava', 
        llava_prompt, 
        images=[image_filename], 
        stream=True,
        options=ollama.Options(num_predict=100, temperature=0.0)
    )
    for chunk in llava_response:
        if debug: print(chunk['response'], end='', flush=True)
        yield chunk['response']
