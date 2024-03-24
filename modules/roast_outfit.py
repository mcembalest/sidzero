from .describe_image import get_image_description
from .roast import get_roast


def respond_with_outfit_roast(image_filename: str = "img/tmp/received_image.jpg", debug=False):
    image_description_generator = get_image_description(
        image_filename,
        focus="""Shirt, pants, shoes, jacket, hat, makeup, hair, anything. Describe fashion and personality.
IMPORTANT: DO NOT TALK ABOUT THE ROOM OR THE ENVIRONMENT. ONLY DESCRIBE PEOPLE'S FASHION, CLOTHES, AND VIBE.""",
        debug=debug
    )
    image_description = ''
    for chunk in image_description_generator:
        image_description += chunk
    roast_generator = get_roast(image_description, debug=debug)
    for chunk in roast_generator:
        yield chunk
