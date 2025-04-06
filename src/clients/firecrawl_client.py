import os
from firecrawl import FirecrawlApp

class FirecrawlClient:
    """Client for interacting with the Firecrawl API."""
    
    def __init__(self):
        """Initialize the Firecrawl client."""
        self.client = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    def scrape_url(self, url):
        """
        Scrape a URL and return the markdown content.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            str: The markdown content.
        """
        crawl_result = self.client.scrape_url(
            url=url, 
            params={
                'formats': ['markdown'], 
                'onlyMainContent': True,
            }
        )
        return dict(crawl_result)['markdown']