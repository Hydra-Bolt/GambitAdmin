import os
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class OddsAPI:
    """Service to interact with The Odds API (https://the-odds-api.com/)"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self, api_key=None):
        """
        Initialize the OddsAPI service.
        
        Args:
            api_key (str, optional): API key for The Odds API. If not provided,
                                    it will try to get it from environment variable.
        """
        self.api_key = api_key or os.environ.get("ODDS_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided for OddsAPI. Set ODDS_API_KEY env variable or provide in constructor.")
        
        # Track API usage to avoid rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # seconds
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to The Odds API with proper rate limiting.
        
        Args:
            endpoint (str): API endpoint to call
            params (dict, optional): Query parameters for the request
            
        Returns:
            dict: API response as dictionary
            
        Raises:
            ValueError: If API key is not provided
            Exception: If API request fails
        """
        if not self.api_key:
            raise ValueError("API key is required for OddsAPI")
            
        # Ensure we don't exceed rate limits
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        # Prepare request parameters    
        request_params = params or {}
        request_params["apiKey"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        logger.debug(f"Making request to: {url}")
        
        try:
            response = requests.get(url, params=request_params)
            self.last_request_time = time.time()
            
            # Check for rate limit headers to adjust future requests
            if 'x-requests-remaining' in response.headers:
                remaining = int(response.headers['x-requests-remaining'])
                if remaining < 10:
                    logger.warning(f"Only {remaining} API requests remaining for the current period")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to The Odds API: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"API request failed: {str(e)}")
            
    def get_sports(self) -> List[Dict[str, Any]]:
        """
        Get all sports supported by the API.
        
        Returns:
            List[dict]: List of sports with their keys and names
        """
        return self._make_request("sports")
        
    def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h", 
                date_format: str = "iso", bookmakers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get odds for a specific sport.
        
        Args:
            sport (str): Sport key to get odds for (e.g., "basketball_nba")
            regions (str): Region for the odds (e.g., "us", "uk", "eu", "au")
            markets (str): Type of odds (e.g., "h2h", "spreads", "totals")
            date_format (str): Format for the event dates (e.g., "iso", "unix")
            bookmakers (List[str], optional): Filter for specific bookmakers
            
        Returns:
            List[dict]: List of events with their odds
        """
        params = {
            "regions": regions,
            "markets": markets,
            "dateFormat": date_format
        }
        
        if bookmakers:
            params["bookmakers"] = ",".join(bookmakers)
            
        return self._make_request(f"sports/{sport}/odds", params)
        
    def get_event_odds(self, sport: str, event_id: str, regions: str = "us",
                     markets: str = "h2h", date_format: str = "iso") -> Dict[str, Any]:
        """
        Get odds for a specific event.
        
        Args:
            sport (str): Sport key (e.g., "basketball_nba")
            event_id (str): Event ID to get odds for
            regions (str): Region for the odds (e.g., "us", "uk", "eu", "au")
            markets (str): Type of odds (e.g., "h2h", "spreads", "totals")
            date_format (str): Format for the event dates (e.g., "iso", "unix")
            
        Returns:
            dict: Event details with odds
        """
        params = {
            "regions": regions,
            "markets": markets,
            "dateFormat": date_format
        }
        
        return self._make_request(f"sports/{sport}/events/{event_id}/odds", params)
        
    def get_historical_odds(self, sport: str, regions: str = "us",
                          markets: str = "h2h", date_format: str = "iso",
                          date: str = None) -> List[Dict[str, Any]]:
        """
        Get historical odds for a specific sport and date.
        
        Args:
            sport (str): Sport key (e.g., "basketball_nba")
            regions (str): Region for the odds (e.g., "us", "uk", "eu", "au")
            markets (str): Type of odds (e.g., "h2h", "spreads", "totals")
            date_format (str): Format for the event dates (e.g., "iso", "unix")
            date (str, optional): Date string in format YYYY-MM-DD
            
        Returns:
            List[dict]: List of historical events with their odds
        """
        params = {
            "regions": regions,
            "markets": markets,
            "dateFormat": date_format
        }
        
        if date:
            params["date"] = date
            
        return self._make_request(f"sports/{sport}/odds-history", params)
        
    def get_scores(self, sport: str, date_format: str = "iso", 
                 since: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get scores for a specific sport.
        
        Args:
            sport (str): Sport key (e.g., "basketball_nba")
            date_format (str): Format for the event dates (e.g., "iso", "unix")
            since (int, optional): Unix timestamp to get scores updated since
            
        Returns:
            List[dict]: List of events with their scores
        """
        params = {
            "dateFormat": date_format
        }
        
        if since:
            params["since"] = since
            
        return self._make_request(f"sports/{sport}/scores", params)