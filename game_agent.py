from strands import Agent, tool
from strands_tools import http_request, retrieve
import sys
import os
import io


GAME_AGENT_PROMPT = """You are a game information assistant. Analyze game data and answer questions.

To answer questions, use tools in the following order:
1. **Use retrieve tool first**: Always use the retrieve tool to search the Knowledge Base for game information.
2. **Internet search**: Only use http_request tool when Knowledge Base doesn't have enough information.

Important: For game-related questions, always search the Knowledge Base using retrieve tool first.
"""


@tool
def get_game_info(keyword: str) -> dict:
    """Search game metadata by keyword or title.
    
    Args:
        keyword: Game title or keyword to search
    """
    # Example game database (replace with actual API or database)
    game_database = {
        "zelda": {
            "title": "The Legend of Zelda: Breath of the Wild",
            "developer": "Nintendo",
            "year": 2017,
            "genre": ["Action", "Adventure"],
            "platform": ["Switch", "Wii U"]
        },
        "elden ring": {
            "title": "Elden Ring",
            "developer": "FromSoftware",
            "year": 2022,
            "genre": ["Action RPG"],
            "platform": ["PC", "PS5", "Xbox"]
        }
    }
    
    keyword_lower = keyword.lower()
    for key, game in game_database.items():
        if key in keyword_lower:
            return game
    
    return {"error": f"No game found for '{keyword}'"}


def safe_input(prompt: str) -> str:
    """Safely handle UTF-8 encoding errors in input."""
    try:
        return input(prompt).strip()
    except UnicodeDecodeError:
        try:
            if hasattr(sys.stdin, 'buffer'):
                sys.stdin = io.TextIOWrapper(
                    sys.stdin.buffer, 
                    encoding='utf-8', 
                    errors='replace'
                )
            return input(prompt).strip()
        except (UnicodeDecodeError, UnicodeError):
            try:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                line = sys.stdin.buffer.readline()
                return line.decode('utf-8', errors='replace').strip()
            except Exception:
                raise


def main():
    """Run the game information agent."""
    # Set Knowledge Base ID from environment variable
    kb_id = os.environ.get("KNOWLEDGE_BASE_ID")
    if not kb_id:
        print("Warning: KNOWLEDGE_BASE_ID environment variable not set")
        kb_id = input("Enter Knowledge Base ID: ").strip()
        os.environ["KNOWLEDGE_BASE_ID"] = kb_id
    
    agent = Agent(
        model="us.amazon.nova-lite-v1:0",
        system_prompt=GAME_AGENT_PROMPT,
        tools=[get_game_info, http_request, retrieve]
    )
    
    # Single query mode (command line argument)
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        try:
            response = agent(query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Interactive mode
    print("Game Information Agent started. Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = safe_input("Ask about games: ")
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Shutting down agent.")
                break
            
            if not query:
                print("Please enter a question.\n")
                continue
            
            try:
                response = agent(query)
                print(f"\n{response}\n")
            except Exception as e:
                print(f"\nError: {e}\n")
        
        except (KeyboardInterrupt, EOFError):
            print("\n\nShutting down agent.")
            break


if __name__ == "__main__":
    main()