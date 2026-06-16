"""
Supabase REST API Client — no DB password required
"""
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _base(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


async def insert(table: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(_base(table), headers=HEADERS, json=data)
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) else result


async def select(table: str, filters: Optional[dict] = None, limit: int = 100) -> list:
    params = {"limit": limit, "order": "created_at.desc"}
    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(_base(table), headers=HEADERS, params=params)
        r.raise_for_status()
        return r.json()


async def update(table: str, row_id: str, data: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.patch(
            _base(table),
            headers=HEADERS,
            params={"id": f"eq.{row_id}"},
            json=data,
        )
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) and result else {}


async def delete(table: str, row_id: str) -> bool:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.delete(
            _base(table),
            headers=HEADERS,
            params={"id": f"eq.{row_id}"},
        )
        r.raise_for_status()
        return True


async def rpc(function_name: str, params: dict = {}) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{function_name}",
            headers=HEADERS,
            json=params,
        )
        r.raise_for_status()
        return r.json()


async def health_check() -> bool:
    try:
        await select("leads", limit=1)
        return True
    except Exception:
        return False
