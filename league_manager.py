import pickle
import os

SAVE_FILE = "football_league.save"

def save_league(league_data):
    """Saves the current state of the league (schools, players, history) to a file."""
    try:
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(league_data, f)
        print(f"\n[System] League successfully saved to {SAVE_FILE}.")
        return True
    except Exception as e:
        print(f"[Error] Failed to save league: {e}")
        return False

def load_league():
    """Loads a league from the save file if it exists."""
    if not os.path.exists(SAVE_FILE):
        return None
    
    try:
        with open(SAVE_FILE, "rb") as f:
            league_data = pickle.load(f)
        print(f"\n[System] League loaded successfully.")
        return league_data
    except Exception as e:
        print(f"[Error] Save file corrupted or unreadable: {e}")
        return None

def save_exists():
    return os.path.exists(SAVE_FILE)