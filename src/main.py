import asyncio
import os
import dotenv
import uuid

from flask import Flask, request, jsonify, g
from flasgger import Swagger
from firecrawl import FirecrawlApp

from .functions.auth import authenticate, get_user_token
from .helpers.http_request import get_request, post_request
from .helpers.socket_request import WebSocketClient
from .decorators.auth_decorator import auth_required

crawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
swagger = Swagger(app)


# HTTP URL Constants
CREATE_PRESENTATION_URL = "https://alai-standalone-backend.getalai.com/create-new-presentation"
CALIBRATE_TONE_URL = "https://alai-standalone-backend.getalai.com/calibrate-tone"
CALIBRATE_VERBOSITY_URL = "https://alai-standalone-backend.getalai.com/calibrate-verbosity"
GET_SAMPLE_TEXT_URL = "https://alai-standalone-backend.getalai.com/get-calibration-sample-text"
UPSERT_PRESENTATION_URL = "https://alai-standalone-backend.getalai.com/upsert-presentation-share"
CREATE_SLIDE_URL = "https://alai-standalone-backend.getalai.com/create-new-slide"
GET_PRESENTATION_QUESTIONS_URL = "https://alai-standalone-backend.getalai.com/get-presentation-questions/"

# WebSocket URL Constants
STREAM_CREATE_SLIDES_FROM_OUTLINE = "wss://alai-standalone-backend.getalai.com/ws/create-slides-from-outlines"
STREAM_GENERATE_SLIDES_OUTLINE = "wss://alai-standalone-backend.getalai.com/ws/generate-slides-outline"
STREAM_CREATE_AND_STREAM_SLIDE_VARIANTS = "wss://alai-standalone-backend.getalai.com/ws/create-and-stream-slide-variants"

# "DEFAULT", "FORMAL", "CASUAL", "EXCITED", "ENTHUSIASTIC", "PROFESSIONAL", "PERSUASIVE", "INFORMATIVE", "INSPIRATIONAL", "EDUCATIONAL", "NARRATIVE", "AUTHORITATIVE", "TECHNICAL", "EMPATHETIC"
TONE: str =  "DEFAULT"
VERBOSITY: int = 3

