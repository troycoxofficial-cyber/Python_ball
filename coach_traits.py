# coach_traits.py

COACH_TRAITS = {
    # --- TIER 1: GAMEDAY COMMANDERS (Tactical Impacts) ---
    "The Analyst": {
        "type": "GAME_DAY",
        "desc": "Offense gets a bonus to 'Play Recognition' (countering defensive setups).",
        "conflict": ["Gut Feeling"]
    },
    "Gut Feeling": {
        "type": "GAME_DAY",
        "desc": "High variance play calling. occasional massive boosts on 4th down conversions.",
        "conflict": ["The Analyst", "Conservative Caller"]
    },
    "Halftime Adjuster": {
        "type": "GAME_DAY",
        "desc": "Team attributes increase by +5 in the 3rd Quarter if losing.",
        "conflict": ["Stubborn"]
    },
    "Clock Manager": {
        "type": "GAME_DAY",
        "desc": "Effective clock usage in last 2 mins. AI makes smarter timeout/out-of-bounds decisions.",
        "conflict": ["Time Waster"]
    },
    "Fourth Down Fire": {
        "type": "GAME_DAY",
        "desc": "Team receives a massive morale/stat boost on 4th down attempts.",
        "conflict": ["Punt Protector"]
    },
    "Defensive Mastermind": {
        "type": "GAME_DAY",
        "desc": "Opposing QB INT chance increases by 10%.",
        "conflict": ["Offensive Guru"]
    },
    "Quarterback Whisperer": {
        "type": "GAME_DAY",
        "desc": "Starting QB receives +5 Awareness and +5 Accuracy on gameday.",
        "conflict": ["QB Killer"]
    },

    # --- TIER 2: RECRUITING SHARKS (Acquisition) ---
    "Pipeline: South": {
        "type": "RECRUITING",
        "desc": "Significantly boosts interest from recruits in SEC/ACC states (FL, GA, AL, TX).",
        "conflict": ["Pipeline: North", "Pipeline: West"]
    },
    "Pipeline: North": {
        "type": "RECRUITING",
        "desc": "Significantly boosts interest from recruits in Big Ten states (OH, MI, PA, NJ).",
        "conflict": ["Pipeline: South", "Pipeline: West"]
    },
    "Pipeline: West": {
        "type": "RECRUITING",
        "desc": "Significantly boosts interest from recruits in CA, AZ, OR, WA.",
        "conflict": ["Pipeline: South", "Pipeline: North"]
    },
    "Living Room Legend": {
        "type": "RECRUITING",
        "desc": "Small bonus to ALL recruits regardless of location.",
        "conflict": ["Socially Awkward"]
    },
    "Five Star Chaser": {
        "type": "RECRUITING",
        "desc": "Massive bonus for 4 and 5 star recruits, but penalty for 1-2 stars.",
        "conflict": ["Diamond in the Rough"]
    },
    "Diamond in the Rough": {
        "type": "RECRUITING",
        "desc": "Bonus to 2-star and 3-star recruits. Reveals their 'Potential' rating earlier.",
        "conflict": ["Five Star Chaser"]
    },
    "JuCo Bandit": {
        "type": "RECRUITING",
        "desc": "Massive interest bonus for Junior College players.",
        "conflict": ["Prep Purist"]
    },
    "Snake Oil Salesman": {
        "type": "RECRUITING",
        "desc": "High chance to flip a commit from another school on Signing Day.",
        "conflict": ["Honest Abe"]
    },

    # --- TIER 3: PROGRAM BUILDERS (Development & Off-Field) ---
    "Weight Room Obsessed": {
        "type": "DEVELOPMENT",
        "desc": "Entire team gets bonus Strength/Conditioning XP in offseason.",
        "conflict": ["Light Practice"]
    },
    "Technician": {
        "type": "DEVELOPMENT",
        "desc": "Bonus XP to technical skills (Catching, Tackling, Blocking).",
        "conflict": ["Raw Athlete"]
    },
    "Academic Stickler": {
        "type": "CULTURE",
        "desc": "No academic suspensions, but harder to recruit players with 'Grade Risk' trait.",
        "conflict": ["Win at All Costs"]
    },
    "Win at All Costs": {
        "type": "CULTURE",
        "desc": "Ignores character issues. Bonus to recruiting 'Toxic' players, but higher suspension risk.",
        "conflict": ["Academic Stickler", "Disciplinarian"]
    },

    # --- TIER 4: THE PORTAL & RETENTION (Future Proofing) ---
    "Retention King": {
        "type": "PORTAL",
        "desc": "Reduces the chance of players transferring out by 50%.",
        "conflict": ["Processed"]
    },
    "Portal Shark": {
        "type": "PORTAL",
        "desc": "Bonus interest from players currently in the Transfer Portal.",
        "conflict": ["Homegrown"]
    },
    "Mercenary Hunter": {
        "type": "PORTAL",
        "desc": "Specific bonus to Grad Transfers (1 year rentals).",
        "conflict": ["Program Builder"]
    },
    "Player's Coach": {
        "type": "CULTURE",
        "desc": "High Morale. Players rarely transfer, but Discipline/Penalties are higher.",
        "conflict": ["Drill Sergeant"]
    },
    "Drill Sergeant": {
        "type": "CULTURE",
        "desc": "Team Stamina drains slower (toughness), but higher transfer rate for backups.",
        "conflict": ["Player's Coach"]
    }
}