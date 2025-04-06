import uuid
import logging
from flask import g, jsonify
from ..clients.alai_client import ALAIClient

logger = logging.getLogger(__name__)

class PresentationService:
    """Service for managing presentations."""
    
    @staticmethod
    def _get_slide_range(num_of_slides):
        """Get slide range based on number of slides."""
        if 2 <= num_of_slides <= 5:
            return "2-5"
        elif 6 <= num_of_slides <= 10:
            return "6-10"
        elif 11 <= num_of_slides <= 15:
            return "11-15"
        elif 16 <= num_of_slides <= 20:
            return "16-20"
        elif num_of_slides > 20:
            return "21-25"
        else:
            return "1"
    
    @staticmethod
    def create_presentation_from_markdown(access_token, metadata, markdown_data):
        """Create a presentation from markdown data."""
        try:
            # Create a new presentation
            presentation_id = uuid.uuid4().hex
            presentation_title = metadata.get("title", "Untitled Presentation")
            
            presentation_data, error = ALAIClient.create_presentation(
                access_token, 
                presentation_id, 
                presentation_title
            )
            
            if error:
                return {"error": "Failed to create presentation"}, 500
            
            presentation_id = presentation_data.get("id")
            slides = presentation_data.get("slides", [])
            
            if not slides:
                return {"error": "No slides created in presentation"}, 500
            
            first_slide_id = slides[0].get("id")
            
            # Get presentation questions
            questions, error = ALAIClient.get_presentation_questions(presentation_id)
            
            if error:
                return {"error": "Failed to get presentation questions"}, 500
            
            # Get slide range based on number of slides
            slide_range = PresentationService._get_slide_range(metadata.get("num_of_slides", 1))
            
            # Generate slides outline
            slide_contexts = ALAIClient.generate_slides_outline(
                access_token,
                presentation_id,
                metadata.get("instructions", ""),
                questions,
                markdown_data,
                slide_range
            )
            
            # Get sample text for calibration
            sample_text, error = ALAIClient.get_sample_text(presentation_id, markdown_data)
            
            if error or not sample_text:
                return {"error": "Failed to get sample text for calibration"}, 500
            
            # Calibrate tone
            _, error = ALAIClient.calibrate_tone(
                presentation_id,
                sample_text,
                metadata.get("tone", "DEFAULT"),
                metadata.get("tone_instructions", None)
            )
            
            if error:
                return {"error": "Failed to calibrate tone"}, 500
            
            # Calibrate verbosity
            _, error = ALAIClient.calibrate_verbosity(
                presentation_id,
                sample_text,
                metadata.get("verbosity", 3),
                metadata.get("tone", "DEFAULT"),
                metadata.get("tone_instructions", None)
            )
            
            if error:
                return {"error": "Failed to calibrate verbosity"}, 500
            
            # Create slides from outline
            messages = ALAIClient.create_slides_from_outline(
                access_token,
                presentation_id,
                metadata.get("instructions", ""),
                markdown_data,
                first_slide_id,
                slide_contexts
            )
            
            slides = messages[0].get("slides", [])
            
            if not slides:
                return {"error": "No slides created in presentation"}, 500
            
            # Create slide variants for each slide
            for slide in slides:
                slide_outline = slide.get("slide_outline", "")
                ALAIClient.create_slide_variants(
                    access_token,
                    presentation_id,
                    slide_outline.get("slide_id", ""),
                    slide_outline.get("slide_title", ""),
                    slide_outline.get("slide_instructions", ""),
                    metadata.get("instructions", "")
                )
            
            # Upsert presentation share
            ppt_id, error = ALAIClient.upsert_presentation_share(presentation_id)
            
            if error:
                return {"error": "Failed to upsert presentation share"}, 500
            
            return {
                "message": "Presentation created successfully",
                "url": f"https://app.getalai.com/view/{ppt_id}",
            }, 200
            
        except Exception as e:
            logger.exception("Error creating presentation")
            return {"error": f"Failed to create presentation: {str(e)}"}, 500