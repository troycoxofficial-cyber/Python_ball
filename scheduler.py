import random
from player import Player
from coach import Coach
from rankings import calculate_rpi  # Required for Seeding

# --- HELPER: FCS TEAM GENERATOR ---
class FCSTeam:
    """A dummy team object to fulfill scheduling requirements."""
    def __init__(self, name_suffix, week):
        self.name = f"FCS {name_suffix}"
        self.region = "FCS"
        self.conference = "FCS"
        self.prestige = 20
        self.wins = 0
        self.losses = 0
        self.points_for = 0
        self.points_against = 0
        self.schedule = []
        self.played = False
        
        # Minimal Coach
        self.coach = Coach("FCS", "Coach", rating=30)
        
        # Generate minimal roster for GameSim
        self.roster = []
        self.depth_chart = {}
        positions = [("QB", 2), ("RB", 3), ("WR", 4), ("TE", 2), 
                     ("OL", 6), ("DL", 5), ("LB", 5), ("DB", 5), ("K", 1), ("P", 1)]
        
        for pos, count in positions:
            self.depth_chart[pos] = []
            for i in range(count):
                # Generic low-stat players
                p = Player("FCS", f"{pos}-{i+1}", pos, 3, 10, age=20)
                p.overall = 60 # Flat rating
                # Override attributes to be mediocre
                for k in p.attributes: p.attributes[k] = 60
                self.roster.append(p)
                self.depth_chart[pos].append(p)

    def record_str(self):
        return "0-0"

    def __str__(self):
        return self.name

class Game:
    def __init__(self, home_team, away_team, week, title=""):
        self.home_team = home_team
        self.away_team = away_team
        self.week = week
        
        # Game State attributes
        self.played = False
        self.home_score = 0
        self.away_score = 0
        self.game_log = [] 
        self.title = title 
        
        self.export_log = False 

    @property
    def winner(self):
        if not self.played: return None
        return self.home_team if self.home_score > self.away_score else self.away_team

    def __str__(self):
        label = f" [{self.title}]" if self.title else ""
        return f"W{self.week}{label}: {self.away_team.name} @ {self.home_team.name}"

def generate_schedule(schools):
    """
    Main entry point. Detects if we are scheduling High School (Regions) 
    or College (Conferences) and applies the appropriate logic.
    """
    # Detect mode based on first school attributes
    is_college = hasattr(schools[0], 'conference')
    
    if is_college:
        return generate_college_schedule_strict(schools)
    else:
        return generate_hs_schedule(schools)

def generate_hs_schedule(schools):
    """Standard Regional scheduling for High School."""
    schedule = {i: [] for i in range(1, 13)}
    regions = {}
    for school in schools:
        # Reset data
        school.schedule = []
        school.wins = 0; school.losses = 0
        school.points_for = 0; school.points_against = 0
        
        if school.region not in regions: regions[school.region] = []
        regions[school.region].append(school)

    for region_name, team_list in regions.items():
        print(f"Scheduling HS Region: {region_name}...")
        for week in range(1, 13):
            weekly_pool = team_list[:]
            random.shuffle(weekly_pool)
            while len(weekly_pool) >= 2:
                home = weekly_pool.pop()
                away = weekly_pool.pop()
                new_game = Game(home, away, week)
                schedule[week].append(new_game)
                home.schedule.append(new_game)
                away.schedule.append(new_game)
    return schedule

