import sys
import httpx
from session_service import save_player_session

def register(player_name: str):
    player_name = str.lower(player_name).strip()
    
    try:
        response = httpx.post(
            "http://localhost:8000/players",
            json={"name": player_name}
        )
        
        if response.status_code == 201:
            player_data = response.json()
            print(f"May the odds be in your favor {player_data['name']}!")

            player_id = player_data.get("id")
            if isinstance(player_id, int):
                save_player_session(player_id)
                board_response = httpx.get(
                    f"http://localhost:8000/players/{player_id}/board",
                    headers={"Authorization": f"Bearer {player_id}"},
                )

                if board_response.status_code != 200:
                    print("Unable to load board right now.")
        elif response.status_code == 422:
            error_detail = response.json()
            error_msg = error_detail.get("detail", {}).get("error", {}).get("description", "Invalid player name")
            
            if error_msg == "Name must be unique":
                print("That name is already taken. Please choose another.")
            elif error_msg == "Name is required":
                print("Name cannot be empty.")
            elif error_msg == "Invalid player name":
                print("Invalid player name. Please use only letters, numbers, underscores, or hyphens.")
                
            sys.exit(1)
        else:
            print(f"Failed to register player (status code: {response.status_code})")
            sys.exit(1)
    except httpx.ConnectError:
        print("Looks like the wurdal servers are taking a loss... try again later!")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)