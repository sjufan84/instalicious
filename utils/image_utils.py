import logging
from pydantic import BaseModel, Field
from dependencies import get_openai_client
from PIL import Image
import requests

# Create the OpenAI client
client = get_openai_client()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImageRequest(BaseModel):
    """ Image Request Model """
    prompt: str = Field(..., title="Prompt", description="The prompt to generate an image from.")

async def generate_image(prompt : str):
    """ Generate an image from the given image request. """
    logger.debug(f"Generating image for prompt: {prompt}")

    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-2",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        logger.debug(f"Image URL: {image_url}")

        # Convert the image to a PIL image
        image = Image.open(requests.get(image_url, stream=True).raw)
        logger.debug("Image successfully converted to PIL image")

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}

    # Return the image response as a string
    return {"image": image, "image_url": image_url}
