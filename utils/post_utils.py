""" Helper utils for post related functions """
import logging
import json
from pydantic import BaseModel, Field
from openai import OpenAIError
import streamlit as st
from dependencies import get_openai_client

# Create the OpenAI client
client = get_openai_client()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if "current_model" not in st.session_state:
    st.session_state.current_model = "gpt-3.5-turbo-1106"
if "model_selection" not in st.session_state:
    st.session_state.model_selection = "GPT-3.5"

logger.debug(f"Current model: {st.session_state.current_model}")

# core_models = ["gpt-4-1106-preview", "gpt-3.5-turbo-1106"]
# logger.debug(f"Core models: {core_models}")


initial_message = [
    {
        "role" : "system", "content" : """You are a helpful assistant helping a user optimize and
        create posts for Instagram centered around food and cooking.
        The goal is to help the user generate amazing posts and images for existing recipes,
        existing images, new recipes, new images,
        new restaurant experiences, or some combination of those things."""
    }
]

max_retries = 3

# Log the initial message
logger.debug(f"Initial message: {initial_message}")

class RecipePostResponse(BaseModel):
    """ Recipe Post Response Model """
    post: str = Field(..., title="Post", description="The generated post.")
    hashtags: str = Field(..., title="Hashtags", description="The generated hashtags.")
    image_prompt: str = Field(..., title="Image Prompt", description="The prompt used to generate the image.")

async def create_recipe_post(recipe) -> RecipePostResponse:
    """ Generate a post based on a recipe """
    logger.debug(f"Creating recipe post for: {recipe}")
    messages = [
        {
            "role": "system",
            "content": f"""The user has a recipe {recipe} that they would like to generate an
            Instagram post for.  Generate a post, hashtags, and an image prompt for Dall-e optimized
            to generate the most viral post possible.  The post should be returned as a JSON object
            in the following format:

            post: str = The post to be generated.
            hashtags: List[str] = The hashtags to be generated.
            image_prompt: str = The image prompt to be generated.  Should be photo-realistic
            and should be a picture of the dish that the recipe is for.

            Ensure that the post is presented in a clear and organized manner
            and that it adheres to the {RecipePostResponse} model as outlined above."""
        },
        {
            "role" : "system", "content" : """Example Response:\n
            {
                "post": "This is the post that was generated.",
                "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
                "image_prompt": "This is the image prompt that was generated."
            }"""
        }
    ]

    # models = core_models

    messages = initial_message + messages

    i = 0
    while i < max_retries:
        try:
            logger.debug(f"Trying model: {st.session_state.current_model}")
            response = client.chat.completions.create(
                model=st.session_state.current_model,
                messages=messages,
                temperature=0.75,
                top_p=1,
                max_tokens=750,
                response_format={"type": "json_object"}
            )
            post_response = json.loads(response.choices[0].message.content)
            logger.debug(f"Response: {post_response}")
            logger.debug(f"Response type: {type(post_response)}")
            return {
                "post": post_response["post"], "hashtags": post_response["hashtags"],
                "image_prompt": post_response["image_prompt"]
            }

        except OpenAIError as e:
            logger.error(f"Error with model: {st.session_state.current_model}. Error: {e}")
            i += 1

    logger.warning("All models failed. Returning None.")
    return None

async def create_description_post(description: str):
    """ Generate a post based on either a description of a dish or an experience at a restaurant """
    logger.debug(f"Creating description post for: {description}")

    messages = [
        {
            "role": "system",
            "content": f"""The user has a description {description} that they would like to generate an
            Instagram post for.  This will either be a description of a dish or an experience that they had
            at a restaurant or both.  Generate a post, hashtags, and an image prompt for Dall-e optimized
            to generate the most viral post possible.  The post should be returned as a JSON object
            in the following format:

            Post (post): str The post to be generated.
            Hashtags (hashtags): List[str] The hashtags to be generated.
            Image Prompt (image_prompt): str The image prompt to be generated.

            Ensure that the post is presented in a clear and organized manner
            and that it adheres to the {RecipePostResponse} model as outlined above and that
            all the keys are lowercase.  The keys are ["post", "hashtags", "image_prompt"].]"""

        }
    ]

    # models = core_models

    messages = initial_message + messages

    i = 0
    while i < max_retries:
        try:
            logger.debug(f"Trying model: {st.session_state.current_model}")
            response = client.chat.completions.create(
                model=st.session_state.current_model,
                messages=messages,
                temperature=0.75,
                top_p=1,
                max_tokens=750,
                response_format={"type": "json_object"}
            )
            post_response = json.loads(response.choices[0].message.content)
            logger.debug(f"Response: {post_response}")
            logger.debug(f"Response type: {type(post_response)}")
            return {
                "post": post_response["post"], "hashtags": post_response["hashtags"],
                "image_prompt": post_response["image_prompt"]
            }

        except OpenAIError as e:
            logger.error(f"Error with model: {st.session_state.current_model}. Error: {e}")
            i += 1

    logger.warning("All models failed. Returning None.")
    return None