def generate_college_schedule_strict(schools):
    """
    Improved Strict Scheduling for College:
    1. 8 Conference Games (Unique opponents)
    2. 4 Non-Conference Games (Unique opponents)
    3. Fallback to FCS if Non-Conf not found.
    """
    print("\n--- GENERATING COLLEGE SCHEDULE (Strict 8 Conf / 4 Non-Conf) ---")
    schedule = {i: [] for i in range(1, 13)}
    
    # 1. Reset Teams & Group by Conference
    conferences = {}
    for s in schools:
        s.schedule = [] # Clear old schedule
        s.wins = 0; s.losses = 0
        s.points_for = 0; s.points_against = 0
        
        if s.conference not in conferences: conferences[s.conference] = []
        conferences[s.conference].append(s)

    # 2. Pre-Calculate Conference Matchups (The "8 Games" Matrix)
    conf_matchups = [] # List of (TeamA, TeamB)
    
    for conf_name, teams in conferences.items():
        num_teams = len(teams)
        target_games = min(8, num_teams - 1)
        
        if target_games < 8:
            print(f" [Warning] {conf_name} only has {num_teams} teams. Scheduling {target_games} conf games.")

        valid_graph = False
        attempts = 0
        
        while not valid_graph and attempts < 20:
            attempts += 1
            current_edges = []
            degrees = {t: 0 for t in teams}
            possible_pairs = []
            
            for i in range(num_teams):
                for j in range(i + 1, num_teams):
                    possible_pairs.append((teams[i], teams[j]))
            random.shuffle(possible_pairs)
            
            for t1, t2 in possible_pairs:
                if degrees[t1] < target_games and degrees[t2] < target_games:
                    current_edges.append((t1, t2))
                    degrees[t1] += 1
                    degrees[t2] += 1
            
            if all(d == target_games for d in degrees.values()):
                valid_graph = True
                conf_matchups.extend(current_edges)
            
        if not valid_graph:
            print(f" [Error] Could not generate perfect schedule for {conf_name}. Using best effort.")
            conf_matchups.extend(current_edges)

    # 3. Schedule Weeks 1-12
    pending_conf_games = {s: [] for s in schools}
    for t1, t2 in conf_matchups:
        pending_conf_games[t1].append(t2)
        pending_conf_games[t2].append(t1)

    all_teams = schools[:]
    
    for week in range(1, 13):
        week_pool = all_teams[:]
        random.shuffle(week_pool)
        week_matches = []
        scheduled_this_week = set()

        # --- PRIORITY 1: SCHEDULE CONFERENCE GAMES ---
        week_pool.sort(key=lambda t: len(pending_conf_games[t]), reverse=True)
        
        for team in week_pool:
            if team in scheduled_this_week: continue
            
            found_conf = False
            for opp in pending_conf_games[team]:
                if opp not in scheduled_this_week:
                    week_matches.append((team, opp, "Conf"))
                    scheduled_this_week.add(team)
                    scheduled_this_week.add(opp)
                    pending_conf_games[team].remove(opp)
                    pending_conf_games[opp].remove(team)
                    found_conf = True
                    break
            
            if found_conf: continue

        # --- PRIORITY 2: SCHEDULE NON-CONFERENCE GAMES ---
        remaining = [t for t in week_pool if t not in scheduled_this_week]
        random.shuffle(remaining)
        
        while len(remaining) > 0:
            t1 = remaining.pop(0)
            if t1 in scheduled_this_week: continue
            
            found_non_conf = False
            for i, t2 in enumerate(remaining):
                already_played = any(g.home_team == t2 or g.away_team == t2 for g in t1.schedule)
                if t1.conference != t2.conference and not already_played:
                    week_matches.append((t1, t2, "Non-Conf"))
                    scheduled_this_week.add(t1)
                    scheduled_this_week.add(t2)
                    remaining.pop(i)
                    found_non_conf = True
                    break
            
            if not found_non_conf:
                fcs_opp = FCSTeam(f"State {random.randint(1,99)}", week)
                week_matches.append((t1, fcs_opp, "FCS"))
                scheduled_this_week.add(t1)

        # --- FINALIZE WEEK ---
        for home, away, g_type in week_matches:
            title = ""
            if g_type == "Conf": title = "Conference Play"
            elif g_type == "FCS": title = "Non-Conference (FCS)"
            else: title = "Non-Conference"
            
            g = Game(home, away, week, title)
            schedule[week].append(g)
            home.schedule.append(g)
            if hasattr(away, 'schedule'):
                away.schedule.append(g)

    return schedule

# --- HS PLAYOFF LOGIC ---

def generate_playoffs_round_of_16(schools, week=13):
    """Seeds the top 16 teams (4 per region) into the bracket."""
    playoff_games = []
    regions = {}
    for school in schools:
        if school.region not in regions: regions[school.region] = []
        regions[school.region].append(school)
        
    print("\n--- SEEDING ROUND OF 16 ---")
    for r_name, teams in regions.items():
        ranked = sorted(teams, key=lambda s: (-s.wins, -(s.points_for - s.points_against), -s.points_for))
        top_seeds = ranked[:4]
        if len(top_seeds) < 4: 
            print(f"Not enough teams in {r_name}"); continue
            
        g1 = Game(top_seeds[0], top_seeds[3], week, title=f"{r_name} Semifinal")
        g2 = Game(top_seeds[1], top_seeds[2], week, title=f"{r_name} Semifinal")
        
        playoff_games.extend([g1, g2])
        for g in [g1, g2]:
            g.home_team.schedule.append(g); g.away_team.schedule.append(g)
            
    return playoff_games

