"""
Alpha Vantage Stocks API Client
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "")

async def get_intraday_data(symbol: str) -> dict:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "apikey": ALPHAVANTAGE_API_KEY
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage Error: {data['Error Message']}")
        if "Information" in data:
            raise ValueError(f"Alpha Vantage API limits: {data['Information']}")
            
        return data

def health_check() -> bool:
    return bool(ALPHAVANTAGE_API_KEY)
