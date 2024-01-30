""" Main Instalicious Page """
import streamlit as st
import asyncio
import io
from streamlit_extras.stylable_container import stylable_container
from utils.image_utils import generate_dalle3_image
from utils.post_utils import create_post, alter_image
import logging
import base64

# Import Google Font in Streamlit CSS
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css?family=Anton');
        @import url('https://fonts.googleapis.com/css2?family=Arapey&display=swap');
    </style>
    """,
    unsafe_allow_html=True
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        "image_model", "user_image_string", "generate_image", "size_choice",
        "current_post", "current_hashtags", "current_image_prompt", "post_page", "generated_image"
    ]
    default_values = [
        "dall-e-3", None, False, "1024x1024", None, None, None, "post_home",
        None
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_session_variables():
    session_vars = [
        "image_model", "is_user_image", "user_image_string", "generate_image", "size_choice",
        "current_post", "current_hashtags", "current_image_prompt", "generated_image", "post_page"
    ]
    for var in session_vars:
        if var in st.session_state:
            del st.session_state[var]

init_session_variables()

# Function to encode the image
async def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def save_image(image, path="image.png"):
    image.save(path)

def display_image(image):
    st.image(image, use_column_width=True)

# Step 4: Create Download Link
def get_image_download_link(image, filename="downloaded_image.png"):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return st.download_button(
        label="Download Image",
        data=buffered.getvalue(),
        file_name=filename,
        mime="image/png",
        use_container_width=True
    )

async def post_home():
    image_string = None
    with stylable_container(
        key="post-home-container",
        css_styles="""
                h1 {
                    color: #000000;
                    font-size: 4em;
                    text-align: center;
                    font-family: 'Anton', sans-serif;
                }
                p {
                    color: #000000;
                    font-size: 1em;
                    text-align: center;
                    font-family: 'Arapey', serif;
                }
        """,
    ):
        # Create a centered header using HTML with bold font
        st.markdown(
            """<h1><b>INSTALICIO.US</b></h1>""", unsafe_allow_html=True
        )
        # Create a centered subheader using HTML with bold font
        st.markdown(
            """<p>
            Transform any meal into a stunning,
            Insta-worthy post... instantly.</p>""", unsafe_allow_html=True
        )
    st.text("")
    st.text("")

    with stylable_container(
        key="post-main",
        css_styles="""
        {
            font-family: 'Arapey', serif;
            font-size: 1em;
        }
        """,
    ):
        picture_mode = st.selectbox(
            '###### 📸 Snap a Pic, 📤 Upload an Image, or Let Us Generate One For You!',
            ("Snap a pic", "Upload an image", "Let Us Generate One For You"), index=None,
        )
        if picture_mode == "Snap a pic":
            uploaded_image = st.camera_input("Snap a pic")
            if uploaded_image:
                # Convert the image to a base64 string
                image_string = await encode_image(uploaded_image)
                st.session_state.user_image_string = image_string
                # Set the session state image to base64 string
                st.write(f"User Snapped Image: {st.session_state.user_image_string[:100]}")

        elif picture_mode == "Upload an image":
            # Show a file upoloader that only accepts image files
            uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
            # Convert the image to a base64 string
            if uploaded_image:
                image_string = await encode_image(uploaded_image)
                st.session_state.user_image_string = image_string
                st.write(f"Uploaded Image: {st.session_state.user_image_string[:100]}")
        elif picture_mode == "Let Us Generate One For You":
            st.session_state.generate_image = True

        st.text("")
        post_prompt = st.text_area("""###### Tell Us About This Recipe or Meal""")

    size_choice = st.radio(
        "Select your desired format:", options=["Square", "Stories"], horizontal=True, index=None,
    )
    if size_choice == "Square":
        st.session_state.size_choice = "1024x1024"
    elif size_choice == "Stories":
        st.session_state.size_choice = "1024x1792"
    st.write(f"Size choice: {st.session_state.size_choice}")
    generate_post_button = st.button("Generate Post", type="primary")
    logger.debug(f"Generate post button pressed: {generate_post_button}")
    if generate_post_button:
        if picture_mode and post_prompt != "" and size_choice and st.session_state.user_image_string:
            with st.spinner("Generating your post. This may take a minute..."):
                image_prompt = await alter_image(post_prompt, st.session_state.user_image_string)
                st.write(f"Image prompt: {image_prompt}")
                st.session_state.current_image_prompt = image_prompt
                post = await create_post(prompt=post_prompt, post_type="no_image")
                st.write(f"Post: {post}")
                st.session_state.current_post = post["post"]
                st.session_state.current_hashtags = post["hashtags"]
                st.session_state.post_page = "display_post"
                st.rerun()
        elif picture_mode and post_prompt != "" and size_choice and not st.session_state.user_image_string:
            with st.spinner("Generating your post. This may take a minute..."):
                post = await create_post(prompt=post_prompt, post_type="with_image")
                st.write(f"Post: {post}")
                st.stop()
                st.session_state.current_post = post["post"]
                st.session_state.current_hashtags = post["hashtags"]
                st.session_state.current_image_prompt = post["image_prompt"]
                st.session_state.post_page = "display_post"
                st.rerun()
        else:
            st.warning("Please make an image choice, enter a description, and select your preferred format.")

    # need_help_button = st.button("Need Help? (Coming Soon)" , type="primary", disabled=True)
    # about_button = st.button("About (Coming Soon)", type="primary", disabled=True)

