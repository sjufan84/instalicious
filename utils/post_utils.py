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

if "vision_status" not in st.session_state:
    st.session_state["vision_status"] = "not_used"
if "vision_prompt" not in st.session_state:
    st.session_state["vision_prompt"] = ""

class ImagePostResponse(BaseModel):
    """ Image Post Response Model """
    post: str = Field(..., title="post", description="The generated post text.")
    hashtags: str = Field(..., title="hashtags", description="The generated hashtags.")
    image_prompt: str = Field(..., title="image_prompt", description="The prompt used to generate the image.")

class TextPostResponse(BaseModel):
    """ Text Post Response Model """
    post: str = Field(..., title="post", description="The generated post text.")
    hashtags: str = Field(..., title="hashtags", description="The generated hashtags.")

initial_message = [
    {
        "role" : "system", "content" : """You are a helpful assistant helping a user optimize and
        create posts for Instagram centered around food and cooking.
        The goal is to help the user generate amazing posts and images for existing recipes,
        existing images, new recipes, new images,
        new restaurant experiences, or some combination of those things."""
    }
]

async def get_messages(post_option: str, prompt: str):
    """ Get the messages for the post option """
    messages = []
    if post_option == "with_image":
        messages = [
            {
                "role": "system",
                "content": f"""The user would like for you to generate an Instagram post optimized
                for engagement and virality based on the prompt {prompt} they have given.  This could
                be a recipe, a description of a dish, a description of a restaurant experience, etc.
                If it is a recipe, you do not need to return the recipe itself,
                just the post text and hashtags. You will create the post, hashtags, and an image prompt
                for dall-e.

                For the image prompt, imagine that you are a professional food photographer,
                create an prompt for dall-e that best conveys the user's prompt
                for maxiumum engagement on Instagram with the characteristics
                of a hyper-realistic photo.  Think about the optimal focus of the image,
                the desired photographic effects
                (i.e. shallow depth of field, natural lighting), composition
                (rule of thirds, close-up shot),
                sensory details,
                technical specifications (i.e. 50 mm prime lens, f/2.8 aperture),
                emotional and aesthetic appeal (i.e. warm, inviting glow,
                comfort, homemade quality) and other considerations that a professional
                photographer would take into account.  Again, the goal is to create the
                most hyper-realistic and true to life photograph that
                is geared toward accomodating the user's
                prompt and the uploaded image. Make sure that there
                are no hands in the generated photo, and that the food is the highlight of the photo.
                Keep the prompt as concise as possible while still being
                descriptive enough to generate the desired photo.

                Your response should be returned as a JSON object in the following format:

                post: str = The post to be generated.
                hashtags: List[str] = The hashtags to be generated.
                image_prompt: str = An image prompt to send to dall-e for generation based on the user prompt.
                Should be photo-realistic and life-like as possible.

                Ensure that the post is presented in a clear and organized manner
                and that it adheres to the {ImagePostResponse} schema as outlined above."""
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

        total_messages = initial_message + messages

    elif post_option == "no_image":
        messages = [
            {
                "role": "system", "content": f"""The user would like
                for you to generate an Instagram post optimized
                for engagement and virality based on the prompt {prompt} they have given.  This could
                be a recipe, a description of a dish, a description of a restaurant experience, etc.
                Your response should be returned as a JSON object in the following format:

                post: str = The post to be generated.
                hashtags: List[str] = The hashtags to be generated.

                Ensure that the post is presented in a clear and organized manner
                and that it adheres to the {TextPostResponse} schema as outlined above."""
            },
            {
                "role": "system", "content": """Example Response:\n
                {
                    "post": "This is the post text that was generated.",
                    "hashtags": ["hashtag1", "hashtag2", "hashtag3"]
                }"""
            }
        ]

        total_messages = initial_message + messages

    logger.debug(f"Total messages: {total_messages}")

    return total_messages


async def create_post(post_type: str, prompt: str):
    """ Generate a post based on a user prompt"""
    messages = await get_messages(post_type, prompt)
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
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
            "image_prompt": post_response["image_prompt"] if "image_prompt" in post_response else None
        }

    except OpenAIError as e:
        logger.error(f"Error with model: gpt-4-turbo-preview. Error: {e}")
        return f"Error with model: gpt-4-preview. Error: {e}"

    logger.warning("All models failed. Returning None.")
    return None

async def alter_image(prompt: str, image_url: str):
    """ Generate a new dall-e prompt based on the user prompt and the image """
    st.session_state.vision_status = "used"
    messages = [
        {
            "role": "system", "content": [
                {
                    "type" : "text", "text" : f"""The user has uploaded an
                    image and a prompt {prompt} that they
                    would like to convert into a viral Instagram post. The prompt may be a recipe, a dish,
                    a description of a restaurant experience, etc.
                    Imagining that you are a professional photographer,
                    create an prompt for dall-e that takes the original image and
                    optimizes it for maxiumum engagement on Instagram with the characteristics
                    of a hyper-realistic photo.  Think about the optimal focus of the image,
                    the desired photographic effects
                    (i.e. shallow depth of field, natural lighting), composition
                    (rule of thirds, close-up shot),
                    sensory details,
                    technical specifications (i.e. 50 mm prime lens, f/2.8 aperture),
                    emotional and aesthetic appeal (i.e. warm, inviting glow,
                    comfort, homemade quality) and other considerations that a professional
                    photographer would take into account.  Again, the goal is to create the
                    most hyper-realistic and true to life photograph that
                    is geared toward accomodating the user's
                    prompt and the uploaded image. Make sure that there
                    are no hands in the generated photo, and that the food is the highlight of the photo.
                    Keep the prompt as concise as possible while still being
                    descriptive enough to generate the desired photo."""
                }
            ]
        },
        {
            "role" : "system", "content" : [
                {
                    "type" : "text", "text" : "This is the image that was passed to you:"
                },
                {
                    "type" : "image_url", "image_url" : f"""data:image/jpeg;base64,
                    {st.session_state.user_image_string}"""
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=250,
        )
        logger.debug(f"Response: {response}")
        prompt_response = response.choices[0].message.content
        logger.debug(f"Prompt response: {prompt_response}")
        st.session_state.vision_prompt = prompt_response
        return prompt_response
    except OpenAIError as e:
        logger.error(f"Error generating prompt for image alteration: {e}")
        return None

async def get_image_prompt(post_prompt: str):
    messages = [
        {
            "role": "system", "content": f"""The user has provided a prompt {post_prompt} that they
                    would like to convert into a viral Instagram post.
                    The prompt may be a recipe, a dish,
                    a description of a restaurant experience, etc.
                    Imagining that you are a professional food photographer,
                    create an prompt for dall-e that best conveys the user's prompt
                    for maxiumum engagement on Instagram with the characteristics
                    of a hyper-realistic photo.  Think about the optimal focus of the image,
                    the desired photographic effects
                    (i.e. shallow depth of field, natural lighting), composition
                    (rule of thirds, close-up shot),
                    sensory details,
                    technical specifications (i.e. 50 mm prime lens, f/2.8 aperture),
                    emotional and aesthetic appeal (i.e. warm, inviting glow,
                    comfort, homemade quality) and other considerations that a professional
                    photographer would take into account.  Again, the goal is to create the
                    most hyper-realistic and true to life photograph that
                    is geared toward accomodating the user's
                    prompt and the uploaded image. Make sure that there
                    are no hands in the generated photo, and that the food is the highlight of the photo.
                    Keep the prompt as concise as possible while still being
                    descriptive enough to generate the desired photo."""
        }
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            max_tokens=250,
        )
        logger.debug(f"Response: {response}")
        prompt_response = response.choices[0].message.content
        logger.debug(f"Prompt response: {prompt_response}")
        return prompt_response
    except OpenAIError as e:
        logger.error(f"Error generating prompt for image generation: {e}")
        return None

async def alter_image2(prompt: str, image_url: str):
    """ Generate a new dall-e prompt based on the user prompt and the image """
    st.session_state.vision_status = "used"
    messages = [
        {
            "role": "system", "content": [
                {
                    "type" : "text", "text" : f"""The user has uploaded an
                    image and a prompt {prompt} that they
                    would like to convert into a viral Instagram post. The prompt may be a recipe, a dish,
                    a description of a restaurant experience, etc.
                    Imagining that you are a professional food photographer,
                    create an prompt for dall-e that takes the original image and
                    optimizes it for maxiumum engagement on Instagram with the characteristics
                    of a hyper-realistic photo, taking into consdideration the various facets of photography
                    necessary to create stunning food photos.  Make sure that there
                    are no hands in the generated photo, and
                    that the food is the highlight of the photo.
                    Keep the prompt as concise and focused."""
                }
            ]
        },
        {
            "role" : "system", "content" : [
                {
                    "type" : "text", "text" : "This is the image that was passed to you:"
                },
                {
                    "type" : "image_url", "image_url" : f"""data:image/jpeg;base64,
                    {st.session_state.user_image_string}"""
                }
            ]
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=250,
        )
        logger.debug(f"Response: {response}")
        prompt_response = response.choices[0].message.content
        logger.debug(f"Prompt response: {prompt_response}")
        st.session_state.vision_prompt = prompt_response
        return prompt_response
    except OpenAIError as e:
        logger.error(f"Error generating prompt for image alteration: {e}")
        return None

