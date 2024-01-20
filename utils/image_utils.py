import logging
import base64
import io
import json
from pydantic import BaseModel, Field
import streamlit as st
from openai import OpenAIError
from dependencies import get_openai_client
from PIL import Image

# Create the OpenAI client
client = get_openai_client()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if "image_list" not in st.session_state:
    st.session_state["image_list"] = []

# Decode Base64 JSON to Image
def decode_image(b64_json):
    data = json.loads(b64_json)
    image_data = base64.b64decode(data['image'])
    return Image.open(io.BytesIO(image_data))

class ImageRequest(BaseModel):
    """ Image Request Model """
    prompt: str = Field(..., title="Prompt", description="The prompt to generate an image from.")

async def generate_image(prompt : str):
    """ Generate an image from the given image request. """
    logger.debug(f"Generating image for prompt: {prompt}")
    image_list = []
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-2",
            size="1024x1024",
            quality="standard",
            n=3,
            response_format="b64_json"
        )
        for i in range(len(response.data)):
            logger.debug(f"Image {i}: {response.data[i].b64_json}")
            image_list.append(decode_image(response.data[i].b64_json))

        st.session_state["image_list"] = image_list

        return image_list

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}
