""" Main Instalicious Page """
import streamlit as st
import asyncio
import io
from streamlit_extras.stylable_container import stylable_container
from utils.image_utils import generate_image
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

# Function to encode the image
async def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the session state
def init_session_variables():
    # Initialize session state variables
    session_vars = [
        "current_post", "current_hashtags", "current_image_prompt", "current_image", "post_page",
        "current_model", "model_selection", "generate_image", "image_choice", "image_list",
        "selected_images", "image_model", "size_choice"
    ]
    default_values = [
        None, None, None, None, "post_home", "gpt-3.5-turbo-1106", "GPT-3.5", False, False, [],
        [], "dall-e-2", None
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

st.session_state.image_model = "dall-e-3"

# Step 2: Save Image to File (optional if you only need to display it)
def save_image(image, path="image.png"):
    image.save(path)

# Step 3: Display Image in Streamlit
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
    image_url = None
    logger.debug("Entering post_home function")
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
    # Create a centered subheader using HTML with bold font
    # that says "Snap a pic or upload an image"
    # Use emojis for the camera and upload icons
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
            # Convert the image to a base64 string
            if uploaded_image:
                image_url = await encode_image(uploaded_image)
        elif picture_mode == "Upload an image":
            # Show a file upoloader that only accepts image files
            uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
            # Convert the image to a base64 string
            if uploaded_image:
                image_url = await encode_image(uploaded_image)
        elif picture_mode == "Let Us Generate One For You":
            st.session_state.generate_image = True
            st.session_state.image_choice = "Based on the prompt"
            image_url = None

        st.text("")

        post_prompt = st.text_area("""###### Tell Us About This Recipe or Meal""")

    size_choice = st.radio(
        "Select your desired format:", options=["Square", "Stories"], horizontal=True, index=None,
    )
    if size_choice == "Square":
        st.session_state.size_choice = "1024x1024"
    elif size_choice == "Stories":
        st.session_state.size_choice = "1024x1792"

    st.radio(
        ":rainbow[AI Model Selection] (This option is only for testing purposes @Babette)",
        options=["GPT-3.5", "GPT-4"], horizontal=True, index=None,
        key="model_selection", on_change=set_model
    )

    generate_post_button = st.button("Generate Post", type="primary")
    logger.debug(f"Generate post button pressed: {generate_post_button}")
    if generate_post_button:
        if picture_mode and post_prompt != "" and size_choice:
            if image_url:
                with st.spinner("Generating your post. This may take a minute..."):
                    image_prompt = await alter_image(post_prompt, image_url)
                    st.session_state.current_image_prompt = image_prompt
                    post = await create_post(prompt=post_prompt, post_type="no_image")
                    st.session_state.current_post = post["post"]
                    st.session_state.current_hashtags = post["hashtags"]
                    st.session_state.post_page = "display_post"
                    st.rerun()
            else:
                with st.spinner("Generating your post. This may take a minute..."):
                    post = await create_post(prompt=post_prompt, post_type="with_image")
                    st.session_state.current_post = post["post"]
                    st.session_state.current_hashtags = post["hashtags"]
                    st.session_state.current_image_prompt = post["image_prompt"]
                    st.session_state.post_page = "display_post"
                    st.rerun()
        else:
            st.warning("Please make an image choice, enter a description, and select your preferred format.")

    need_help_button = st.button("Need Help? (Coming Soon)" , type="primary", disabled=True)
    about_button = st.button("About (Coming Soon)", type="primary", disabled=True)

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
            st.session_state.images = await generate_image(
                st.session_state["current_image_prompt"]
            )
    if st.session_state.image_list != []:
        with stylable_container(
            key="image-display-container",
            css_styles="""
                    button {
                        color: #ffffff;
                        background-color: #f0d1b7;
                    }
            """,
        ):
            if st.session_state.image_model == "dall-e-2":
                col1, col2, col3 = st.columns(3)
                # Display each image in one column with a radio button below it for the user to select
                # Only one image can be selected at a time
                # Use PIL to convert the image_url to a PIL image and then display it
                with col1:
                    logger.debug(f"Image 1: {st.session_state.image_list[0]}")
                    display_image(st.session_state.image_list[0])
                    get_image_download_link(st.session_state.image_list[0], "image1.png")
                with col2:
                    logger.debug(f"Image 2: {st.session_state.image_list[1]}")
                    display_image(st.session_state.image_list[1])
                    get_image_download_link(st.session_state.image_list[1], "image2.png")
                with col3:
                    logger.debug(f"Image 3: {st.session_state.image_list[2]}")
                    display_image(st.session_state.image_list[2])
                    get_image_download_link(st.session_state.image_list[2], "image3.png")
            elif st.session_state.image_model == "dall-e-3":
                # If the image model is dall-e-3, display 1 image
                logger.debug(f"Image 1: {st.session_state.image_list[0]}")
                display_image(st.session_state.image_list[0])
                get_image_download_link(st.session_state.image_list[0], "image1.png")
    st.markdown(
        """
        <p style="text-align: left; color: #000000; font-size:1em; margin-top: 30px; margin-left: 5px;">
        Want to Start Over?</p>
        """, unsafe_allow_html=True
    )
    generate_new_post_button = st.button("Generate New Post", type="primary")
    if generate_new_post_button:
        # Reset the session state
        st.session_state.current_post = None
        st.session_state.current_hashtags = None
        st.session_state.current_image_prompt = None
        st.session_state.generate_image = False
        st.session_state.image_choice = False
        st.session_state.current_image = None
        st.session_state.post_page = "post_home"
        st.session_state.model_selection = "GPT-3.5"
        st.session_state.current_model = "gpt-3.5-turbo-1106"
        st.session_state.image_list = None
        st.session_state.selected_image = None
        st.rerun()

if st.session_state.post_page == "post_home":
    logger.debug("Running post_home function")
    asyncio.run(post_home())
elif st.session_state.post_page == "display_post":
    logger.debug("Running display_post function")
    asyncio.run(display_post())