def run_async_task(coroutine):
    """Run an async task from sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def create_presentation(metadata, markdown_data):
    """Create a presentation from the crawled data."""
    json_data = {}
    json_data['presentation_id'] = uuid.uuid4().hex
    json_data['presentation_title'] = metadata.get("title", "Untitled Presentation")
    json_data['create_first_slide'] = True
    json_data['theme_id'] = 'a6bff6e5-3afc-4336-830b-fbc710081012' # Not sure what is this but we cant seem to change it
    json_data["default_color_set_id"] = 0

    response = post_request(CREATE_PRESENTATION_URL,
                            data=json_data,
                        )

    if response.status_code != 200:
        return jsonify(response.json), response.status_code
    presentation_id = response.json().get("id")
    if not presentation_id:
        return jsonify({"error": "Failed to create presentation"}), 500
    slides = response.json().get("slides", [])
    if not slides:
        return jsonify({"error": "No slides created in presentation"}), 500
    
    first_slide_id = slides[0].get("id")
    
    response = get_request(GET_PRESENTATION_QUESTIONS_URL + f"/{presentation_id}")
    if response.status_code != 200:
        return jsonify(response.json()), response.status_code
    
    questions = response.json()

    slide_number = metadata.get("num_of_slides", 1)
    slide_range: str = "1"

    if 2 <= slide_number <= 5:
        slide_range = "2-5"
    elif 6 <= slide_number <= 10:
        slide_range = "6-10"
    elif 11 <= slide_number <= 15:
        slide_range = "11-15"
    elif 16 <= slide_number <= 20:
        slide_range = "16-20"
    elif slide_number > 20:
        slide_range = "21-25"

    create_outline_json = {
        "auth_token": g.access_token,
        "presentation_id": presentation_id,
        "presentation_instructions": metadata.get("instructions", ""),
        "presentation_questions": questions,
        "raw_context": markdown_data,
        "slide_order": 0,
        "slide_range": slide_range
    }

    slide_contexts = run_async_task(WebSocketClient.connect_and_listen(ws_url= STREAM_GENERATE_SLIDES_OUTLINE,
        data=create_outline_json))

    json_data = {}
    json_data['presentation_id'] = presentation_id
    json_data['raw_context'] = markdown_data

    get_sample_text_response = post_request(
        GET_SAMPLE_TEXT_URL,
        data=json_data
    )
    if get_sample_text_response.status_code != 200:
        return jsonify(get_sample_text_response.json()), get_sample_text_response.status_code

    sample_text = get_sample_text_response.json().get("sample_text", "")
    if not sample_text:
        return jsonify({"error": "Failed to get sample text for calibration"}), 500

    # set tone
    calibrate_tone_json = {
        "presentation_id": presentation_id,
        "original_text": sample_text,
        "tone_type": metadata.get("tone", "DEFAULT"),
        "tone_instructions": metadata.get("tone_instructions", None),
    }

    calibrate_tone_response = post_request(CALIBRATE_TONE_URL,
                                data=calibrate_tone_json)
    
    if calibrate_tone_response.status_code != 200:
        return jsonify(calibrate_tone_response.json()), calibrate_tone_response.status_code
    
    calibrate_verbosity_json = {
        "presentation_id": presentation_id,
        "original_text": sample_text,
        "verbosity_level": metadata.get("verbosity", 3),
        "previous_verbosity_level": 3,
        "tone_type": metadata.get("tone", "DEFAULT"),
        "tone_instructions": metadata.get("tone_instructions", None),
    }

    calibrate_verbosity_response = post_request(CALIBRATE_VERBOSITY_URL,
                                data=calibrate_verbosity_json)
    if calibrate_verbosity_response.status_code != 200:
        return jsonify(calibrate_verbosity_response.json()), calibrate_verbosity_response.status_code
    
    
    socket_data = {
        "auth_token" : g.access_token,
        "presentation_id" : presentation_id,
        "presentation_instructions" : metadata.get("instructions", ""),
        "raw_context" : markdown_data,
        "slide_id" : first_slide_id,
        "slide_outlines" : slide_contexts,
        "starting_slide_order": 0,
        "images_on_slide" : [],
        "update_tone_verbosity_calibration_status" : True
    }
    
    messages = run_async_task(WebSocketClient.connect_and_listen(ws_url=STREAM_CREATE_SLIDES_FROM_OUTLINE,
        data=socket_data))
    
    slides = messages[0].get("slides", [])
    if not slides:
        return jsonify({"error": "No slides created in presentation"}), 500
    
    for slide in slides:
        slide_outline = slide.get("slide_outline", "")
        socket_data = {
            "auth_token": g.access_token,
            "additional_instructions": metadata.get("instructions", ""),
            "images_on_slide": [],
            "layout_type": "AI_GENERATED_LAYOUT",
            "presentation_id": presentation_id,
            "slide_id": slide_outline.get("slide_id", ""),
            "slide_specific_context": slide_outline.get("slide_instructions", ""),
            "slide_title": slide_outline.get("slide_title", ""),
            "update_tone_verbosity_calibration_status": False
        }

        create_slide_response = run_async_task(WebSocketClient.connect_and_listen(
            ws_url=STREAM_CREATE_AND_STREAM_SLIDE_VARIANTS,
            data=socket_data
        ))
    
    ppt_id = post_request(UPSERT_PRESENTATION_URL, data= {
        "presentation_id": presentation_id,
    })

    ppt_id = ppt_id.json()
    
    return jsonify({
        "message": "Presentation created successfully",
        "url": "https://app.getalai.com/view/" + ppt_id,
    }), 200

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return access token.
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: "utsav"
            password:
              type: string
              example: "securepassword123"
    responses:
      200:
        description: Successful authentication
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            expires_at:
              type: integer
      401:
        description: Authentication failed
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    auth_response = authenticate(username, password)
    if auth_response:
        return jsonify(auth_response)

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/create-presentation", methods=["POST"])
@auth_required
def protected():
    request_json = request.json
    if not request_json:
        return jsonify({"error": "No data provided"}), 400
    url = request_json.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
    crawl_result = crawl_app.scrape_url(url=url, 
                                        params={
                                            'formats': [ 'markdown'] , 
                                            'onlyMainContent': True,})
    return create_presentation(metadata=request_json, markdown_data=dict(crawl_result)['markdown'])


if __name__ == "__main__":
    dotenv.load_dotenv()
    if 'user_sessions' not in g:
        g.user_sessions = {}
    app.run(debug=True)
    