async def display_post():
    """ Display the post and the images """
    with stylable_container(
        key="display-post-container",
        css_styles="""
                h1 {
                    color: #000000;
                    font-size: 4em;
                    text-align: center;
                    font-family: 'Anton', sans-serif;
                }
                p {
                    color: #000000;
                    font-size: 1em;
                    text-align: center;
                    font-family: 'Arapey', serif;
                }
        """,
    ):
        # Create a centered header using HTML with bold font
        st.markdown("""
        <h1 style='text-align: center; color: #000000;
        font-size:4em'><b>INSTALICIO.US</b></h1>""", unsafe_allow_html=True)

    st.text("")

    with stylable_container(
        key = "display-post-main",
        css_styles = """
        {
            font-family: 'Arapey', serif;
            font-size: 1em;
            background-color: #FFFFFF;
            text-align: left;
            border-radius: 10px;
        }
        """,
    ):
        logger.debug("Entering display_post function")
        # Convert the list of hashtags to a string with a space in between and
        # a "#" in front of each hashtag
        hashtags_string = " ".join(["#" + hashtag for hashtag in st.session_state["current_hashtags"]])
        # Use the post-content style to display the post
        st.markdown(f'''
            <p style="font-weight: semibold; margin: 15px;">{st.session_state['current_post']}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.text("")
        st.markdown(f'''
            <p style="color:#203590; font-weight: bold; margin: 15px 15px 30px 15px;">{hashtags_string}</p>
            </div>
        ''', unsafe_allow_html=True)

    st.text("")
    st.text("")

    st.markdown(
        """<p style='text-align: center; color: #000000;
        font-size: 20px; font-family:"Arapey";'>Pick Instalicious Image(s)</p>""", unsafe_allow_html=True
    )
    if not st.session_state.image_list:
        with st.spinner("Generating your images..."):
            st.session_state.generated_image = await generate_dalle3_image(
                st.session_state["current_image_prompt"]
            )
    if st.session_state.generated_image:
        with stylable_container(
            key="image-display-container",
            css_styles="""
                    button {
                        color: #ffffff;
                        background-color: #f0d1b7;
                    }
            """,
        ):
            # If the image model is dall-e-3, display 1 image
            logger.debug(f"Your Image: {st.session_state.generated_image}")
            display_image(st.session_state.generated_image)
            get_image_download_link(st.session_state.generated_image, filename="instalicious_image.png")

    st.markdown(
        """
        <p style="text-align: left; color: #000000; font-size:1em; margin-top: 30px; margin-left: 5px;">
        Want to Start Over?</p>
        """, unsafe_allow_html=True
    )
    generate_new_post_button = st.button("Generate New Post", type="primary")
    if generate_new_post_button:
        # Reset the session state
        reset_session_variables()

if st.session_state.post_page == "post_home":
    logger.debug("Running post_home function")
    asyncio.run(post_home())
elif st.session_state.post_page == "display_post":
    logger.debug("Running display_post function")
    asyncio.run(display_post())