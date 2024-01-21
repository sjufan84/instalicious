import logging
import base64
import io
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
if "image_model" not in st.session_state:
    st.session_state["image_model"] = "dall-e-2"
if "size_choice" not in st.session_state:
    st.session_state["size_choice"] = "1024x1024"

# Decode Base64 JSON to Image
def decode_image(image_data, image_name):
    """ Decode the image data from the given image request. """
    logger.debug(f"Decoding image: {image_data}")
    # Decode the image
    image_bytes = base64.b64decode(image_data)
    # Convert the bytes to an image
    image = Image.open(io.BytesIO(image_bytes))
    # Save the image
    image.save(image_name)
    return image

class ImageRequest(BaseModel):
    """ Image Request Model """
    prompt: str = Field(..., title="Prompt", description="The prompt to generate an image from.")

async def generate_image(prompt : str):
    """ Generate an image from the given image request. """
    logger.debug(f"Generating image for prompt: {prompt}")
    logger.debug(f"Image model: {st.session_state['image_model']}")
    image_list = []
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model=f"{st.session_state['image_model']}",
            size=f"{st.session_state['size_choice']}",
            quality="standard",
            n=1,
            response_format="b64_json"
        )
        for i in range(len(response.data)):
            logger.debug(f"Image {i}: {response.data[i].b64_json}")
            image_list.append(decode_image(image_data=response.data[i].b64_json, image_name=f"image{i}.png"))
            logger.debug(f"Image list: {image_list}")

        st.session_state["image_list"] = image_list
        logging.debug(f"Image list: {image_list}")
        return image_list

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}
