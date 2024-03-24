from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from modules import detect_input, respond, respond_with_calculate, respond_with_outfit_roast, respond_with_search

app = FastAPI(debug=False)


async def stream_module_result(module_result):
    try:
        return StreamingResponse(module_result, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def save_image(image: UploadFile = File(...), image_filename:str = "img/tmp/received_image.jpg"):
    try:
        image_data = await image.read()
        with open(image_filename, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        raise Exception("Could not save image") from e


@app.post("/calculate/")
async def calculate_api(chat: str = Form(...)):
    return stream_module_result(respond_with_calculate(chat))


@app.post("/detect_input/")
async def detect_input_api(text: str = Form(...), chat: str = Form(...)):
    return stream_module_result(detect_input(text, chat))


@app.post("/respond/")
async def respond_api(chat: str = Form(...)):
    return stream_module_result(respond(chat, "malicious"))


@app.post("/roast_outfit/")
async def roast_outfit_api(image: UploadFile = File(...)):
    await save_image(image)
    return stream_module_result(respond_with_outfit_roast())


@app.post("/search/")
async def search_api(chat: str = Form(...)):
    return stream_module_result(respond_with_search(chat))
