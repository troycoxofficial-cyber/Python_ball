import random
from coach_traits import COACH_TRAITS

class Coach:
    # Existing Archetypes
    DEV_ARCHETYPES = [
        "Generalist", "Quarterback Guru", "Offensive Specialist",
        "Defensive Specialist", "Trench Master", "Skill Developer"
    ]

    def __init__(self, first_name, last_name, rating=None, fixed_archetype=None, age=None, alma_mater=None):
        self.first_name = first_name
        self.last_name = last_name
        
        # --- PERSONAL DATA ---
        self.age = age if age else random.randint(32, 65)
        self.years_at_school = 0
        self.alma_mater = alma_mater # Name of the school they played/graduated from
        
        # --- JOB SECURITY & CONTRACTS ---
        # Fan Support: 100 = God Status, 50 = Neutral, < 10 = Fired
        self.fan_support = 80 
        self.salary = 0             # In Dollars
        self.contract_years = 0     # Years remaining
        self.loyalty_rating = random.randint(1, 10) # 1 = Mercenary, 10 = Lifer
        
        # --- BASE STATS ---
        base_rating = rating if rating is not None else random.randint(10, 60)
        self.development_skill = max(1, min(10, int(base_rating / 10)))
        
        # --- PERSONALITY & SCHEME ---
        self.run_pass_bias = random.randint(0, 10) # 0=Run, 10=Pass
        self.aggressiveness = random.randint(0, 10) 
        self.fourth_down_agg = random.randint(0, 10) 
        self.tempo_bias = random.randint(0, 10)

        # --- DEVELOPMENT ARCHETYPE ---
        if fixed_archetype and fixed_archetype in self.DEV_ARCHETYPES:
            self.development_archetype = fixed_archetype
        else:
            self.development_archetype = random.choice(self.DEV_ARCHETYPES)

        # --- HISTORY & LEGACY ---
        self.history = [] # List of dicts: {year, team, record, conf_record, awards}
        self.career_wins = 0
        self.career_losses = 0
        self.championships = 0

        # --- TRAIT GENERATION ---
        self.traits = []
        self._generate_traits(base_rating)

    # Legacy property for compatibility with other modules that might check job_security
    @property
    def job_security(self):
        return self.fan_support

    @job_security.setter
    def job_security(self, value):
        self.fan_support = value

    def _generate_traits(self, rating):
        """Assigns traits based on coach quality."""
        num_traits = 1
        if rating > 50: num_traits = 2
        if rating > 80: num_traits = 3
        if rating > 90: num_traits = 4
        
        available = list(COACH_TRAITS.keys())
        random.shuffle(available)
        
        count = 0
        while count < num_traits and available:
            candidate = available.pop()
            has_conflict = False
            candidate_data = COACH_TRAITS[candidate]
            if "conflict" in candidate_data:
                for existing in self.traits:
                    if existing in candidate_data["conflict"]:
                        has_conflict = True
                        break
            
            if not has_conflict:
                self.traits.append(candidate)
                count += 1

    @property
    def full_name(self):
        return f"HC {self.first_name} {self.last_name}"

    @property
    def style_string(self):
        """Returns a string describing style (e.g., 'Air Raid / Aggressive')."""
        style = "Balanced"
        if self.run_pass_bias >= 7: style = "Air Raid"
        elif self.run_pass_bias <= 3: style = "Smashmouth"
        
        if self.aggressiveness >= 7: style += " / Aggressive"
        elif self.aggressiveness <= 3: style += " / Conservative"
        
        return style
        
    @property
    def scheme_type(self):
        """Simplified scheme identifier for hiring logic."""
        if self.run_pass_bias >= 7: return "Spread"
        if self.run_pass_bias <= 3: return "Power"
        return "Pro-Style"

    def sign_contract(self, salary, years):
        """Updates contract terms."""
        self.salary = salary
        self.contract_years = years
        self.fan_support = 80 # Reset support (Honeymoon period)

    def archive_season(self, year, team_name, wins, losses, conf_wins, conf_losses, awards=None):
        """Saves the season record to the coach's history."""
        entry = {
            "year": year,
            "team": team_name,
            "record": f"{wins}-{losses}",
            "conf_record": f"{conf_wins}-{conf_losses}",
            "awards": awards or []
        }
        self.history.append(entry)
        self.career_wins += wins
        self.career_losses += losses
        if "National Champ" in (awards or []):
            self.championships += 1
        
        self.age += 1
        self.years_at_school += 1

    def check_retirement(self):
        """Determines if the coach decides to retire based on age and success."""
        if self.age < 55: return False
        
        # Base chance increases with age
        chance = (self.age - 55) * 2 # 60yo = 10%, 65yo = 20%, 70yo = 30%
        
        # Force retirement cap
        if self.age >= 75: return True
        
        # Success factors
        # If they just won a natty, small chance to ride off into sunset
        if self.history and "National Champ" in self.history[-1]['awards']:
            chance += 15 
            
        return random.randint(1, 100) <= chance

    # --- SCHEME SPECIFIC TRAINING WEIGHTS ---
    def get_training_focus(self, position):
        """Returns a list of attributes to prioritize based on scheme."""
        focus = []
        
        # 1. Scheme Bias (Air Raid vs Smashmouth)
        if self.run_pass_bias >= 7: # Air Raid
            if position in ["QB", "WR", "TE"]:
                focus = ["THP", "ACC", "CTH", "SPD", "AGI"]
            elif position == "OL":
                focus = ["BLK", "AGI"] # Pass blocking needs agility
        elif self.run_pass_bias <= 3: # Smashmouth
            if position in ["RB", "OL", "TE", "DL"]:
                focus = ["STR", "BLK", "TKL", "durability"] # Toughness focus
            elif position == "QB":
                focus = ["SPD", "ACC"] # Option QB needs speed
        
        # 2. Archetype Bias
        if self.development_archetype == "Trench Master" and position in ["OL", "DL"]:
            focus.append("STR")
        elif self.development_archetype == "Skill Developer" and position in ["WR", "DB"]:
            focus.append("SPD")
            
        return focus

    def get_recruiting_bonus(self, recruit, school):
        """
        Returns a score modifier for recruiting a specific player.
        """
        bonus = 0
        
        # 1. SCHEME FIT
        if self.run_pass_bias >= 7: # Air Raid
            if recruit.position in ["WR", "TE"] and recruit.attributes["SPD"] > 80:
                bonus += 100
            if recruit.position == "QB" and recruit.attributes["THP"] > 80:
                bonus += 120
        elif self.run_pass_bias <= 3: # Smashmouth
            if recruit.position in ["OL", "RB"] and recruit.attributes["STR"] > 80:
                bonus += 100
        
        # 2. Trait Bonuses
        if "Pipeline: South" in self.traits and recruit.home_region == "SOUTH": bonus += 150
        if "Pipeline: North" in self.traits and recruit.home_region == "NORTH": bonus += 150
        if "Pipeline: West" in self.traits and recruit.home_region == "WEST": bonus += 150
        
        if "Five Star Chaser" in self.traits:
            if recruit.stars >= 4: bonus += 120
            elif recruit.stars <= 2: bonus -= 50
            
        if "Diamond in the Rough" in self.traits:
            if recruit.stars <= 3: 
                bonus += 100
                if recruit.potential > 80: bonus += 50
            
        if "Quarterback Guru" in self.traits and recruit.position == "QB": bonus += 60
        if "Trench Master" in self.development_archetype and recruit.position in ["OL", "DL"]: bonus += 40
        if "Living Room Legend" in self.traits: bonus += 50
        if "Snake Oil Salesman" in self.traits: bonus += 65
        if "Socially Awkward" in self.traits: bonus -= 40
        if "JuCo Bandit" in self.traits and getattr(recruit, 'is_juco', False): bonus += 200

        return bonus

    def get_game_bonus(self, context, **kwargs):
        """Generic hook for game_sim.py to ask for bonuses."""
        val = 0
        if context == "4th_down":
            if "Fourth Down Fire" in self.traits: val += 15
            if "Gut Feeling" in self.traits and random.random() < 0.3: val += 20
        elif context == "play_recognition":
            if "The Analyst" in self.traits: val += 10
        elif context == "int_chance_defense":
            if "Defensive Mastermind" in self.traits: val += 10
        elif context == "qb_attributes":
            if "Quarterback Whisperer" in self.traits: val += 5
        elif context == "halftime":
            diff = kwargs.get('score_diff', 0)
            if "Halftime Adjuster" in self.traits and diff < 0: val += 5
        elif context == "penalty_chance":
            if "Disciplinarian" in self.traits: val -= 20
            if "Player's Coach" in self.traits: val += 20
            if "Clock Manager" in self.traits: val -= 10
            
        return val

    def get_dev_bonus(self, position):
        """Base dev bonus."""
        bonus_rolls = int(self.development_skill / 2)
        if self.development_archetype == "Quarterback Guru" and position == "QB": bonus_rolls += 8
        elif self.development_archetype == "Offensive Specialist" and position in ["QB","RB","WR","TE","OL"]: bonus_rolls += 4
        elif self.development_archetype == "Defensive Specialist" and position in ["DL","LB","DB"]: bonus_rolls += 4
        elif self.development_archetype == "Trench Master" and position in ["OL","DL"]: bonus_rolls += 6
        elif self.development_archetype == "Skill Developer" and position in ["WR","DB","RB"]: bonus_rolls += 6

        if "Weight Room Obsessed" in self.traits: bonus_rolls += 3
        if "Technician" in self.traits: bonus_rolls += 2
        if "Program Builder" in self.traits: bonus_rolls += 1
        return bonus_rolls

    def __str__(self):
        salary_str = f"${self.salary/1000000:.1f}M" if self.salary > 0 else "N/A"
        return f"{self.full_name} ({self.career_wins}-{self.career_losses}) | {salary_str} thru {self.contract_years}yrs"