""" Main Instalicious Page """
import streamlit as st
import asyncio
import io
from PIL import Image
from pillow_heif import register_heif_opener
import streamlit.components.v1 as components
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
from openai import OpenAIError
from dependencies import get_openai_client
from utils.image_utils import generate_dalle3_image
from utils.post_utils import alter_image, get_image_prompt
import logging
import base64


st.set_page_config(
    page_title="Instalicio.us",
    initial_sidebar_state="collapsed",
)

register_heif_opener()

# Create the OpenAI client
client = get_openai_client()

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
        "image_model", "user_image_string", "generate_image", "post_prompt",
        "current_post", "current_hashtags", "current_image_prompt", "post_page",
        "generated_image", "size_choice"
    ]
    default_values = [
        "dall-e-3", None, False, None, None, None, None, "post_verify",
        [], None
    ]

    for var, default_value in zip(session_vars, default_values):
        if var not in st.session_state:
            st.session_state[var] = default_value

def reset_session_variables():
    session_vars = [
        "image_model", "is_user_image", "user_image_string", "generate_image", "post_prompt"
        "current_post", "current_hashtags", "current_image_prompt", "generated_image"
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
    with stylable_container(
        key="post-home-container",
        css_styles="""
                h1 {
                    color: #000000;
                    font-size: 4em;
                    text-align: center;
                    font-family: 'Anton', sans-serif;
                }
        """,
    ):
        # Create a centered header using HTML with bold font
        st.markdown(
            """<h1><b>INSTALICIO.US</b></h1>""", unsafe_allow_html=True
        )
        # Create a centered subheader using HTML with bold font
        st.markdown(
            """<p style='text-align:center; font-family:"Arapey";'>
            Transform any meal into a stunning,
            Insta-worthy post... instantly.</p>""", unsafe_allow_html=True
        )
    with stylable_container(
        key="post-main",
        css_styles="""
        {
            font-family: 'Arapey', serif;
            font-size: 1em;
            border-color: #000000;
        }
        p {
            font-size: 1.1em;
            text-align: start;
        }
        """,
    ):
        st.markdown(
            """**How it works:** Instalicio.us uses cutting-edge AI to generate stunning
            images and social media posts optimized for engagement and virality based on your prompt.
            This could be a description of the dish, a mood, a pasted recipe,
            a restaurant experience you had, etc.\n\n Let your imagination run wild!"""
        )
        st.text("")
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
            uploaded_image = st.file_uploader(
                "Upload an image", type=["png", "jpg", "jpeg", "heic", "HEIC"]
            )
            # Convert the image to a base64 string
            if uploaded_image:
                # If the file type is .heic or .HEIC, convert to a .png using PIL
                if uploaded_image.name.endswith(".heic") or uploaded_image.name.endswith(".HEIC"):
                    image_string = heic_to_base64(uploaded_image)
                    st.session_state.user_image_string = image_string
                else:
                    image_string = await encode_image(uploaded_image)
                st.session_state.user_image_string = image_string
        elif picture_mode == "Let Us Generate One For You":
            st.session_state.user_image_string = None
        st.text("")
        post_prompt = st.text_area("""###### Tell Us About This Recipe or Meal""")

        size_choice = st.radio(
            "Select your desired format:", options=["Square", "Stories"], horizontal=True, index=None,
        )
        if size_choice == "Square":
            st.session_state.size_choice = "1024x1024"
        elif size_choice == "Stories":
            st.session_state.size_choice = "1024x1792"

        generate_post_button = st.button("Generate Post", type="primary", use_container_width=True)
        logger.debug(f"Generate post button pressed: {generate_post_button}")
        if generate_post_button:
            if picture_mode and post_prompt != "" and st.session_state.size_choice is not None:
                st.session_state.post_prompt = post_prompt
                st.session_state.post_page = "display_post"
                st.rerun()
            else:
                st.warning("Please make an image choice, size choice, and enter a prompt.")

    st.text("")
    st.text("")
    st.markdown(
        """<p style='text-align:center; font-family:"Arapey";'>If you need some inspiration,
        click the button below to
        see some examples of posts that Instalicio.us has generated.
        Whether you are trying to enhance an image you already have or
        generate a completely new one, we think you will find the tool useful and delightful.</p>""",
        unsafe_allow_html=True
    )
    examples_button = st.button("See Examples", type="primary", use_container_width=True)
    if examples_button:
        switch_page("Dalle3StreamingExamples")
        st.rerun()

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
        messages = [
            {
                "role": "system", "content": f"""You are a helpful assistant helping a user optimize and
                create posts for Instagram centered around food and cooking.The user would like
                for you to generate an Instagram post optimized
                for engagement and virality based on the prompt {st.session_state.post_prompt}
                they have given.  This could be a recipe, a description of a dish,
                a description of a restaurant experience, etc.
                If it is a recipe, you do not need to return the recipe itself,
                Make sure to that the post includes hashtags
                and that the post is presented in a clear
                and organized manner.  Return only the generated post text and hashtags.
                You do not need to return any other message content other than a note
                at the end that says something like "Now give us just a sec, and we will generate
                an amazing image for you to go with your post."
                """
            },
            {
                "role" : "user",
                "content" : f"""Can you help me generate an amazing
                Instagram post based on this prompt {st.session_state.post_prompt}?"""
            }
        ]

    message_placeholder = st.empty()
    full_response = ""
    if st.session_state.current_post is None:
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].finish_reason == "stop":
                    logging.debug("Received 'stop' signal from response.")
                    break
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.current_post = full_response
        except OpenAIError as e:
            logger.error(f"Error generating post: {e}")
            st.error(f"Error generating post: {e}")
    if st.session_state.current_post:
        html = f"""
        <input type="text" id="textToCopy" value="{st.session_state.current_post}" style="color:transparent;
        border-color:transparent;">
        <button onclick="copyToClipboard()" style="background-color:transparent; height: 2.75em;
        margin-left: 7em; border-radius:4px; font-size:1em;">Copy Post 📋</button>

        <script>
            function copyToClipboard() {{
                var copyText = document.getElementById("textToCopy");
                copyText.select();
                copyText.setSelectionRange(0, 99999); /* For mobile devices */
                document.execCommand("copy");
                alert("Copied the text: " + copyText.value);
            }}
        </script>
        """
        components.html(html, height=75)
        st.text("")
    if not st.session_state.generated_image != [] and st.session_state.user_image_string:
        with st.spinner("Hang tight, we are generating your image..."):
            image_prompt = await alter_image(st.session_state.post_prompt, st.session_state.user_image_string)
            st.session_state.generated_image = await generate_dalle3_image(
                prompt=image_prompt
            )
    elif not st.session_state.generated_image != [] and st.session_state.user_image_string is None:
        with st.spinner("Hang tight, we are generating your image..."):
            image_prompt = await get_image_prompt(st.session_state.post_prompt)
            st.session_state.generated_image = await generate_dalle3_image(
                prompt=image_prompt
            )

    st.markdown(
        """<p style='text-align: center; color: #000000;
        font-size: 20px; font-family:"Arapey";'>Here's your image!</p>""", unsafe_allow_html=True
    )
    if st.session_state.generated_image:
        with stylable_container(
            key="image-display-container",
            css_styles="""
                button {
                    color: white;
                    background-color: #76beaa;
                }
            """,
        ):
            # If the image model is dall-e-3, display 1 image
            logger.debug(f"Your Image: {st.session_state.generated_image}")
            display_image(st.session_state.generated_image)
            get_image_download_link(st.session_state.generated_image, filename="instalicious_image.png")

    generate_new_post_button = st.button("Generate New Post", type="primary", use_container_width=True)
    if generate_new_post_button:
        # Reset the session state
        reset_session_variables()
        st.session_state.current_post = None
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
