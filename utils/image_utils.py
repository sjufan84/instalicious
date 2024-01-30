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

if "generated_images" not in st.session_state:
    st.session_state["generated_images"] = []
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

async def generate_dalle3_image(prompt : str):
    """ Generate an image from the given image request. """
    logger.debug(f"Generating image for prompt: {prompt}")
    logger.debug(f"Image model: {st.session_state['image_model']}")
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-3",
            size=f"{st.session_state['size_choice']}",
            quality="standard",
            n=1,
            response_format="b64_json"
        )
        returned_image = response.data[0].b64_json[:100]
        logger.debug(f"Returned image: {returned_image}")
        decoded_image = decode_image(image_data=response.data[0].b64_json, image_name="image.png")
        logging.debug(f"Decoded image: {decoded_image}")

        return decoded_image

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}

async def generate_dalle2_images(prompt : str):
    """ Generate an image from the given image request. """
    image_list = []
    logger.debug(f"Generating images for prompt: {prompt}")
    # Generate the image
    try:
        response = client.images.generate(
            prompt=prompt,
            model="dall-e-2",
            size="1024x1024",
            n=3,
            response_format="b64_json"
        )
        for i in range(3):
            returned_image = response.data[i].b64_json[:100]
            logger.debug(f"Returned image: {returned_image}")
            decoded_image = decode_image(image_data=response.data[i].b64_json, image_name=f"image{i}.png")
            image_list.append(decoded_image)
            logging.debug(f"Decoded image: {decoded_image}")

        st.session_state.generated_images = image_list
        return image_list

    except OpenAIError as e:
        logger.error(f"Error generating image: {e}")
        return {"error": str(e)}
