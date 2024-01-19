""" Main Instalicious Page """
import streamlit as st
import asyncio
from utils.image_utils import generate_image
from utils.post_utils import create_recipe_post, create_description_post
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        "current_post", "current_hashtags", "current_image_prompt", "current_image", "post_page",
        "current_model", "model_selection"
    ]
    default_values = [
        None, None, None, None, "post_home", "gpt-3.5-turbo-1106", "GPT-3.5"
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

init_session_variables()

# Define the callback function to update the session state
def set_model():
    if st.session_state["model_selection"] == 'GPT-3.5':
        st.session_state["current_model"] = "gpt-3.5-turbo-1106"
    elif st.session_state["model_selection"] == 'GPT-4':
        st.session_state["current_model"] = "gpt-4-1106-preview"

async def post_home():
    logger.debug("Entering post_home function")
    st.markdown("""##### I would like to generate a post from:""")

    post_type = st.selectbox(
        "Post Type",
        ("Existing Recipe", "Description of a recipe or restaurant experience")
    )
    logger.debug(f"Post type selected: {post_type}")

    if post_type == "Existing Recipe":
        post_input = st.text_area("Recipe Input", value="Paste your recipe here")
    else:
        post_input = st.text_area(
            "Description Input", value="Describe your recipe, dish, or restaurant experience here"
        )
    logger.debug(f"Post input: {post_input}")

    st.radio(
        ":rainbow[AI Model Selection]", options=["GPT-3.5", "GPT-4"], horizontal=True, index=None,
        key="model_selection", on_change=set_model)
    # st.write(f"Selected model: {st.session_state['model_selection']}")
    # st.write(f"Current model: {st.session_state['current_model']}")

    generate_post_button = st.button("Generate Post")
    logger.debug(f"Generate post button pressed: {generate_post_button}")

    if generate_post_button:
        if post_type == "Existing Recipe":
            with st.spinner("Generating your post. This may take a minutes or two,\
            but you can't rush greatness..."):
                logger.debug("Generating post from recipe...")
                post_response = await create_recipe_post(post_input)
                if post_response:
                    st.session_state["current_post"] = post_response["post"]
                    st.session_state["current_hashtags"] = post_response["hashtags"]
                    st.session_state["current_image_prompt"] = post_response["image_prompt"]
                    st.session_state.post_page = "display_post"
                    st.rerun()
        else:
            with st.spinner("Generating your post. This may take a minutes or two,\
            but you can't rush greatness..."):
                logger.debug("Generating post from description...")
                post_response = await create_description_post(post_input)
                if post_response:
                    st.session_state["current_post"] = post_response["post"]
                    st.session_state["current_hashtags"] = post_response["hashtags"]
                    st.session_state["current_image_prompt"] = post_response["image_prompt"]
                    st.session_state.post_page = "display_post"
                    st.rerun()

async def display_post():
    logger.debug("Entering display_post function")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("""##### Post:""")
        st.markdown(f"{st.session_state['current_post']}")
        st.text("")
        st.markdown("""##### Hashtags""")
        # Write the hashtags as a string
        for hashtag in st.session_state["current_hashtags"]:
            st.write(f":violet[#{hashtag}]")

    with col2:
        st.markdown("""##### Image:""")
        if not st.session_state.current_image:
            with st.spinner("Generating your image..."):
                st.session_state.current_image = await generate_image(
                    st.session_state["current_image_prompt"]
                )
        if st.session_state.current_image:
            st.image(st.session_state.current_image["image"], use_column_width=True)

    generate_new_post_button = st.button("Generate New Post")
    if generate_new_post_button:
        # Reset the session state
        st.session_state.current_post = None
        st.session_state.current_hashtags = None
        st.session_state.current_image_prompt = None
        st.session_state.current_image = None
        st.session_state.post_page = "post_home"
        st.session_state.model_selection = "GPT-3.5"
        st.session_state.current_model = "gpt-3.5-turbo-1106"
        st.rerun()

if st.session_state.post_page == "post_home":
    logger.debug("Running post_home function")
    asyncio.run(post_home())
elif st.session_state.post_page == "display_post":
    logger.debug("Running display_post function")
    asyncio.run(display_post())
