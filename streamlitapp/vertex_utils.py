from google import genai
import os


def get_vertex_client():
    os.environ["GOOGLE_CLOUD_API_KEY"] = "AQ.Ab8RN6Ku11MlnrqOjUkD9ouPBe68j6kmWH4l_4YmnVSsiUjU_A"
    return genai.Client(vertexai=True, api_key=os.environ["GOOGLE_CLOUD_API_KEY"])