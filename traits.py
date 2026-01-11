# traits.py

TRAITS = {
    # --- TIER 1: ELITE (GOLD) ---
    "Field General": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Boosts Offensive Line blocking awareness when on field.",
        "conflicts": ["System Product", "Slow Processor", "Statue"]
    },
    "Clutch Gene": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Attributes +10 in 4th Quarter when score is within 7.",
        "conflicts": ["Choker"]
    },
    "Film Room Rat": {
        "tier": "GOLD",
        "type": "DEV",
        "desc": "Double XP gain for Mental attributes (INT, AWARENESS).",
        "conflicts": ["Lazy", "Party Animal", "Grade Risk"]
    },
    "Iron Man": {
        "tier": "GOLD",
        "type": "PHYSICAL",
        "desc": "Immune to 'Minor' and 'Moderate' injuries. Only suffers Severe ones.",
        "conflicts": ["Glass", "Soft", "Injury Prone", "Glass Cannon"]
    },
    "Route Technician": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Significant separation bonus on technical routes (Curl, Out, Comeback).",
        "conflicts": ["Raw Athlete"]
    },
    "Ball Hawk": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Deflection rolls count as Interception rolls 25% more often.",
        "conflicts": ["Stone Hands"]
    },
    "Trench Dog": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Stamina drains 50% slower during run plays.",
        "conflicts": ["Low Motor"]
    },
    "Locker Room Leader": {
        "tier": "GOLD",
        "type": "CULTURE",
        "desc": "Prevents teammates from transferring; reduces penalty rates.",
        "conflicts": ["Toxic", "Loner", "Mercenary"]
    },
    "Ice Veins": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "(Kicker/Punter) Immune to 'Icing' timeout penalties and pressure accuracy drops.",
        "conflicts": ["Shaky", "Choker"]
    },
    "Human Joystick": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "Massive bonus to YAC (Yards After Catch) and broken tackles.",
        "conflicts": ["Stiff Hips"]
    },
    "Brick Wall": {
        "tier": "GOLD",
        "type": "GAME_BUFF",
        "desc": "(OL) Negates the first 'Pass Rush Win' by a defender per drive.",
        "conflicts": ["Turnstile"]
    },

    # --- TIER 2: POSITIVE (SILVER) ---
    "Gym Rat": {
        "tier": "SILVER",
        "type": "DEV",
        "desc": "Small bonus to Strength training every week.",
        "conflicts": ["Lazy"]
    },
    "Scramble Drill": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "Accuracy increases when pocket collapses.",
        "conflicts": ["Statue"]
    },
    "Safety Valve": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "Guarantee catch on 3rd down if throw is < 5 yards.",
        "conflicts": ["Drop Prone", "Stone Hands"]
    },
    "Big Hitter": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "Slightly increased fumble force chance; slightly higher injury risk to self.",
        "conflicts": ["Ankle Biter"]
    },
    "Fan Favorite": {
        "tier": "SILVER",
        "type": "NARRATIVE",
        "desc": "Harder to cut/bench without lowering team prestige.",
        "conflicts": ["Villain"]
    },
    "Road Warrior": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "Negates Home Field Advantage penalties when playing away.",
        "conflicts": ["Homesick"]
    },
    "Coach's Pet": {
        "tier": "SILVER",
        "type": "CULTURE",
        "desc": "Will sign for less scholarship money/stay despite lack of playing time.",
        "conflicts": ["Mercenary", "Toxic"]
    },
    "First Step": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "(DL/Edge) Bonus to sack rolls on 3rd and Long.",
        "conflicts": ["Slow Starter"]
    },
    "Satellite": {
        "tier": "SILVER",
        "type": "GAME_BUFF",
        "desc": "(RB) Receives WR-level separation bonuses on passing routes.",
        "conflicts": ["Stone Hands"]
    },
    "Mentor": {
        "tier": "SILVER",
        "type": "CULTURE",
        "desc": "Boosts XP gain for younger players at the same position.",
        "conflicts": ["Loner"]
    },

    # --- TIER 3: MIXED / NEUTRAL (BRONZE) ---
    "Gunslinger": {
        "tier": "BRONZE",
        "type": "GAME_MIXED",
        "desc": "Throws Deep +20% more often. INT chance +10%.",
        "conflicts": ["Game Manager"]
    },
    "Game Manager": {
        "tier": "BRONZE",
        "type": "GAME_MIXED",
        "desc": "Throws Checkdowns +30% more often. Zero INTs, but low YPA.",
        "conflicts": ["Gunslinger", "Hero Ball"]
    },
    "Mercenary": {
        "tier": "BRONZE",
        "type": "CULTURE",
        "desc": "Development +10%, but 100% transfer chance if not starting.",
        "conflicts": ["Loyal", "Coach's Pet", "Locker Room Leader"]
    },
    "Glass Cannon": {
        "tier": "BRONZE",
        "type": "PHYSICAL",
        "desc": "Speed/Strength +5, but Injury Risk Multiplier is 3.0x.",
        "conflicts": ["Iron Man"]
    },
    "Trash Talker": {
        "tier": "BRONZE",
        "type": "GAME_MIXED",
        "desc": "Lowers opponent stats slightly, but high Personal Foul penalty risk.",
        "conflicts": ["Silent Assassin", "Choir Boy"]
    },
    "System Product": {
        "tier": "BRONZE",
        "type": "GAME_MIXED",
        "desc": "Elite performance in specific scheme (e.g. Spread), terrible in others.",
        "conflicts": ["Field General", "High IQ"]
    },
    "Weight Room Hero": {
        "tier": "BRONZE",
        "type": "PHYSICAL",
        "desc": "STR cap is 99, but SPD cap is lowered by 5.",
        "conflicts": ["Track Star"]
    },
    "Track Star": {
        "tier": "BRONZE",
        "type": "PHYSICAL",
        "desc": "SPD cap is 99, but TKL/STR caps lowered by 5.",
        "conflicts": ["Weight Room Hero"]
    },
    "Hero Ball": {
        "tier": "BRONZE",
        "type": "GAME_MIXED",
        "desc": "Ignores play call to scramble/throw deep if team is losing. 50/50 outcome.",
        "conflicts": ["Game Manager", "Coach's Pet"]
    },
    "Media Darling": {
        "tier": "BRONZE",
        "type": "NARRATIVE",
        "desc": "Increases School Prestige if he starts, but demands playing time.",
        "conflicts": ["Camera Shy"]
    },

    # --- TIER 4: NEGATIVE (RED) ---
    "Stone Hands": {
        "tier": "RED",
        "type": "GAME_DEBUFF",
        "desc": "Drop rate flat +10% regardless of coverage.",
        "conflicts": ["Sticky Hands", "Safety Valve", "Satellite"]
    },
    "Choker": {
        "tier": "RED",
        "type": "GAME_DEBUFF",
        "desc": "Attributes -15 in 4th Quarter of close games.",
        "conflicts": ["Clutch Gene", "Ice Veins"]
    },
    "Lazy": {
        "tier": "RED",
        "type": "DEV",
        "desc": "Skipped training sessions. 50% chance to gain 0 XP in offseason.",
        "conflicts": ["Gym Rat", "Film Room Rat"]
    },
    "Toxic": {
        "tier": "RED",
        "type": "CULTURE",
        "desc": "Lowers the Morale/Development of all other players at his position.",
        "conflicts": ["Locker Room Leader", "Mentor"]
    },
    "Injury Prone": {
        "tier": "RED",
        "type": "PHYSICAL",
        "desc": "Recover from injuries 2 weeks slower. Minor injuries become Moderate.",
        "conflicts": ["Iron Man", "Wolverine Blood"]
    },
    "Party Animal": {
        "tier": "RED",
        "type": "NARRATIVE",
        "desc": "Random chance to be suspended for games.",
        "conflicts": ["Film Room Rat", "Choir Boy"]
    },
    "Statue": {
        "tier": "RED",
        "type": "GAME_DEBUFF",
        "desc": "(QB) Sack Avoidance is halved. Cannot scramble.",
        "conflicts": ["Scrambler", "Escapist", "Field General"]
    },
    "Homesick": {
        "tier": "RED",
        "type": "CULTURE",
        "desc": "Attributes -5 if playing for a school >500 miles from home state.",
        "conflicts": ["Road Warrior"]
    },
    "Grade Risk": {
        "tier": "RED",
        "type": "NARRATIVE",
        "desc": "Random chance to be academically ineligible for Bowl Games.",
        "conflicts": ["Film Room Rat", "High IQ"]
    },
    "Turnstile": {
        "tier": "RED",
        "type": "GAME_DEBUFF",
        "desc": "(OL) Blocking rolls are penalized heavily on 3rd down.",
        "conflicts": ["Brick Wall"]
    },
    "Soft": {
        "tier": "RED",
        "type": "PHYSICAL",
        "desc": "Will sit out games for Minor injuries (Bruises).",
        "conflicts": ["Iron Man", "Trench Dog"]
    },
    "Ankle Biter": {
        "tier": "RED",
        "type": "GAME_DEBUFF",
        "desc": "Missed tackle rate increased significantly against STR-based runners.",
        "conflicts": ["Big Hitter"]
    }
}