def generate_next_playoff_round(schedule, previous_week):
    prev_games = schedule.get(previous_week, [])
    if not prev_games: return []
    
    next_week = previous_week + 1
    new_games = []
    print(f"Generating matchups for Week {next_week}...")

    if next_week == 14:
        region_winners = {}
        for g in prev_games:
            w = g.winner
            if not w: 
                print(f"Error: Game {g} not decided yet."); return []
            
            r_name = g.title.replace(" Semifinal", "")
            if r_name not in region_winners: region_winners[r_name] = []
            region_winners[r_name].append(w)
            
        for r_name, winners in region_winners.items():
            if len(winners) == 2:
                w1, w2 = winners[0], winners[1]
                home = w1 if w1.wins >= w2.wins else w2
                away = w2 if w1 == home else w1
                ng = Game(home, away, next_week, title=f"{r_name} Final")
                new_games.append(ng)

    elif next_week == 15:
        winners_by_region = {}
        for g in prev_games:
            w = g.winner
            r_name = g.title.replace(" Final", "")
            winners_by_region[r_name] = w
            
        if "NORTH" in winners_by_region and "SOUTH" in winners_by_region:
            n = winners_by_region["NORTH"]; s = winners_by_region["SOUTH"]
            home = n if n.wins >= s.wins else s
            away = s if n == home else n
            new_games.append(Game(home, away, next_week, title="State Semifinal (N/S)"))
            
        if "WEST" in winners_by_region and "MIDWEST" in winners_by_region:
            w = winners_by_region["WEST"]; mw = winners_by_region["MIDWEST"]
            home = w if w.wins >= mw.wins else mw
            away = mw if w == home else w
            new_games.append(Game(home, away, next_week, title="State Semifinal (W/MW)"))

    elif next_week == 16:
        finalists = [g.winner for g in prev_games if g.winner]
        if len(finalists) == 2:
            f1, f2 = finalists[0], finalists[1]
            ng = Game(f1, f2, next_week, title="STATE CHAMPIONSHIP")
            new_games.append(ng)

    for g in new_games:
        g.home_team.schedule.append(g)
        g.away_team.schedule.append(g)
        
    return new_games

# --- COLLEGE PLAYOFF LOGIC (NEW) ---

def generate_cfp_round1(schools, week=14):
    """
    Selects top 12 teams.
    Seeds 1-4: Bye (Returned separately).
    Seeds 5-12: Play Round 1 in Week 14.
    """
    # Use Rankings Logic
    sorted_teams = sorted(schools, key=calculate_rpi, reverse=True)
    top_12 = sorted_teams[:12]
    
    seeds = top_12[:4] # 1, 2, 3, 4 (Byes)
    rest = top_12[4:]  # 5..12
    
    # 5 vs 12 (Index 0 vs 7)
    # 6 vs 11 (Index 1 vs 6)
    # 7 vs 10 (Index 2 vs 5)
    # 8 vs 9  (Index 3 vs 4)
    
    games = []
    games.append(Game(rest[0], rest[7], week, title="CFP Round 1 (5v12)"))
    games.append(Game(rest[1], rest[6], week, title="CFP Round 1 (6v11)"))
    games.append(Game(rest[2], rest[5], week, title="CFP Round 1 (7v10)"))
    games.append(Game(rest[3], rest[4], week, title="CFP Round 1 (8v9)"))
    
    for g in games:
        g.home_team.schedule.append(g)
        g.away_team.schedule.append(g)
        
    return games, seeds

