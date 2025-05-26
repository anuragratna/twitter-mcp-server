"""
Simple MCP (Machine Control Protocol) implementation for the Twitter service.
"""

from fastapi import APIRouter, FastAPI
from typing import Any, Callable, Dict
from functools import wraps

class MCPServer:
    def __init__(self):
        self.router = APIRouter()
        self.tools = {}

    def tool(self, name: str, description: str, parameters: Dict[str, Any], returns: Dict[str, Any]) -> Callable:
        """Decorator to register a function as an MCP tool."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Register the tool
            self.tools[name] = {
                "name": name,
                "description": description,
                "parameters": parameters,
                "returns": returns,
                "function": wrapper
            }
            
            # Add FastAPI route
            self.router.add_api_route(
                f"/tools/{name}",
                wrapper,
                methods=["POST"],
                response_model=returns.get("type", Dict[str, Any]),
                name=name,
                description=description
            )
            
            return wrapper
        return decorator

    def setup_routes(self, app: FastAPI):
        """Add all tool routes to the FastAPI application."""
        app.include_router(self.router, prefix="/mcp") 