"""
Simple MCP (Machine Control Protocol) implementation for the Twitter service.
"""

from fastapi import APIRouter
from typing import Any, Callable, Dict
from functools import wraps

router = APIRouter()
tools = {}

def tool(name: str, description: str, parameters: Dict[str, Any], returns: Dict[str, Any]) -> Callable:
    """Decorator to register a function as an MCP tool."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        # Register the tool
        tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "returns": returns,
            "function": wrapper
        }
        
        # Add FastAPI route
        router.add_api_route(
            f"/tools/{name}",
            wrapper,
            methods=["POST"],
            response_model=returns.get("type", Dict[str, Any]),
            name=name,
            description=description
        )
        
        return wrapper
    return decorator 