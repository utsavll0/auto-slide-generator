"""Configuration settings for the application."""

class BaseConfig:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    
    # API endpoints
    ALAI_BASE_URL = "https://alai-standalone-backend.getalai.com"
    ALAI_WS_BASE_URL = "wss://alai-standalone-backend.getalai.com/ws"
    
    # HTTP URL Constants
    CREATE_PRESENTATION_URL = f"{ALAI_BASE_URL}/create-new-presentation"
    CALIBRATE_TONE_URL = f"{ALAI_BASE_URL}/calibrate-tone"
    CALIBRATE_VERBOSITY_URL = f"{ALAI_BASE_URL}/calibrate-verbosity"
    GET_SAMPLE_TEXT_URL = f"{ALAI_BASE_URL}/get-calibration-sample-text"
    UPSERT_PRESENTATION_URL = f"{ALAI_BASE_URL}/upsert-presentation-share"
    CREATE_SLIDE_URL = f"{ALAI_BASE_URL}/create-new-slide"
    GET_PRESENTATION_QUESTIONS_URL = f"{ALAI_BASE_URL}/get-presentation-questions"
    
    # WebSocket URL Constants
    STREAM_CREATE_SLIDES_FROM_OUTLINE = f"{ALAI_WS_BASE_URL}/create-slides-from-outlines"
    STREAM_GENERATE_SLIDES_OUTLINE = f"{ALAI_WS_BASE_URL}/generate-slides-outline"
    STREAM_CREATE_AND_STREAM_SLIDE_VARIANTS = f"{ALAI_WS_BASE_URL}/create-and-stream-slide-variants"
    
    # App settings
    DEFAULT_THEME_ID = 'a6bff6e5-3afc-4336-830b-fbc710081012'
    DEFAULT_COLOR_SET_ID = 0
    DEFAULT_TONE = "DEFAULT"
    DEFAULT_VERBOSITY = 3
    

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
