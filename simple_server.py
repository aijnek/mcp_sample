from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")
print("Starting FastMCP server...")

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two numbers together.
    """
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    Subtracts the second number from the first.
    """
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiplies two numbers together.
    """
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """
    Divides the first number by the second.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@mcp.resource("users://profile/{user_id}")
def get_user_profile(user_id: str) -> dict:
    """
    Fetches the user profile for the given user ID.
    """
    # Simulate fetching user profile from a database
    user_profiles = {
        "1": {"name": "Alice", "age": 30},
        "2": {"name": "Bob", "age": 25},
        "3": {"name": "Charlie", "age": 35},
    }
    return user_profiles.get(user_id, {"error": "User not found"})

@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return "App configuration here"

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="stdio")