def generate_cfp_qf(schedule, seeds, week=15):
    """
    Generates Quarterfinals (Week 15).
    Seeds 1-4 vs Winners of Round 1.
    """
    prev_games = schedule.get(week-1, [])
    winners = {} 
    for g in prev_games:
        if "CFP Round 1" in g.title and g.winner:
            if "8v9" in g.title: winners["8v9"] = g.winner
            if "5v12" in g.title: winners["5v12"] = g.winner
            if "7v10" in g.title: winners["7v10"] = g.winner
            if "6v11" in g.title: winners["6v11"] = g.winner
            
    games = []
    # 1 vs 8/9
    if "8v9" in winners:
        games.append(Game(seeds[0], winners["8v9"], week, title="CFP QF (1 vs 8/9)"))
    # 4 vs 5/12
    if "5v12" in winners:
        games.append(Game(seeds[3], winners["5v12"], week, title="CFP QF (4 vs 5/12)"))
    # 2 vs 7/10
    if "7v10" in winners:
        games.append(Game(seeds[1], winners["7v10"], week, title="CFP QF (2 vs 7/10)"))
    # 3 vs 6/11
    if "6v11" in winners:
        games.append(Game(seeds[2], winners["6v11"], week, title="CFP QF (3 vs 6/11)"))
        
    for g in games:
        g.home_team.schedule.append(g)
        g.away_team.schedule.append(g)
        
    return games

def generate_cfp_semis(schedule, week=16):
    """Generates Semifinals (Week 16)."""
    prev_games = schedule.get(week-1, [])
    winners = {}
    for g in prev_games:
        if "CFP QF" in g.title and g.winner:
            if "1 vs" in g.title: winners["Q1"] = g.winner
            if "4 vs" in g.title: winners["Q4"] = g.winner
            if "2 vs" in g.title: winners["Q2"] = g.winner
            if "3 vs" in g.title: winners["Q3"] = g.winner
            
    games = []
    # Semis: 1/8/9 winner vs 4/5/12 winner
    if "Q1" in winners and "Q4" in winners:
        games.append(Game(winners["Q1"], winners["Q4"], week, title="CFP Semifinal A"))
    # Semis: 2/7/10 winner vs 3/6/11 winner
    if "Q2" in winners and "Q3" in winners:
        games.append(Game(winners["Q2"], winners["Q3"], week, title="CFP Semifinal B"))

    for g in games:
        g.home_team.schedule.append(g)
        g.away_team.schedule.append(g)
        
    return games

def generate_cfp_final(schedule, week=16):
    """
    Generates Final (Also Week 16).
    Checks the current week's schedule (Semis) to find winners.
    """
    current_games = schedule.get(week, [])
    finalists = []
    for g in current_games:
        if "CFP Semifinal" in g.title and g.winner:
            finalists.append(g.winner)
            
    if len(finalists) == 2:
        g = Game(finalists[0], finalists[1], week, title="CFP NATIONAL CHAMPIONSHIP")
        g.home_team.schedule.append(g)
        g.away_team.schedule.append(g)
        return [g]
    return []

# --- CONF CHAMPIONSHIPS ---

def generate_conference_championships(schools, week=13):
    """Schedules #1 vs #2 for each conference in Week 13."""
    from rankings import calculate_rpi
    
    print(f"\n--- SCHEDULING COLLEGE CONFERENCE CHAMPIONSHIPS (Week {week}) ---")
    new_games = []
    
    sorted_schools = sorted(schools, key=calculate_rpi, reverse=True)
    rank_map = {team: i+1 for i, team in enumerate(sorted_schools)}
    
    conferences = {}
    for s in schools:
        if s.conference == "Independent": continue
        if s.conference not in conferences: conferences[s.conference] = []
        conferences[s.conference].append(s)
        
    for conf_name, teams in conferences.items():
        if len(teams) < 2: continue
        for t in teams:
            t._temp_conf_wins = 0
            for g in t.schedule:
                if g.played and g.winner == t and g.title == "Conference Play":
                    t._temp_conf_wins += 1
        
        ranked_in_conf = sorted(teams, key=lambda x: (x._temp_conf_wins, x.wins, x.points_for - x.points_against), reverse=True)
        t1, t2 = ranked_in_conf[0], ranked_in_conf[1]
        r1, r2 = rank_map.get(t1, 99), rank_map.get(t2, 99)
        
        print(f" -> {conf_name}: (#{r1}) {t1.name} vs (#{r2}) {t2.name}")
        g = Game(t1, t2, week, title=f"{conf_name} Championship")
        new_games.append(g)
        t1.schedule.append(g); t2.schedule.append(g)
        
        for t in teams:
            if hasattr(t, '_temp_conf_wins'): del t._temp_conf_wins
            
    return new_games