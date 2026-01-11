
import random
import uuid
from traits import TRAITS

# --- GEOGRAPHY DATA ---
# Copied here to avoid circular imports with world_gen.py
REGIONS = {
    "SOUTH": ["Alabama", "Arkansas", "Florida", "Georgia", "Kentucky", "Louisiana", "Mississippi", "North Carolina", "South Carolina", "Tennessee", "Virginia", "West Virginia"],
    "NORTH": ["Connecticut", "Delaware", "Illinois", "Indiana", "Maine", "Maryland", "Massachusetts", "Michigan", "New Hampshire", "New Jersey", "New York", "Ohio", "Pennsylvania", "Rhode Island", "Vermont", "Wisconsin"],
    "WEST": ["Alaska", "Arizona", "California", "Colorado", "Hawaii", "Idaho", "Montana", "Nevada", "New Mexico", "Oregon", "Utah", "Washington", "Wyoming"],
    "MIDWEST": ["Iowa", "Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "Oklahoma", "South Dakota", "Texas"]
}

class Player:
    POSITION_WEIGHTS = {
        "QB": {"THP": 0.35, "ACC": 0.35, "INT": 0.15, "SPD": 0.10, "AGI": 0.05},
        "RB": {"SPD": 0.30, "AGI": 0.30, "STR": 0.20, "CTH": 0.10, "INT": 0.10},
        "WR": {"SPD": 0.35, "CTH": 0.35, "AGI": 0.20, "ACC": 0.05, "STR": 0.05},
        "TE": {"CTH": 0.35, "BLK": 0.35, "STR": 0.20, "SPD": 0.05, "INT": 0.05},
        "OL": {"BLK": 0.45, "STR": 0.40, "INT": 0.10, "AGI": 0.05},
        "DL": {"STR": 0.35, "TKL": 0.30, "AGI": 0.20, "BLK": 0.10, "INT": 0.05},
        "LB": {"TKL": 0.35, "STR": 0.25, "INT": 0.20, "SPD": 0.10, "AGI": 0.10},
        "DB": {"SPD": 0.30, "ACC": 0.20, "INT": 0.20, "CTH": 0.15, "TKL": 0.15},
        "K":  {"KPW": 0.60, "ACC": 0.40},
        "P":  {"KPW": 0.60, "ACC": 0.40}
    }

    def __init__(self, first_name, last_name, position, year, school_prestige, age=None, context="HS"):
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.context = context
        
        # --- Age & Eligibility ---
        self.eligibility_year = year
        if age:
            self.age = age
        else:
            base_age = 14 if context == "HS" else 18
            self.age = base_age + year

        # --- Recruiting Status ---
        self.stars = 0 
        self.recruit_rating = 0 
        self.commitment = None # Tracks verbal commitment (School Name)
        
        # --- Geography & Pipeline ---
        self.home_state = self._assign_home_state(context)
        self.home_region = self._get_region_from_state(self.home_state)
        
        # Added DUR (Durability) to attributes
        self.attributes = {
            "SPD": 0, "STR": 0, "AGI": 0, "INT": 0,
            "THP": 0, "ACC": 0, "CTH": 0, "BLK": 0, 
            "TKL": 0, "KPW": 0, "DUR": 0 
        }
        
        # --- Health & Stamina ---
        self.stamina = 100
        self.max_stamina = 100
        self.injury_type = None  
        self.weeks_injured = 0   
        
        # --- Personality ---
        # Loyalty: 0 (Mercenary) to 100 (Lifer)
        self.loyalty = random.randint(0, 100) 
        
        # --- Potential (The Ceiling) ---
        # UPDATED: Lowered HS mean potential from 68 -> 66 to reduce "Super Elite" saturation
        mean_pot = 66 if context == "HS" else 80
        
        # UPDATED: Increased variability from 10 to 15 to make potential more variable
        self.potential = int(random.gauss(mean_pot, 15))
        self.potential = max(40, min(99, self.potential))

        # --- FOG OF WAR: Hype Factor ---
        # Hype modifies how good a player LOOKS vs how good they ARE.
        self.hype_factor = random.randint(-12, 12)
        # Perceived potential is what scouts "see"
        self.perceived_potential = max(40, min(99, self.potential + self.hype_factor))

        self.history = []
        self.traits = [] 

        # Current Season Stats
        self.stats = {}
        self.reset_stats() 
        
        self.generate_attributes(school_prestige, context)
        self.overall = self.calculate_overall()
        
        # --- ASSIGN TRAITS ---
        self.assign_traits()
        
        # --- INITIAL STAR CALC (for HS Seniors generated at start) ---
        if context == "HS" and self.eligibility_year == 4:
            self.calculate_stars()

    def _assign_home_state(self, context):
        all_states = [s for r in REGIONS.values() for s in r]
        # Weighted random: Big football states produce more players
        weights = []
        for s in all_states:
            w = 1
            if s in ["Texas", "Florida", "California", "Georgia", "Ohio"]: w = 6
            elif s in ["Louisiana", "Alabama", "Pennsylvania", "Michigan"]: w = 3
            weights.append(w)
        return random.choices(all_states, weights=weights, k=1)[0]

    def _get_region_from_state(self, state):
        for region, states in REGIONS.items():
            if state in states: return region
        return "MIDWEST" # Fallback

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_injured(self):
        return self.weeks_injured > 0

    @property
    def year_str(self):
        years = {1: "Fr", 2: "So", 3: "Jr", 4: "Sr"}
        return years.get(self.eligibility_year, "Sr+")

    def check_transfer_intent(self, school, depth_chart_rank):
        """
        Determines if a player wants to enter the transfer portal.
        Returns (Bool, Reason_String).
        Uses Player Traits and Coach Traits.
        """
        if self.context == "HS": return False, ""
        
        # Base stats
        unhappiness = 0
        reason = ""
        
        coach_traits = []
        if school.coach:
            coach_traits = getattr(school.coach, 'traits', [])

        # 1. THE "HOLLYWOOD" FACTOR (Too good for this school)
        # 4/5 Star player at a low prestige school
        if self.stars >= 4 and school.prestige < 60:
            unhappiness += 50
            reason = "Seeking bigger brand"
            
        # 2. THE "BENCH WARMER" (Good player, not starting)
        if self.overall > 78 and depth_chart_rank > 1:
            unhappiness += 70
            reason = "Lack of playing time"
        elif self.overall > 74 and depth_chart_rank > 2:
            unhappiness += 50
            reason = "Buried on depth chart"
            
        # 3. THE "RAGE QUIT" (Team is losing)
        if school.wins < 4:
            unhappiness += 20
            if not reason: reason = "Winning culture"

        # --- TRAIT IMPACTS ---
        
        # Player Traits
        if "Mercenary" in self.traits:
            if depth_chart_rank > 1:
                unhappiness += 100 # GONE
                reason = "Mercenary demands start"
            else:
                unhappiness += 10 # Always looking
                
        if "Coach's Pet" in self.traits:
            unhappiness -= 40 # Very loyal
            
        if "Homesick" in self.traits:
            if self.home_region != school.region:
                unhappiness += 30
                reason = "Homesick"
                
        if "Fan Favorite" in self.traits:
            unhappiness -= 10
            
        # Coach Traits
        if "Retention King" in coach_traits:
            unhappiness -= 30
            
        if "Player's Coach" in coach_traits:
            unhappiness -= 20
            
        if "Drill Sergeant" in coach_traits:
            if depth_chart_rank > 1:
                unhappiness += 15 # Backups hate hard practice
                
        # 4. TAMPERING / CHAOS (Random Chance)
        # Even starters might leave if the bag is heavy
        tamper_chance = 0.05
        if "Mercenary" in self.traits: tamper_chance = 0.15
        
        if depth_chart_rank == 1 and random.random() < tamper_chance:
            unhappiness += 40
            reason = "Business decision (NIL)"
            
        # 5. GRAD TRANSFER (Senior year, want to start)
        if self.eligibility_year == 3 and depth_chart_rank > 1:
            unhappiness += 80
            reason = "Grad transfer for PT"

        # MITIGATING FACTOR: LOYALTY
        # High loyalty reduces unhappiness
        if "Team Captain" in self.traits: self.loyalty += 20
        unhappiness -= (self.loyalty / 2)
        
        # Final Roll
        # If unhappiness is high (e.g., 60), roll 1-100. If roll < 60, they leave.
        roll = random.randint(0, 100)
        
        if unhappiness > 0 and roll < unhappiness:
            return True, reason
            
        return False, ""

    def generate_attributes(self, prestige, context):
        """Generates attributes with STRICT Tiered Logic."""
        is_bad_team = prestige <= 5     
        is_avg_team = 5 < prestige <= 8 
        is_elite_team = prestige > 8    

        if context == "HS":
            # UPDATED: Boosted freshman floors by ~5 points to match Senior outcomes
            if is_bad_team:
                if self.eligibility_year == 1: base_range = (40, 47) 
                elif self.eligibility_year == 2: base_range = (45, 53)
                elif self.eligibility_year == 3: base_range = (52, 58)
                else:                            base_range = (55, 63) 
                hard_cap = 68 
            elif is_avg_team:
                if self.eligibility_year == 1: base_range = (43, 50) 
                elif self.eligibility_year == 2: base_range = (49, 57)
                elif self.eligibility_year == 3: base_range = (56, 64)
                else:                            base_range = (60, 69)
                hard_cap = 75 
            else: 
                if self.eligibility_year == 1: base_range = (47, 55) 
                elif self.eligibility_year == 2: base_range = (54, 62)
                elif self.eligibility_year == 3: base_range = (62, 70)
                else:                            base_range = (68, 76)
                hard_cap = 80 
            
            # --- SKILL POSITION BUFF (ADJUSTED) ---
            if self.position in ["QB", "RB", "WR", "LB", "DB"]:
                # Slightly less good than the previous 3-7 range
                bonus = random.randint(2, 6)
            else:
                # Other positions are slightly worse
                bonus = random.randint(-2, -1)
        else:
            # College Generation Logic (for initial world gen)
            if self.eligibility_year == 1:   base_range = (50, 60) 
            elif self.eligibility_year == 2: base_range = (56, 64)
            elif self.eligibility_year == 3: base_range = (62, 70)
            else:                            base_range = (66, 75)
            # Prestige 1-99 scaling
            bonus = int((prestige / 100.0) * 25)
            hard_cap = 99 
            if self.eligibility_year == 1: hard_cap = 82
            if self.eligibility_year == 2: hard_cap = 88

        min_r, max_r = base_range
        raw_rating = random.randint(min_r, max_r) + bonus
        target_rating = min(hard_cap, raw_rating)

        primary_boost = 5 if context == "HS" else 6
        secondary_penalty = -5 if context == "HS" else -6

        weights = self.POSITION_WEIGHTS.get(self.position, {})
        for attr in self.attributes:
            if attr == "DUR":
                self.attributes[attr] = random.randint(60, 99)
                continue
            if attr in weights:
                val = target_rating + primary_boost + random.randint(-2, 2)
            else:
                val = target_rating + secondary_penalty + random.randint(-5, 5)
            self.attributes[attr] = int(max(1, min(99, val)))

    def assign_traits(self):
        self.traits = []
        count_roll = random.randint(1, 100)
        
        if count_roll > 60: num_traits = 5
        elif count_roll > 20: num_traits = 4
        else: num_traits = 3

        if self.overall >= 80:
            weights = [35, 40, 20, 5]   
        elif self.overall >= 60:
            weights = [10, 30, 40, 20]  
        else:
            weights = [5, 15, 40, 40]   

        attempts = 0
        while len(self.traits) < num_traits and attempts < 100:
            attempts += 1
            tier_choice = random.choices(["GOLD", "SILVER", "BRONZE", "RED"], weights=weights, k=1)[0]
            candidates = [k for k, v in TRAITS.items() if v["tier"] == tier_choice]
            if not candidates: continue
            
            new_trait_name = random.choice(candidates)
            new_trait_data = TRAITS[new_trait_name]
            
            has_conflict = False
            if new_trait_name in self.traits: has_conflict = True
            if not has_conflict:
                for existing in self.traits:
                    if existing in new_trait_data.get("conflicts", []): has_conflict = True
                    if new_trait_name in TRAITS[existing].get("conflicts", []): has_conflict = True
            
            if not has_conflict:
                self.traits.append(new_trait_name)

    def calculate_overall(self):
        weights = self.POSITION_WEIGHTS.get(self.position)
        if not weights: return 40
        weighted_sum = 0
        total_weight = 0
        for attr, weight in weights.items():
            weighted_sum += self.attributes.get(attr, 0) * weight
            total_weight += weight
        if total_weight == 0: return 0
        return int(weighted_sum / total_weight)
    
    def calculate_stars(self):
        # STAR RATING: Based on Perceived Potential (Fog of War) + Current Ability
        if self.context == "HS":
            score = self.overall
            # If perceived potential is high, boost the rating significantly
            if self.perceived_potential > 70: 
                score += (self.perceived_potential - 70) * 0.6
            
            # Special Teams Nerf (K/P)
            if self.position in ["K", "P"]:
                score -= 15 # Severe penalty to star calculation for specialists

            dur = self.attributes.get("DUR", 80)
            if dur < 70: score -= 3 
            elif dur > 90: score += 1 
            
            self.recruit_rating = int(score)
            
            # UPDATED: STRICTER THRESHOLDS FOR REALISM (IRL-like distribution)
            if score >= 84: self.stars = 5   # Top ~30-40 players
            elif score >= 76: self.stars = 4 # Top ~300-400 players
            elif score >= 68: self.stars = 3 # FBS Caliber
            elif score >= 60: self.stars = 2 # G5/FCS Caliber
            else: self.stars = 1
        else:
            # College players use real overall
            self.recruit_rating = self.overall 
            if self.overall >= 88: self.stars = 5   
            elif self.overall >= 82: self.stars = 4 
            elif self.overall >= 75: self.stars = 3 
            elif self.overall >= 68: self.stars = 2 
            else: self.stars = 1
        return self.stars

    def reset_stats(self):
        self.stats = {
            "pass_att": 0, "pass_cmp": 0, "pass_yds": 0, "pass_td": 0, "pass_int": 0, "sacks_taken": 0,
            "rush_att": 0, "rush_yds": 0, "rush_td": 0, "fumbles": 0,
            "rec_cat": 0, "rec_yds": 0, "rec_td": 0,
            "tackles": 0, "sacks": 0, "int_made": 0, "def_td": 0,
            "fg_made": 0, "fg_att": 0, "punts": 0, "punt_yds": 0
        }
        self.stamina = 100

    def get_stat_summary(self, stats_dict=None):
        """Returns a formatted string of the most relevant stats for this player's position."""
        if stats_dict is None:
            stats_dict = self.stats
        
        s = stats_dict
        if self.position == "QB":
            return f"{s.get('pass_yds',0)} yds | [green]{s.get('pass_td',0)} TD[/green] | [red]{s.get('pass_int',0)} INT[/red]"
        elif self.position in ["RB", "WR", "TE"]:
            tot_yds = s.get('rush_yds',0) + s.get('rec_yds',0)
            tot_td = s.get('rush_td',0) + s.get('rec_td',0)
            return f"{tot_yds} tot yds | [green]{tot_td} TD[/green]"
        elif self.position in ["LB", "DB", "DL"]:
            return f"{s.get('tackles',0)} Tkl | {s.get('sacks',0)} Sck | [green]{s.get('int_made',0)} INT[/green]"
        elif self.position == "K":
            return f"{s.get('fg_made',0)}/{s.get('fg_att',0)} FG"
        elif self.position == "P":
            return f"{s.get('punts',0)} Punts | {s.get('punt_yds',0)} Yds"
        return "No measurable stats."
        
    def recover_health_weekly(self):
        if self.weeks_injured > 0:
            rec_amt = 1
            # TRAIT: Wolverine Blood (Heals faster)
            if "Wolverine Blood" in self.traits: rec_amt += 1
            # TRAIT: Injury Prone (Heals slower)
            if "Injury Prone" in self.traits and random.random() < 0.5: rec_amt = 0

            self.weeks_injured -= rec_amt
            if self.weeks_injured <= 0:
                self.weeks_injured = 0
                self.injury_type = None
        self.stamina = 100

    def train(self, coach=None):
        # ... (Existing Lazy Trait Logic) ...
        if "Lazy" in self.traits and random.random() < 0.5:
            return

        # ... (Growth Chances Calculation logic remains the same) ...
        if self.context == "HS": growth_chances = 10 
        else: growth_chances = 25

        if self.potential > 70: growth_chances += 3 
        if self.potential > 85: growth_chances += 3 
        if self.potential > 95: growth_chances += 5 

        if "Gym Rat" in self.traits: growth_chances += 5 
        if "Film Room Rat" in self.traits: growth_chances += 5 

        if coach:
            # Use safe getattr incase Coach object is old version
            dev_bonus = getattr(coach, 'development_skill', 5)
            if hasattr(coach, 'get_dev_bonus'):
                dev_bonus = coach.get_dev_bonus(self.position)
            growth_chances += int(dev_bonus * 2)

        # --- NEW: SCHEME SPECIFIC FOCUS ---
        weights = self.POSITION_WEIGHTS.get(self.position, {})
        relevant_attrs = list(weights.keys())
        if random.random() < 0.1: relevant_attrs.append("DUR")
        
        # Get Coach Preferences
        coach_focus = []
        if coach and hasattr(coach, 'get_training_focus'):
            coach_focus = coach.get_training_focus(self.position)

        improved = False
        
        for _ in range(growth_chances):
            roll = random.randint(1, 100)
            if roll <= self.potential:
                
                # Selection Logic: 50% chance to pick from Coach Focus (if exists)
                if coach_focus and random.random() < 0.5:
                    # Filter focus to ensure valid attrs for this player
                    valid_focus = [f for f in coach_focus if f in self.attributes]
                    if valid_focus:
                        attr_to_boost = random.choice(valid_focus)
                    else:
                        attr_to_boost = random.choice(relevant_attrs)
                else:
                    attr_to_boost = random.choice(relevant_attrs)
                
                # ... (Existing Cap Logic) ...
                cap = 99
                if attr_to_boost == "STR" and "Weight Room Hero" in self.traits: cap = 99
                if attr_to_boost == "SPD" and "Weight Room Hero" in self.traits: cap = 90
                
                # HS Caps
                if self.context == "HS":
                    if self.eligibility_year == 1 and self.attributes[attr_to_boost] > 60: continue
                    if self.eligibility_year == 2 and self.attributes[attr_to_boost] > 70: continue
                    if self.eligibility_year == 3 and self.attributes[attr_to_boost] > 80: continue

                if self.attributes[attr_to_boost] < cap:
                    self.attributes[attr_to_boost] += 1
                    improved = True
        
        if improved:
            self.overall = self.calculate_overall()

    def archive_season(self, team_name, team_record, year):
        season_log = {
            "year": year,
            "year_class": self.year_str,
            "age": self.age,
            "team": team_name,
            "record": team_record,
            "overall": self.overall,
            "stats": self.stats.copy() 
        }
        self.history.append(season_log)

    def __str__(self):
        stars_str = "*" * self.stars if self.stars > 0 else ""
        inj_str = f" [INJ: {self.injury_type} ({self.weeks_injured} wks)]" if self.weeks_injured > 0 else ""
        trait_str = f" [{len(self.traits)} Traits]" if self.traits else ""
        return f"[{self.overall}] {self.position} {self.full_name} {stars_str}{inj_str}{trait_str}"
