import ollama
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model_id = "vikhyatk/moondream2"
revision = "2024-03-13"
moondream = AutoModelForCausalLM.from_pretrained(
    model_id, trust_remote_code=True, revision=revision, torch_dtype=torch.float16
).to(device)
moondream_tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)


def describe_image(image_filename, model="moondream", focus="", debug=True):
    prompt = f"""What's going on? Respond with 1 or 2 sentences. Apply the following focus: {focus}"""
    if "moondream" in model:
        answer = moondream.answer_question(
            moondream.encode_image(Image.open(image_filename)),
            prompt,
            moondream_tokenizer
        )
        yield answer
    elif "llava" in model:
        llava_response = ollama.generate(
            'llava',
            prompt,
            images=[image_filename],
            stream=True,
            options=ollama.Options(num_predict=100, temperature=0.0)
        )
        for chunk in llava_response:
            if debug: print(chunk['response'], end='', flush=True)
            yield chunk['response']
