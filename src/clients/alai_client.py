import logging
import asyncio
from ..helpers.http_request import get_request, post_request
from ..helpers.socket_request import WebSocketClient
from ..config import BaseConfig

logger = logging.getLogger(__name__)

class ALAIClient:
    """Client for interacting with the ALAI API."""
    
    @staticmethod
    def run_async_task(coroutine):
        """Run an async task from sync context."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)
    
    @staticmethod
    def create_presentation(access_token, presentation_id, title, theme_id=None, color_set_id=None):
        """Create a new presentation."""
        json_data = {
            'presentation_id': presentation_id,
            'presentation_title': title,
            'create_first_slide': True,
            'theme_id': theme_id or BaseConfig.DEFAULT_THEME_ID,
            'default_color_set_id': color_set_id or BaseConfig.DEFAULT_COLOR_SET_ID
        }
        
        response = post_request(BaseConfig.CREATE_PRESENTATION_URL, data=json_data)
        
        if response.status_code != 200:
            logger.error(f"Failed to create presentation: {response.json()}")
            return None, response.json()
            
        return response.json(), None
    
    @staticmethod
    def get_presentation_questions(presentation_id):
        """Get questions for a presentation."""
        response = get_request(f"{BaseConfig.GET_PRESENTATION_QUESTIONS_URL}/{presentation_id}")
        
        if response.status_code != 200:
            logger.error(f"Failed to get presentation questions: {response.json()}")
            return None, response.json()
            
        return response.json(), None
    
    @staticmethod
    def get_sample_text(presentation_id, raw_context):
        """Get sample text for calibration."""
        json_data = {
            'presentation_id': presentation_id,
            'raw_context': raw_context
        }
        
        response = post_request(BaseConfig.GET_SAMPLE_TEXT_URL, data=json_data)
        
        if response.status_code != 200:
            logger.error(f"Failed to get sample text: {response.json()}")
            return None, response.json()
            
        return response.json().get("sample_text", ""), None
    
    @staticmethod
    def calibrate_tone(presentation_id, sample_text, tone_type, tone_instructions=None):
        """Calibrate tone for a presentation."""
        json_data = {
            'presentation_id': presentation_id,
            'original_text': sample_text,
            'tone_type': tone_type,
            'tone_instructions': tone_instructions,
        }
        
        response = post_request(BaseConfig.CALIBRATE_TONE_URL, data=json_data)
        
        if response.status_code != 200:
            logger.error(f"Failed to calibrate tone: {response.json()}")
            return None, response.json()
            
        return response.json(), None
    
    @staticmethod
    def calibrate_verbosity(presentation_id, sample_text, verbosity_level, tone_type, tone_instructions=None):
        """Calibrate verbosity for a presentation."""
        json_data = {
            'presentation_id': presentation_id,
            'original_text': sample_text,
            'verbosity_level': verbosity_level,
            'previous_verbosity_level': BaseConfig.DEFAULT_VERBOSITY,
            'tone_type': tone_type,
            'tone_instructions': tone_instructions,
        }
        
        response = post_request(BaseConfig.CALIBRATE_VERBOSITY_URL, data=json_data)
        
        if response.status_code != 200:
            logger.error(f"Failed to calibrate verbosity: {response.json()}")
            return None, response.json()
            
        return response.json(), None
    
    @staticmethod
    def generate_slides_outline(access_token, presentation_id, instructions, questions, raw_context, slide_range):
        """Generate slides outline."""
        data = {
            "auth_token": access_token,
            "presentation_id": presentation_id,
            "presentation_instructions": instructions,
            "presentation_questions": questions,
            "raw_context": raw_context,
            "slide_order": 0,
            "slide_range": slide_range
        }
        
        return ALAIClient.run_async_task(
            WebSocketClient.connect_and_listen(
                ws_url=BaseConfig.STREAM_GENERATE_SLIDES_OUTLINE,
                data=data
            )
        )
    
    @staticmethod
    def create_slides_from_outline(access_token, presentation_id, instructions, raw_context, 
                                  first_slide_id, slide_contexts):
        """Create slides from outline."""
        data = {
            "auth_token": access_token,
            "presentation_id": presentation_id,
            "presentation_instructions": instructions,
            "raw_context": raw_context,
            "slide_id": first_slide_id,
            "slide_outlines": slide_contexts,
            "starting_slide_order": 0,
            "images_on_slide": [],
            "update_tone_verbosity_calibration_status": True
        }
        
        return ALAIClient.run_async_task(
            WebSocketClient.connect_and_listen(
                ws_url=BaseConfig.STREAM_CREATE_SLIDES_FROM_OUTLINE,
                data=data
            )
        )
    
    @staticmethod
    def create_slide_variants(access_token, presentation_id, slide_id, slide_title, slide_instructions, 
                             additional_instructions=None):
        """Create slide variants."""
        data = {
            "auth_token": access_token,
            "additional_instructions": additional_instructions or "",
            "images_on_slide": [], # Dont know why but if we use the scraped images the socket returns 404 image not found error
            "layout_type": "AI_GENERATED_LAYOUT",
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "slide_specific_context": slide_instructions,
            "slide_title": slide_title,
            "update_tone_verbosity_calibration_status": False
        }
        
        return ALAIClient.run_async_task(
            WebSocketClient.connect_and_listen(
                ws_url=BaseConfig.STREAM_CREATE_AND_STREAM_SLIDE_VARIANTS,
                data=data
            )
        )
    
    @staticmethod
    def upsert_presentation_share(presentation_id):
        """Upsert presentation share."""
        response = post_request(
            BaseConfig.UPSERT_PRESENTATION_URL, 
            data={"presentation_id": presentation_id}
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to upsert presentation share: {response.json()}")
            return None, response.json()
            
        return response.json(), None