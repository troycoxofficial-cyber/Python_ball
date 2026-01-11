import random
from player import Player
from coach import Coach
from scheduler import generate_schedule

# --- Configuration ---
ROSTER_SIZE = 52
POSITION_TEMPLATE = [("QB", 3), ("RB", 5), ("WR", 7), ("TE", 3), ("OL", 9), ("DL", 8), ("LB", 7), ("DB", 8), ("K", 1), ("P", 1)]

# --- HIGH SCHOOL DATA ---
REGIONS = {
    "SOUTH": ["Alabama", "Arkansas", "Florida", "Georgia", "Kentucky", "Louisiana", "Mississippi", "North Carolina", "South Carolina", "Tennessee", "Virginia", "West Virginia"],
    "NORTH": ["Connecticut", "Delaware", "Illinois", "Indiana", "Maine", "Maryland", "Massachusetts", "Michigan", "New Hampshire", "New Jersey", "New York", "Ohio", "Pennsylvania", "Rhode Island", "Vermont", "Wisconsin"],
    "WEST": ["Alaska", "Arizona", "California", "Colorado", "Hawaii", "Idaho", "Montana", "Nevada", "New Mexico", "Oregon", "Utah", "Washington", "Wyoming"],
    "MIDWEST": ["Iowa", "Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "Oklahoma", "South Dakota", "Texas"]
}
DIRECTIONS = ["North", "South", "East", "West", "Northeast", "Northwest", "Southeast", "Southwest", "Central"]
TYPES = ["State"]

# --- COLLEGE DATA (Format: Name, Conf, PrevRec, Coach, Prestige, CoachRating) ---
COLLEGE_DB = [
    ["Boston College","ACC","2-10","Bill O'Brien",40,65],
    ["California","ACC","7-6","Tosh Lupoi",55,70],
    ["Clemson","ACC","7-6","Dabo Swinney",82,75],
    ["Duke","ACC","8-5","Manny Diaz",65,85],
    ["Florida State","ACC","5-7","Mike Norvell",80,60],
    ["Georgia Tech","ACC","9-4","Brent Key",68,80],
    ["Louisville","ACC","9-4","Jeff Brohm",69,80],
    ["Miami (FL)","ACC","11-2","Mario Cristobal",88,85],
    ["NC State","ACC","8-5","Dave Doeren",62,75],
    ["North Carolina","ACC","4-8","Bill Belichick",65,80],
    ["Pittsburgh","ACC","8-5","Pat Narduzzi",60,70],
    ["SMU","ACC","8-4","Rhett Lashlee",65,75],
    ["Stanford","ACC","4-8","Tavita Pritchard",50,65],
    ["Syracuse","ACC","3-10","Fran Brown",35,60],
    ["Virginia","ACC","11-3","Tony Elliott",68,80],
    ["Virginia Tech","ACC","3-9","James Franklin",74,90],
    ["Wake Forest","ACC","8-4","Jake Dickert",58,75],
    ["Army","AAC","6-6","Jeff Monken",60,80],
    ["Charlotte","AAC","1-11","Tim Albin",15,65],
    ["East Carolina","AAC","9-4","Blake Harrell",45,70],
    ["Florida Atlantic","AAC","4-8","Zach Kittley",35,65],
    ["Memphis","AAC","8-5","Charles Huff",58,75],
    ["Navy","AAC","10-2","Brian Newberry",62,80],
    ["North Texas","AAC","11-2","Neal Brown",48,75],
    ["Rice","AAC","5-7","Scott Abell",30,60],
    ["South Florida","AAC","9-4","Brian Hartline",48,80],
    ["Temple","AAC","5-7","K.C. Keeler",35,65],
    ["Tulane","AAC","11-3","Will Hall",68,70],
    ["Tulsa","AAC","4-8","Tre Lamb",35,65],
    ["UAB","AAC","4-8","Alex Mortensen",35,60],
    ["UTSA","AAC","7-6","Jeff Traylor",45,75],
    ["Arizona","Big 12","9-3","Brent Brennan",65,75],
    ["Arizona State","Big 12","8-4","Kenny Dillingham",65,75],
    ["Baylor","Big 12","5-7","Dave Aranda",58,60],
    ["BYU","Big 12","12-2","Kalani Sitake",68,85],
    ["Cincinnati","Big 12","7-5","Scott Satterfield",62,65],
    ["Colorado","Big 12","3-9","Deion Sanders",60,50],
    ["Houston","Big 12","10-3","Willie Fritz",65,85],
    ["Iowa State","Big 12","8-4","Jimmy Rogers",62,75],
    ["Kansas","Big 12","5-7","Lance Leipold",50,75],
    ["Kansas State","Big 12","6-6","Collin Klein",68,80],
    ["Oklahoma State","Big 12","1-11","Eric Morris",55,70],
    ["TCU","Big 12","8-4","Sonny Dykes",68,75],
    ["Texas Tech","Big 12","12-1","Joey McGuire",78,90],
    ["UCF","Big 12","5-7","Scott Frost",62,65],
    ["Utah","Big 12","10-2","Morgan Scalley",82,80],
    ["West Virginia","Big 12","4-8","Rich Rodriguez",60,70],
    ["Illinois","Big Ten","8-4","Bret Bielema",62,75],
    ["Indiana","Big Ten","13-0","Curt Cignetti",85,100],
    ["Iowa","Big Ten","8-4","Kirk Ferentz",78,85],
    ["Maryland","Big Ten","4-8","Mike Locksley",55,60],
    ["Michigan","Big Ten","9-3","Kyle Whittingham",95,95],
    ["Michigan State","Big Ten","4-8","Pat Fitzgerald",75,80],
    ["Minnesota","Big Ten","8-5","P.J. Fleck",62,75],
    ["Nebraska","Big Ten","7-5","Matt Rhule",78,75],
    ["Northwestern","Big Ten","7-6","David Braun",55,70],
    ["Ohio State","Big Ten","12-1","Ryan Day",98,90],
    ["Oregon","Big Ten","12-1","Dan Lanning",96,95],
    ["Penn State","Big Ten","6-6","Matt Campbell",90,85],
    ["Purdue","Big Ten","2-10","Barry Odom",50,70],
    ["Rutgers","Big Ten","5-7","Greg Schiano",45,70],
    ["UCLA","Big Ten","3-9","Bob Chesney",75,80],
    ["USC","Big Ten","9-3","Lincoln Riley",92,80],
    ["Washington","Big Ten","9-4","Jedd Fisch",82,80],
    ["Wisconsin","Big Ten","4-8","Luke Fickell",78,65],
    ["Delaware","C-USA","7-6","Ryan Carty",25,65],
    ["FIU","C-USA","7-6","Willie Simmons",25,65],
    ["Jacksonville St","C-USA","9-5","New Coach",40,50],
    ["Kennesaw State","C-USA","10-4","Jerry Mack",35,75],
    ["Liberty","C-USA","4-8","Jamey Chadwell",55,75],
    ["Louisiana Tech","C-USA","7-5","Sonny Cumbie",40,65],
    ["Middle Tennessee","C-USA","3-9","Derek Mason",20,60],
    ["Missouri State","C-USA","7-6","Ryan Beard",20,65],
    ["New Mexico State","C-USA","4-8","Tony Sanchez",15,55],
    ["Sam Houston","C-USA","2-10","Phil Longo",15,70],
    ["UTEP","C-USA","2-10","Scotty Walden",15,55],
    ["Western Kentucky","C-USA","9-4","Tyson Helton",45,75],
    ["Akron","MAC","5-7","Joe Moorhead",20,65],
    ["Ball State","MAC","4-8","Mike Uremovich",20,65],
    ["Bowling Green","MAC","4-8","Eddie George",30,60],
    ["Buffalo","MAC","5-7","Pete Lembo",25,65],
    ["Central Michigan","MAC","7-6","Matt Drinkall",35,65],
    ["Eastern Michigan","MAC","4-8","Chris Creighton",35,70],
    ["Kent State","MAC","5-7","Mark Carney",20,70],
    ["Massachusetts","MAC","0-12","Joe Harasymiak",5,60],
    ["Miami (OH)","MAC","7-7","Chuck Martin",40,75],
    ["Northern Illinois","MAC","3-9","Thomas Hammock",35,60],
    ["Ohio","MAC","9-4","John Hauser",45,65],
    ["Toledo","MAC","8-5","Mike Jacobs",45,70],
    ["Western Michigan","MAC","10-4","Lance Taylor",48,75],
    ["Air Force","MWC","4-8","Troy Calhoun",55,75],
    ["Boise State","MWC","9-5","Spencer Danielson",70,75],
    ["Colorado State","MWC","2-10","Jim Mora",40,70],
    ["Fresno State","MWC","8-4","Matt Entz",50,70],
    ["Hawaii","MWC","9-4","Timmy Chang",40,70],
    ["Nevada","MWC","3-9","Jeff Choate",35,60],
    ["New Mexico","MWC","9-4","Jason Eck",30,70],
    ["San Diego State","MWC","9-4","Sean Lewis",50,70],
    ["San Jose State","MWC","3-9","Ken Niumatalolo",35,65],
    ["UNLV","MWC","10-4","Dan Mullen",55,80],
    ["Utah State","MWC","6-7","Bronco Mendenhall",40,75],
    ["Wyoming","MWC","4-8","Jay Sawvel",35,60],
    ["Oregon State","Pac-12","2-10","JaMarcus Shephard",45,70],
    ["Washington State","Pac-12","7-6","Kirby Moore",55,70],
    ["Alabama","SEC","11-3","Kalen DeBoer",98,90],
    ["Arkansas","SEC","2-10","Ryan Silverfield",65,70],
    ["Auburn","SEC","5-7","Alex Golesh",78,80],
    ["Florida","SEC","4-8","Jon Sumrall",85,85],
    ["Georgia","SEC","12-1","Kirby Smart",100,100],
    ["Kentucky","SEC","5-7","Will Stein",60,75],
    ["LSU","SEC","7-6","Lane Kiffin",92,95],
    ["Mississippi State","SEC","5-7","Jeff Lebby",60,70],
    ["Missouri","SEC","8-5","Eli Drinkwitz",68,75],
    ["Oklahoma","SEC","10-3","Brent Venables",92,80],
    ["Ole Miss","SEC","11-1","Pete Golding",82,75],
    ["South Carolina","SEC","4-8","Shane Beamer",62,65],
    ["Tennessee","SEC","8-4","Josh Heupel",84,80],
    ["Texas","SEC","9-3","Steve Sarkisian",96,85],
    ["Texas A&M","SEC","11-2","Mike Elko",85,85],
    ["Vanderbilt","SEC","10-2","Clark Lea",58,90],
    ["Appalachian State","Sun Belt","5-7","Dowell Loggains",55,65],
    ["Arkansas State","Sun Belt","7-6","Butch Jones",35,65],
    ["Coastal Carolina","Sun Belt","6-6","Ryan Beard",45,65],
    ["Georgia Southern","Sun Belt","6-6","Clay Helton",40,65],
    ["Georgia State","Sun Belt","1-11","Dell McGee",20,50],
    ["James Madison","Sun Belt","12-2","Billy Napier",65,75],
    ["Louisiana","Sun Belt","6-7","Michael Desormeaux",45,65],
    ["Marshall","Sun Belt","5-7","Tony Gibson",40,65],
    ["Old Dominion","Sun Belt","9-3","Ricky Rahne",45,75],
    ["South Alabama","Sun Belt","4-8","Major Applewhite",35,60],
    ["Southern Miss","Sun Belt","7-6","Blake Anderson",35,70],
    ["Texas State","Sun Belt","6-6","GJ Kinne",35,70],
    ["Troy","Sun Belt","8-6","Gerad Parker",40,65],
    ["UL Monroe","Sun Belt","3-9","Bryant Vincent",15,55],
    ["Notre Dame","Independent","10-2","Marcus Freeman",94,90],
    ["UConn","Independent","9-4","Jason Candle",45,75]
]

def load_names():
    try:
        with open("firstnames.txt", "r") as f:
            first_names = [line.strip() for line in f.readlines()]
        with open("lastnames.txt", "r") as f:
            last_names = [line.strip() for line in f.readlines()]
        return first_names, last_names
    except FileNotFoundError:
        return ["Player"], ["Doe"]

class HighSchool:
    def __init__(self, name, region, state, prestige):
        self.name = name
        self.region = region
        self.state = state
        self.prestige = prestige
        self.roster = []
        self.schedule = []
        self.depth_chart = {}
        self.coach = None 
        
        self.wins = 0
        self.losses = 0
        self.ties = 0 
        self.points_for = 0
        self.points_against = 0
        
        # Awards / History
        self.conf_champ = False
        self.nat_champ = False
        self.bowl_win = False
        
        # --- DEBUG LOGGING ---
        self.roster_log = []
        self.logging_enabled = False # Default to OFF (False)
        
    def log_event(self, year, message):
        """Records a roster change event if logging is enabled."""
        if getattr(self, 'logging_enabled', False):
            self.roster_log.append(f"[Year {year}] {message}")

    @property
    def team_overall(self):
        if not self.roster: return 0
        return int(sum(p.overall for p in self.roster) / len(self.roster))

    def set_depth_chart(self):
        self.depth_chart = {}
        for pos, _ in POSITION_TEMPLATE:
            self.depth_chart[pos] = []
        for player in self.roster:
            if player.position in self.depth_chart:
                self.depth_chart[player.position].append(player)
        for pos in self.depth_chart:
            self.depth_chart[pos].sort(key=lambda x: x.overall, reverse=True)

    def record_str(self):
        return f"{self.wins}-{self.losses}"

    def __str__(self):
        return f"[{self.team_overall}] {self.name} ({self.record_str()})"

class College:
    def __init__(self, name, conference, prestige, prev_record):
        self.name = name
        self.conference = conference
        self.prestige = prestige
        self.prev_record = prev_record 
        
        self.roster = []
        self.schedule = []
        self.depth_chart = {}
        self.coach = None
        
        self.wins = 0
        self.losses = 0
        self.points_for = 0
        self.points_against = 0
        
        # Awards / History
        self.conf_champ = False
        self.nat_champ = False
        self.bowl_win = False

        # --- NEW HISTORY TRACKING ---
        self.playoff_appearances = 0
        self.national_championships = 0
        self.top_25_finishes = 0
        self.heisman_winners = [] # List of tuples: (Year, PlayerName)
        
        self.region = conference 

        # --- BUDGET & EXPECTATIONS ---
        self.budget = self._calculate_initial_budget()
        self.expectations = "Win 6 games" # Default string, updated annually

        # --- DEBUG LOGGING ---
        self.roster_log = []
        self.logging_enabled = False

    def _calculate_initial_budget(self):
        """Calculates budget based on prestige tiers."""
        if self.prestige >= 90: return random.randint(15_000_000, 20_000_000)
        elif self.prestige >= 80: return random.randint(10_000_000, 15_000_000)
        elif self.prestige >= 60: return random.randint(6_000_000, 10_000_000)
        elif self.prestige >= 40: return random.randint(3_000_000, 6_000_000)
        else: return random.randint(1_000_000, 3_000_000)

    def log_event(self, year, message):
        """Records a roster change event if logging is enabled."""
        if getattr(self, 'logging_enabled', False):
            self.roster_log.append(f"[Year {year}] {message}")

    @property
    def team_overall(self):
        if not self.roster: return 0
        return int(sum(p.overall for p in self.roster) / len(self.roster))

    def set_depth_chart(self):
        self.depth_chart = {}
        for pos, _ in POSITION_TEMPLATE:
            self.depth_chart[pos] = []
        for player in self.roster:
            if player.position in self.depth_chart:
                self.depth_chart[player.position].append(player)
        for pos in self.depth_chart:
            self.depth_chart[pos].sort(key=lambda x: x.overall, reverse=True)

    def record_str(self):
        return f"{self.wins}-{self.losses}"

    def __str__(self):
        return f"[{self.team_overall}] {self.name} ({self.record_str()})"

class Universe:
    def __init__(self):
        self.year = 2024
        self.current_week = 1
        
        self.high_school_league = [] 
        self.college_league = []     
        self.recruiting_pool = []    
        
        self.schedule = {}
        
        # --- NEW GLOBAL HISTORY ---
        self.heisman_history = []     # List of dicts: {year, player, team, stats}
        self.championship_history = [] # List of dicts: {year, champion, runner_up}

def generate_roster(first_names, last_names, school_prestige, base_age=14, context="HS"):
    roster = []
    for pos, count in POSITION_TEMPLATE:
        for _ in range(count):
            f_name = random.choice(first_names)
            l_name = random.choice(last_names)
            
            # 1=Fr, 2=So, 3=Jr, 4=Sr
            year = random.choices([1, 2, 3, 4], weights=[20, 25, 25, 30], k=1)[0]
            
            # Calculate Age
            start_age = base_age + year 
            
            new_player = Player(f_name, l_name, pos, year, school_prestige, age=start_age, context=context)
            
            # --- Calculate Stars for Seniors IMMEDIATELY ---
            if year == 4 and context == "HS":
                new_player.calculate_stars()
                
            roster.append(new_player)
    return roster

def generate_colleges():
    first_names, last_names = load_names()
    colleges = []
    
    print(f"Generating {len(COLLEGE_DB)} college teams...")
    
    for entry in COLLEGE_DB:
        # Entry: ["Name", "Conf", "Rec", "Coach Name", Prestige, CoachRating]
        name = entry[0]
        conf = entry[1]
        rec = entry[2]
        coach_name = entry[3]
        prestige = max(1, min(99, entry[4]))
        coach_rating = entry[5]
        
        new_college = College(name, conf, prestige, rec)
        
        # Placeholder roster for warmup sim
        new_college.roster = generate_roster(first_names, last_names, school_prestige=10, base_age=18, context="COLLEGE")
        
        new_college.set_depth_chart()
        
        # Generate Coach
        parts = coach_name.split(" ")
        c_first = parts[0]
        c_last = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        # --- COACH AGE & TENURE ---
        c_age = random.randint(32, 58)
        
        # --- SEED ALMA MATER ---
        # 30% chance the initial coach is an alumnus of a random school
        alma = None
        if random.random() < 0.3:
            random_entry = random.choice(COLLEGE_DB)
            alma = random_entry[0] # The name
            
        new_college.coach = Coach(c_first, c_last, rating=coach_rating, age=c_age, alma_mater=alma)
        new_college.coach.years_at_school = random.randint(0, 8) 
        
        # --- CONTRACT INITIALIZATION ---
        # Note: Budget is now on the School object.
        # Ensure salary fits within budget
        max_offer = new_college.budget * 0.9
        salary_req = 400_000 * coach_rating # Roughly matches skill
        if salary_req > max_offer: salary_req = max_offer 
        
        new_college.coach.salary = int(salary_req)
        new_college.coach.contract_years = random.randint(2, 5) 
        
        # Loyalty (Some coaches are lifers, some are mercenaries)
        # 30% Chance to be loyal "program builder"
        if random.random() < 0.3:
            new_college.coach.loyalty_rating = random.randint(7, 10)
        else:
            new_college.coach.loyalty_rating = random.randint(1, 6)
        
        colleges.append(new_college)
        
    return colleges

def run_warmup_simulation(universe):
    """
    Simulates a 9-Year Preload.
    Phase 1 (5 Years): HS Incubation (Players mature without being recruited).
    Phase 2 (4 Years): College Fill (Recruiting active).
    """
    from recruiting import process_signing_day
    
    print("\n" + "="*60)
    print("      INITIALIZING 9-YEAR WARMUP SIMULATION")
    print("      Phase 1: High School Incubation (5 Years)")
    print("      Phase 2: College Recruitment Fill (4 Years)")
    print("="*60)
    
    first_names, last_names = load_names()
    
    # --- PHASE 1: HS INCUBATION (5 Years) ---
    for i in range(5):
        print(f" [Phase 1 - Year {i+1}/5] Simulating {universe.year} (HS Only)...")
        
        # Track HS Graduates stats for logging
        grad_stats = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        total_grads = 0

        for school in universe.high_school_league:
            # Identify Graduates (Year 4s)
            graduating = [p for p in school.roster if p.eligibility_year == 4]
            
            for p in graduating:
                p.calculate_stars() # Ensure stars are calc'd
                if p.stars in grad_stats:
                    grad_stats[p.stars] += 1
                total_grads += 1
            
            # Remove graduates (Retire)
            school.roster = [p for p in school.roster if p.eligibility_year < 4]
            
            # Age & Train Underclassmen
            for p in school.roster:
                p.eligibility_year += 1
                p.age += 1
                p.train(school.coach)
                if p.eligibility_year == 4:
                    p.calculate_stars()
            
            # Refill
            pos_counts = {p.position: 0 for p in school.roster}
            for p in school.roster: pos_counts[p.position] += 1
            for pos, target in POSITION_TEMPLATE:
                needed = target - pos_counts.get(pos, 0)
                if needed > 0:
                    for _ in range(needed):
                        f_name = random.choice(first_names)
                        l_name = random.choice(last_names)
                        new_p = Player(f_name, l_name, pos, 1, school.prestige, age=14, context="HS")
                        school.roster.append(new_p)
            school.set_depth_chart()

        # College Attrition (Flush placeholders)
        for school in universe.college_league:
            school.roster = [p for p in school.roster if p.eligibility_year < 4]
            for p in school.roster:
                p.eligibility_year += 1
                p.age += 1
                p.train(school.coach)
            
            # Refill with walk-ons to maintain structure
            pos_counts = {p.position: 0 for p in school.roster}
            for p in school.roster: pos_counts[p.position] += 1
            for pos, target in POSITION_TEMPLATE:
                needed = target - pos_counts.get(pos, 0)
                if needed > 0:
                    for _ in range(needed):
                        f_name = random.choice(first_names)
                        l_name = random.choice(last_names)
                        walk_on = Player(f_name, l_name, pos, 1, 1, age=18, context="COLLEGE")
                        school.roster.append(walk_on)
            school.set_depth_chart()

        print(f"   > HS Graduates: {total_grads} (Unrecruited)")
        print(f"   > Breakdown: 5★:{grad_stats[5]} | 4★:{grad_stats[4]} | 3★:{grad_stats[3]} | 2★:{grad_stats[2]} | 1★:{grad_stats[1]}")
        universe.year += 1

    # --- PHASE 2: RECRUITING (4 Years) ---
    for i in range(4):
        print(f" [Phase 2 - Year {i+1}/4] Simulating {universe.year} (Recruiting Active)...")
        
        # 1. Recruiting
        rankings = process_signing_day(universe, silent=True)
        
        # Log Stats
        star_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        total_recruits = 0
        for data in rankings.values():
            for p in data['commits']:
                if p.stars in star_counts:
                    star_counts[p.stars] += 1
                total_recruits += 1
        
        print(f"   > Recruiting Class: {total_recruits} signees")
        print(f"   > Breakdown: 5★:{star_counts[5]} | 4★:{star_counts[4]} | 3★:{star_counts[3]} | 2★:{star_counts[2]} | 1★:{star_counts[1]}")

        # Add to colleges
        for school, data in rankings.items():
            if school in rankings:
                school.roster.extend(data['commits'])

        # 2. HS Progression
        for school in universe.high_school_league:
            school.roster = [p for p in school.roster if p.context != "COLLEGE"] # Remove signed
            school.roster = [p for p in school.roster if p.eligibility_year < 4] # Remove unsigned seniors
            
            for p in school.roster:
                p.eligibility_year += 1
                p.age += 1
                p.train(school.coach)
                if p.eligibility_year == 4:
                    p.calculate_stars()
            
            pos_counts = {p.position: 0 for p in school.roster}
            for p in school.roster: pos_counts[p.position] += 1
            for pos, target in POSITION_TEMPLATE:
                needed = target - pos_counts.get(pos, 0)
                if needed > 0:
                    for _ in range(needed):
                        f_name = random.choice(first_names)
                        l_name = random.choice(last_names)
                        new_p = Player(f_name, l_name, pos, 1, school.prestige, age=14, context="HS")
                        school.roster.append(new_p)
            school.set_depth_chart()

        # 3. College Progression
        for school in universe.college_league:
            school.roster = [p for p in school.roster if p.eligibility_year < 4]
            for p in school.roster:
                p.eligibility_year += 1
                p.age += 1
                p.train(school.coach)
                p.calculate_stars()
            
            # Refill with walk-ons to maintain structure
            pos_counts = {p.position: 0 for p in school.roster}
            for p in school.roster: pos_counts[p.position] += 1
            for pos, target in POSITION_TEMPLATE:
                needed = target - pos_counts.get(pos, 0)
                if needed > 0:
                    for _ in range(needed):
                        f_name = random.choice(first_names)
                        l_name = random.choice(last_names)
                        walk_on = Player(f_name, l_name, pos, 1, 1, age=18, context="COLLEGE")
                        school.roster.append(walk_on)
            school.set_depth_chart()
        
        universe.year += 1
    
    print(" [Warmup Complete] Roster generation finished.\n")

def generate_world(target_count=300):
    first_names, last_names = load_names()
    generated_schools = []
    possible_names = []

    # --- HS GENERATION ---
    for region_name, states in REGIONS.items():
        for state in states:
            for suffix in DIRECTIONS + TYPES:
                possible_names.append({'name': f"{state} {suffix}", 'region': region_name, 'state': state})
            for prefix in DIRECTIONS:
                possible_names.append({'name': f"{prefix} {state}", 'region': region_name, 'state': state})

    random.shuffle(possible_names)
    selection = possible_names[:min(target_count, len(possible_names))]

    print(f"Generating rosters and coaches for {len(selection)} high schools...")
    
    # --- UPDATED PRESTIGE DISTRIBUTION ---
    prestige_weights = [20, 20, 15, 15, 10, 8, 6, 3, 2, 1] 
    
    for data in selection:
        prestige = random.choices([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], weights=prestige_weights, k=1)[0]
        new_school = HighSchool(data['name'], data['region'], data['state'], prestige)
        
        # Generate Roster (Base age 14, HS context)
        new_school.roster = generate_roster(first_names, last_names, prestige, base_age=14, context="HS")
        new_school.set_depth_chart() 
        
        # Generate Coach
        c_first = random.choice(first_names)
        c_last = random.choice(last_names)
        # --- HS COACH AGE ---
        c_age = random.randint(25, 60)
        new_school.coach = Coach(c_first, c_last, age=c_age)
        
        generated_schools.append(new_school)

    generated_schools.sort(key=lambda x: (x.region, -x.team_overall, x.name))
    
    # --- COLLEGE GENERATION ---
    colleges = generate_colleges()
    
    # Create the Universe Container
    universe = Universe()
    universe.high_school_league = generated_schools
    universe.college_league = colleges
    universe.schedule = {}
    
    # Start in 2015 so we end up in 2024 after 9 loops (5+4)
    universe.year = 2015 
    
    # --- RUN WARMUP ---
    run_warmup_simulation(universe)

    # --- RESET COACH HISTORY FOR GAME START ---
    # Resets all college coaches so the "First Watchable Year" is their Year 0/1.
    print("Resetting coach records for start of play...")
    for school in universe.college_league:
        if school.coach:
            school.coach.years_at_school = 0
            school.coach.history = []
            school.coach.career_wins = 0
            school.coach.career_losses = 0
            school.coach.championships = 0 
    
    # Final Setup for Game Start
    print("Generating Season Schedule...")
    universe.schedule = generate_schedule(universe.high_school_league)
    universe.current_week = 1
    
    return universe