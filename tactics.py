# --- FORMATIONS ---
FORMATIONS_OFF = [
    "I-Formation", "Singleback", "Shotgun", "Pistol", "Empty Set", "Goal Line"
]

FORMATIONS_DEF = [
    "4-3 Base", "3-4 Base", "Nickel", "Dime", "Goal Line Stand"
]

# --- OFFENSIVE PLAYS ---
# Time: Seconds ran off clock (Average including huddle)
# Routes: List of (Position, RouteType, TargetPriority)
# Priority: Higher = Primary read
OFF_PLAYS = {
    "RUN_POWER":   {
        "type": "RUN", "risk": 1, "reward": 4, "time": 50, "desc": "Power Run",
        "gap": "Inside" 
    },
    "RUN_ZONE":    {
        "type": "RUN", "risk": 2, "reward": 6, "time": 50, "desc": "Zone Run",
        "gap": "Off-Tackle"
    },
    "RUN_DRAW":    {
        "type": "RUN", "risk": 3, "reward": 8, "time": 55, "desc": "Draw Play",
        "gap": "Middle"
    },
    
    # PASS plays now include Route Concepts
    "PASS_QUICK":  {
        "type": "PASS", "risk": 2, "reward": 4, "time": 45, "desc": "Quick Slants",
        "routes": {
            "WR": ("Slant", 10), "TE": ("Flat", 8), "RB": ("Checkdown", 7)
        }
    },
    "PASS_SCREEN": {
        "type": "PASS", "risk": 3, "reward": 7, "time": 45, "desc": "WR Screen",
        "routes": {
            "WR": ("Screen", 10), "RB": ("Swing", 6), "TE": ("Block", 0)
        }
    },
    "PASS_STD":    {
        "type": "PASS", "risk": 5, "reward": 10,"time": 50, "desc": "Dropback (Dig/Curl)",
        "routes": {
            "WR": ("Curl", 10), "TE": ("Seam", 9), "RB": ("Block", 0)
        }
    },
    "PASS_PA":     {
        "type": "PASS", "risk": 6, "reward": 15,"time": 55, "desc": "Play Action Crossers",
        "routes": {
            "TE": ("Cross", 10), "WR": ("Post", 8), "RB": ("Fake", 0)
        }
    },
    "PASS_DEEP":   {
        "type": "PASS", "risk": 8, "reward": 30,"time": 50, "desc": "Four Verticals",
        "routes": {
            "WR": ("Go", 10), "TE": ("Go", 9), "RB": ("Block", 0)
        }
    },
}

# --- DEFENSIVE STRATEGIES ---
# Counters: What this defense is good against
# Weakness: What kills this defense
DEF_STRATEGIES = {
    "COVER_2":     {"desc": "Cover 2 Zone",   "bonus_vs": ["PASS_QUICK", "PASS_STD"], "weak_vs": ["RUN_POWER", "PASS_DEEP"]},
    "COVER_3":     {"desc": "Cover 3 Zone",   "bonus_vs": ["PASS_DEEP", "PASS_PA"],   "weak_vs": ["PASS_QUICK", "PASS_SCREEN"]},
    "MAN_1":       {"desc": "Man Coverage",   "bonus_vs": ["PASS_SCREEN", "RUN_ZONE"],"weak_vs": ["RUN_DRAW", "PASS_QUICK"]},
    "BLITZ_ZONE":  {"desc": "Zone Blitz",     "bonus_vs": ["PASS_STD", "RUN_DRAW"],   "weak_vs": ["PASS_QUICK", "RUN_POWER"]},
    "BLITZ_HEAVY": {"desc": "All Out Blitz",  "bonus_vs": ["RUN_ZONE", "RUN_POWER"],  "weak_vs": ["PASS_SCREEN", "PASS_PA"]},
    "GOAL_LINE":   {"desc": "Goal Line Stand","bonus_vs": ["RUN_POWER", "RUN_ZONE"],  "weak_vs": ["PASS_PA", "PASS_QUICK"]},
}