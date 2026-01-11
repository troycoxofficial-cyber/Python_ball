import random
from game_sim import GameSim
from player import Player
from coach import Coach
from tactics import OFF_PLAYS, DEF_STRATEGIES

# --- MOCK CLASSES TO ISOLATE THE MATH ---
class MockTeam:
    def __init__(self, name, off_rating, def_rating):
        self.name = name
        self.coach = Coach("Test", "Coach")
        self.coach.run_pass_bias = 5
        self.coach.aggressiveness = 5
        
        # Create a dummy depth chart with specific ratings
        self.depth_chart = {}
        positions = ["QB", "RB", "WR", "TE", "OL", "DL", "LB", "DB", "K", "P"]
        
        for pos in positions:
            self.depth_chart[pos] = []
            for _ in range(5):
                p = Player("Test", "Player", pos, 1, 1)
                # FORCE ATTRIBUTES based on rating
                rating_val = off_rating if pos in ["QB", "RB", "WR", "TE", "OL"] else def_rating
                for attr in p.attributes:
                    p.attributes[attr] = rating_val
                p.overall = p.calculate_overall()
                self.depth_chart[pos].append(p)

class MockGame:
    def __init__(self):
        self.home_team = MockTeam("Home", 75, 75) 
        self.away_team = MockTeam("Away", 75, 75)
        self.export_log = False
        self.week = 1

def run_tuning_test(sim_count=1000, off_rating=75, def_rating=75):
    print(f"\n--- RUNNING SIMULATION: Offense {off_rating} OVR vs Defense {def_rating} OVR ---")
    
    # Setup
    game = MockGame()
    game.home_team = MockTeam("Defense", 75, def_rating)
    game.away_team = MockTeam("Offense", off_rating, 75)
    
    sim = GameSim(game)
    sim.offense = game.away_team
    sim.defense = game.home_team
    
    results = {
        "runs": 0, "run_yds": 0, "breakaways": 0, "stuffed": 0,
        "passes": 0, "completions": 0, "pass_yds": 0, "sacks": 0, "ints": 0,
        "scrambles": 0
    }
    
    print(f"Simulating {sim_count} plays...")
    
    # Lists for random selection
    run_plays = [k for k,v in OFF_PLAYS.items() if v["type"] == "RUN"]
    pass_plays = [k for k,v in OFF_PLAYS.items() if v["type"] == "PASS"]
    def_plays = list(DEF_STRATEGIES.keys())

    for _ in range(sim_count):
        # Alternate run/pass
        if random.random() < 0.5:
            # RUN TEST
            off_key = random.choice(run_plays) 
            def_key = random.choice(def_plays)
            desc, score, time = sim.resolve_play(off_key, def_key, "NORMAL")
            
            results["runs"] += 1
            if "SACK" in desc or "Pressure" in desc:
                pass 
            else:
                try:
                    words = desc.split()
                    for i, w in enumerate(words):
                        if "yds" in w or "yds." in w:
                            yds = int(words[i-1])
                            results["run_yds"] += yds
                            if yds <= 0: results["stuffed"] += 1
                            if yds >= 20: results["breakaways"] += 1
                            break
                except: pass

        else:
            # PASS TEST
            off_key = random.choice(pass_plays)
            def_key = random.choice(def_plays)
            desc, score, time = sim.resolve_play(off_key, def_key, "NORMAL")
            
            if "SACK" in desc:
                results["sacks"] += 1
                results["passes"] += 1 
            elif "Pressure" in desc and "scrambles" in desc:
                results["scrambles"] += 1
                results["runs"] += 1 
                try:
                    words = desc.split()
                    for i, w in enumerate(words):
                        if "yds" in w:
                            yds = int(words[i-1])
                            results["run_yds"] += yds
                except: pass
            elif "Pressure" in desc and "Throws it away" in desc:
                results["passes"] += 1
            elif "INTERCEPTED" in desc:
                results["ints"] += 1
                results["passes"] += 1
            elif "Incomplete" in desc:
                results["passes"] += 1
            else:
                results["passes"] += 1
                results["completions"] += 1
                try:
                    words = desc.split()
                    for i, w in enumerate(words):
                        if "yds" in w:
                            yds = int(words[i-1])
                            results["pass_yds"] += yds
                except: pass

    # REPORT
    if results["runs"] > 0:
        ypc = results["run_yds"] / results["runs"]
        print(f"RUSHING: {results['runs']} att, {results['run_yds']} yds, {ypc:.2f} avg")
        print(f"   Breakaways (>20y): {results['breakaways']} ({(results['breakaways']/results['runs'])*100:.1f}%)")
        print(f"   Stuffed (<=0y)   : {results['stuffed']} ({(results['stuffed']/results['runs'])*100:.1f}%)")
        print(f"   (Includes {results['scrambles']} QB Scrambles)")

    if results["passes"] > 0:
        cmp_pct = (results['completions'] / results['passes']) * 100
        yPa = results['pass_yds'] / results['passes']
        sack_pct = (results['sacks'] / results['passes']) * 100
        int_pct = (results['ints'] / results['passes']) * 100
        print(f"PASSING: {results['passes']} att, {results['completions']} cmp, {results['pass_yds']} yds")
        print(f"   Comp %  : {cmp_pct:.1f}%  (Target: 58-65%)")
        print(f"   Yards/Att: {yPa:.1f}   (Target: 6.5-8.0)")
        print(f"   Sack %  : {sack_pct:.1f}%  (Target: 5-8%)")
        print(f"   Int %   : {int_pct:.1f}%  (Target: 2-3%)")

if __name__ == "__main__":
    run_tuning_test(1000, 75, 75)