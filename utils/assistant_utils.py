""" Helper functions to use OpenAI Assistant API. """
from dependencies import get_openai_client

client = get_openai_client()

assistant_id = "asst_AJBb9qwzFR12OyORfRRjAjH4"

async def upload_file(image_file) -> str:
    """ Upload the file to OpenAI.  Returns the file id """
    file_response = client.files.create(
        file=open(f"{image_file}", "rb"),
        purpose="assistants"
    )
    return file_response.id

async def create_assistant_file_image(image_file):
    """ Return the enhanced image from the assitants API.
    Return True if successful, False otherwise. """
    file_id = await upload_file(image_file)
    assistant_file = client.beta.assistants.files.create(
        assistant_id=f"{assistant_id}",
        file_id=f"{file_id}"
    )
    if assistant_file:
        return True
    else:
        return False
