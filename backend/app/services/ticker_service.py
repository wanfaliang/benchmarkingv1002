"""Ticker validation service using FMP API"""
import requests
from typing import Optional, Dict, Any
from ..config import settings

class TickerService:
    def __init__(self):
        self.base_url = "https://financialmodelingprep.com/stable"
        self.api_key = settings.FMP_API_KEY
    
    def validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """Validate ticker using FMP search-symbol API"""
        if not self.api_key:
            return {"valid": False, "error": "FMP API key not configured"}
        
        try:
            url = f"{self.base_url}/search-symbol"
            params = {
                "query": ticker.upper(),
                "apikey": self.api_key,
                "limit": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                # Check if exact match
                if result["symbol"].upper() == ticker.upper():
                    return {
                        "valid": True,
                        "symbol": result["symbol"],
                        "name": result["name"],
                        "currency": result.get("currency", "USD"),
                        "exchange": result.get("exchange", "")
                    }
            
            return {"valid": False, "error": "Ticker not found"}
            
        except requests.RequestException as e:
            return {"valid": False, "error": f"API error: {str(e)}"}
        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

ticker_service = TickerService()