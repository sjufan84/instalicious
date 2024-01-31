""" Main Instalicious Page """
import streamlit as st
import asyncio
import io
from PIL import Image
from pillow_heif import register_heif_opener
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
from utils.image_utils import generate_dalle2_images
from utils.post_utils import create_post, alter_image
import logging
import base64

register_heif_opener()

def heic_to_base64(heic_path):
    # Read HEIC file
    heif_file = Image.open(heic_path)

    # Convert to RGB
    img = heif_file.convert("RGB")

    # Create an in-memory file object
    buffer = io.BytesIO()

    # Save the image to the in-memory file object
    img.save(buffer, format="JPEG")

    # Encode to Base64
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64


st.set_page_config(
    page_title="Instalicio.us",
    initial_sidebar_state="collapsed",
)

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
        "image_model", "user_image_string", "generate_image",
        "current_post", "current_hashtags", "current_image_prompt", "post_page", "generated_images"
    ]
    default_values = [
        "dall-e-3", None, False, None, None, None, "post_verify",
        []
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_session_variables():
    session_vars = [
        "image_model", "is_user_image", "user_image_string", "generate_image",
        "current_post", "current_hashtags", "current_image_prompt", "generated_images"
    ]
    for var in session_vars:
        if var in st.session_state:
            del st.session_state[var]

    st.session_state.post_page = "post_home"

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

def post_verify():
    password_input = st.text_input("Enter the password to access this page", type="password")
    submit_password_button = st.button("Submit", type="primary", use_container_width=True)
    if submit_password_button:
        if password_input == "cupcake":
            st.session_state.post_page = "post_home"
            st.rerun()
        else:
            st.warning("Incorrect password. Please try again.")

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
            border-color: #000000;
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
                if uploaded_image.name.endswith(".heic") or uploaded_image.name.endswith(".HEIC"):
                    image_string = heic_to_base64(uploaded_image)
                    st.session_state.user_image_string = image_string
                else:
                    image_string = await encode_image(uploaded_image)
                st.session_state.user_image_string = image_string

        elif picture_mode == "Upload an image":
            # Show a file upoloader that only accepts image files
            uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "heic", "HEIC"])
            # Convert the image to a base64 string
            if uploaded_image:
                # If the file type is .heic or .HEIC, convert to a .png using PIL
                if uploaded_image.name.endswith(".heic") or uploaded_image.name.endswith(".HEIC"):
                    image_string = heic_to_base64(uploaded_image)
                    st.session_state.user_image_string = image_string
                else:
                    image_string = await encode_image(uploaded_image)
                st.write(image_string[:100] + "...")
                st.session_state.user_image_string = image_string
        elif picture_mode == "Let Us Generate One For You":
            st.session_state.generate_image = True

        st.text("")
        post_prompt = st.text_area("""###### Tell Us About This Recipe or Meal""")

    generate_post_button = st.button("Generate Post", type="primary", use_container_width=True)
    logger.debug(f"Generate post button pressed: {generate_post_button}")
    if generate_post_button:
        if picture_mode and post_prompt != "" and st.session_state.user_image_string:
            with st.spinner("Generating your post. This may take a minute..."):
                image_prompt = await alter_image(post_prompt, st.session_state.user_image_string)
                st.session_state.current_image_prompt = image_prompt
                post = await create_post(prompt=post_prompt, post_type="no_image")
                st.session_state.current_post = post["post"]
                st.session_state.current_hashtags = post["hashtags"]
                st.session_state.post_page = "display_post"
                st.rerun()
        elif picture_mode and post_prompt != "" and not st.session_state.user_image_string:
            with st.spinner("Generating your post. This may take a minute..."):
                post = await create_post(prompt=post_prompt, post_type="with_image")
                st.session_state.current_post = post["post"]
                st.session_state.current_hashtags = post["hashtags"]
                st.session_state.current_image_prompt = post["image_prompt"]
                st.session_state.post_page = "display_post"
                st.rerun()
        else:
            st.warning("Please make an image choice, enter a description, and select your preferred format.")

    st.text("")
    st.text("")
    with stylable_container(
        key="post-home-footer",
        css_styles="""
        {
            font-family: 'Arapey', serif;
            font-size: 1.1em;
        }
        """,
    ):
        st.markdown(
            """**How it works:** Instalicio.us uses cutting edge AI to generate stunning images and
            posts optimized for engagement and virality based on your prompt.  This could be a description
            of the dish and a setting, a pasted recipe, a restaurant experience you had, etc.
            Let your imagination
            run wild!  If you snap or upload an image, a separate model "looks at" the image,
            and then factors that in to the post generation as well."""
        )
        st.markdown(
            """**If you need some inspiration**, click the button below to
            see some examples of posts that Instalicio.us has generated.
            Whether you are trying to enhance an image you already have or
            generate a completely new one, we think you will find the tool useful and delightful."""
        )
        examples_button = st.button("See Examples", type="primary", use_container_width=True)
        if examples_button:
            switch_page("Examples")
            st.rerun()
        st.markdown(
            """
            <p style="text-align: left; color: #000000; font-size:1em; margin-top: 30px; margin-left: 5px;">
            Before you leave, please <a href="http://www.google.com";
            color="blue";>fill out a quick survey</a>
            to tell us about your experience and help us get better!</p>
            """, unsafe_allow_html=True
        )

    # need_help_button = st.button("Need Help? (Coming Soon)" , type="primary", disabled=True)
    # about_button = st.button("About (Coming Soon)", type="primary", disabled=True)

async def display_post():
    """ Display the post and the image """
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
        font-size: 20px; font-family:"Arapey";'>Here are your images!</p>""", unsafe_allow_html=True
    )
    if not st.session_state.generated_images != []:
        with st.spinner("Generating your images..."):
            st.session_state.generated_images = await generate_dalle2_images(
                st.session_state["current_image_prompt"]
            )
    if st.session_state.generated_images != []:
        with stylable_container(
            key="image-display-container",
            css_styles="""
                    button {
                        color: #ffffff;
                        background-color: #76beaa;
                    }
            """,
        ):
            st.markdown("##### Here are your images!")
            col1, col2, col3 = st.columns(3, gap="medium")
            # Display the iamges from the list of generated images
            with col1:
                display_image(st.session_state.generated_images[0])
                get_image_download_link(
                    st.session_state.generated_images[0], filename="instalicious_image_1.png"
                )
            with col2:
                display_image(st.session_state.generated_images[1])
                get_image_download_link(
                    st.session_state.generated_images[1], filename="instalicious_image_2.png"
                )
            with col3:
                display_image(st.session_state.generated_images[2])
                get_image_download_link(
                    st.session_state.generated_images[2], filename="instalicious_image_3.png"
                )

    st.markdown(
        """
        <p style="text-align: left; color: #000000; font-size:1em; margin-top: 30px; margin-left: 5px;">
        Want to Start Over? Before you do, please
        <a href="http://www.google.com"; color="blue";>fill out a quick survey</a>
        to tell us about your experience and help us get better!</p>
        """, unsafe_allow_html=True
    )
    generate_new_post_button = st.button("Generate New Post", type="primary", use_container_width=True)
    if generate_new_post_button:
        # Reset the session state
        reset_session_variables()
        st.rerun()

if st.session_state.post_page == "post_verify":
    logger.debug("Running post_verify function")
    post_verify()
elif st.session_state.post_page == "post_home":
    logger.debug("Running post_home function")
    asyncio.run(post_home())
elif st.session_state.post_page == "display_post":
    logger.debug("Running display_post function")
    asyncio.run(display_post())
