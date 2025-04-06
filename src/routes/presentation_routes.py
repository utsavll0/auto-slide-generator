from flask import Blueprint, request, jsonify, g
from ..decorators.auth_decorator import auth_required
from ..clients.firecrawl_client import FirecrawlClient
from ..service.presentation_service import PresentationService

presentation_bp = Blueprint('presentation', __name__)

@presentation_bp.route("/create", methods=["POST"])
@auth_required
def create_presentation():
    """
    Create a presentation from a URL.
    ---
    tags:
      - Presentation
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            url:
              type: string
              example: "https://example.com"
            title:
              type: string
              example: "My Presentation"
            num_of_slides:
              type: integer
              example: 5
            tone:
              type: string
              example: "PROFESSIONAL"
            verbosity:
              type: integer
              example: 3
            instructions:
              type: string
              example: "Focus on key points"
    responses:
      200:
        description: Presentation created successfully
      400:
        description: Bad request
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
    request_json = request.json
    if not request_json:
        return jsonify({"error": "No data provided"}), 400
        
    url = request_json.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400
        
    # Scrape URL
    firecrawl_client = FirecrawlClient()
    markdown_data = firecrawl_client.scrape_url(url)
    
    # Create presentation
    result, status_code = PresentationService.create_presentation_from_markdown(
        g.access_token, 
        request_json, 
        markdown_data
    )
    
    return jsonify(result), status_code