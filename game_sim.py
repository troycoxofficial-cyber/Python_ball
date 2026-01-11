import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from rich.align import Align

from tactics import OFF_PLAYS, DEF_STRATEGIES

# --- INJURY DATA ---
INJURIES_MINOR = [("Bruised Ribs", 1, 1), ("Hip Pointer", 1, 2), ("Stinger", 1, 1), ("Sprained Wrist", 1, 2), ("Bruised Knee", 1, 2), ("Turf Toe", 1, 3), ("Lower Back Strain", 1, 2)]
INJURIES_MODERATE = [("Sprained Ankle", 2, 3), ("Hamstring Strain", 2, 4), ("Groin Strain", 2, 4), ("Concussion", 1, 3), ("Calf Strain", 2, 5), ("Shoulder Subluxation", 3, 5), ("Elbow Sprain", 2, 4), ("Broken Finger", 3, 6), ("Deep Thigh Bruise", 2, 3)]
INJURIES_SERIOUS = [("High Ankle Sprain", 5, 8), ("MCL Sprain", 5, 8), ("Meniscus Tear", 4, 9), ("Broken Hand", 5, 8), ("Sports Hernia", 6, 9), ("Broken Collarbone", 7, 10), ("Broken Ribs", 4, 7)]
INJURIES_SEVERE = [("Broken Arm", 9, 14), ("Broken Leg", 12, 18), ("Torn Pectoral", 11, 16), ("Torn Triceps", 11, 16), ("Lisfranc Injury", 10, 16), ("Torn ACL", 14, 20), ("Achilles Tear", 14, 20), ("Patellar Tendon Tear", 14, 20), ("Vertebrae Fracture", 15, 25)]

class GameSim:
    def __init__(self, game, console=None):
        self.game = game
        # Use provided console or create a new one to ensure Rich works everywhere
        self.console = console if console else Console()
        
        self.home = game.home_team
        self.away = game.away_team
        self.offense = self.away 
        self.defense = self.home
        self.quarter = 1
        self.time_remaining = 900 
        self.down = 1
        self.distance = 10
        self.ball_on = 25 
        self.log = []
        self.is_overtime = False
        self.ot_period = 0  # Track OT period for new rules
        self.stats = {
            self.home: {"score": 0, "yards": 0, "pass": 0, "rush": 0, "to": 0},
            self.away: {"score": 0, "yards": 0, "pass": 0, "rush": 0, "to": 0}
        }

    def get_clock_str(self):
        if self.is_overtime: return f"[yellow]OT{self.ot_period}[/yellow]" if self.ot_period > 0 else "[yellow]OT[/yellow]"
        mins = int(self.time_remaining // 60)
        secs = int(self.time_remaining % 60)
        return f"{mins:02d}:{secs:02d}"

    def get_field_pos_str(self):
        pos = max(1, min(99, int(self.ball_on)))
        if pos > 50: return f"opp {100 - pos}"
        return f"own {pos}"

    def switch_possession(self, kickoff=False, ot_reset=False, turnover=False):
        self.offense, self.defense = self.defense, self.offense
        self.down = 1
        self.distance = 10
        
        if turnover and not kickoff and not ot_reset:
            # Ball spot flips on turnover (e.g., Int at 40 goes to Own 60)
            self.ball_on = 100 - self.ball_on
        elif self.is_overtime or ot_reset: 
            # OT Reset handled in play_overtime mostly, but default here
            self.ball_on = 75 
        elif kickoff: 
            self.ball_on = 25
        else: 
            self.ball_on = 100 - self.ball_on

    def check_time_management(self):
        # Coach Trait: Clock Manager
        coach = self.offense.coach
        hurry_threshold = 300
        chew_threshold = 240
        
        if "Clock Manager" in coach.traits:
            hurry_threshold = 420 
            chew_threshold = 360  
        
        if self.quarter < 4: return "NORMAL"
        score_diff = self.stats[self.offense]["score"] - self.stats[self.defense]["score"]
        
        if score_diff < 0 and self.time_remaining < hurry_threshold: return "HURRY"
        if score_diff > 0 and self.time_remaining < chew_threshold: return "CHEW"
        return "NORMAL"

    def draw_live_ui(self, last_play_desc):
        self.console.clear()
        
        h_score = self.stats[self.home]["score"]
        a_score = self.stats[self.away]["score"]
        
        # Color the leading score
        h_style = "bold green" if h_score > a_score else ("bold red" if h_score < a_score else "bold white")
        a_style = "bold green" if a_score > h_score else ("bold red" if a_score < h_score else "bold white")
        
        # Possession indicators
        p_h = "[yellow]◄ BALL[/yellow]" if self.offense == self.home else "      "
        p_a = "[yellow]BALL ►[/yellow]" if self.offense == self.away else "      "
        
        # --- SCOREBOARD ---
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        grid.add_row(
            f"[bold]{self.away.name.upper()}[/bold] ({self.away.record_str()})",
            "vs",
            f"[bold]{self.home.name.upper()}[/bold] ({self.home.record_str()})"
        )
        grid.add_row(
            f"{p_a} [{a_style}]{a_score}[/{a_style}]",
            "",
            f"[{h_style}]{h_score}[/{h_style}] {p_h}"
        )
        
        scoreboard = Panel(grid, style="cyan", box=box.ROUNDED)
        self.console.print(scoreboard)
        
        # --- GAME STATUS ---
        q_str = f"[yellow]OT{self.ot_period}[/yellow]" if self.is_overtime else f"Q{self.quarter}"
        clock = self.get_clock_str()
        mode = self.check_time_management()
        mode_str = f"[red]HURRY[/red]" if mode == "HURRY" else (f"[green]CHEW[/green]" if mode == "CHEW" else "NORMAL")
        
        status_table = Table(box=box.SIMPLE, show_header=False, expand=True)
        status_table.add_column("Clock", justify="left")
        status_table.add_column("Down", justify="center")
        status_table.add_column("Mode", justify="right")
        
        status_table.add_row(
            f"{q_str} | {clock}",
            f"{self.down} & {int(self.distance)} | {self.get_field_pos_str()}",
            f"Mode: {mode_str}"
        )
        self.console.print(status_table)

        # --- FIELD VISUALIZATION ---
        field_chars = [f"[green].[/green]"] * 100
        for i in range(10, 100, 10): field_chars[i] = f"[white]|[/white]"
        
        # Target Line
        target_idx = int(self.ball_on + self.distance)
        if 0 <= target_idx < 100: field_chars[target_idx] = f"[yellow]I[/yellow]"
        
        # Ball Position
        b_idx = max(0, min(99, int(self.ball_on)))
        field_chars[b_idx] = f"[bold yellow]O[/bold yellow]"
        
        field_str = "".join(field_chars)
        self.console.print(Panel(Align.center(f"[red]END[/red] {field_str} [red]END[/red]"), box=box.HEAVY))
        
        # --- LAST PLAY ---
        self.console.print(Panel(f"[bold]{last_play_desc}[/bold]", title="LAST PLAY", border_style="cyan"))

    def get_active_player(self, team, position, count=1):
        candidates = team.depth_chart.get(position, [])
        active = []
        for p in candidates:
            # TRAIT: Iron Man (Ignores fatigue minimums slightly)
            threshold = 15 if "Iron Man" in p.traits else 25
            
            # TRAIT: Soft (Refuses to play if hurt at all)
            if "Soft" in p.traits and p.weeks_injured > 0: continue
            
            if p.weeks_injured == 0 and p.stamina > threshold:
                active.append(p)
            if len(active) == count: break
        
        if len(active) < count:
            for p in candidates:
                if p not in active and p.weeks_injured == 0:
                    active.append(p)
                    if len(active) == count: break
        
        if not active: active = [candidates[0]] if candidates else []
        if count == 1: return active[0] if active else None
        return active

    def process_fatigue_and_injury(self, player, fatigue_amount, risk_multiplier=1.0):
        if not player: return None
        
        # TRAIT: Trench Dog (Less stamina loss)
        if "Trench Dog" in player.traits: fatigue_amount = int(fatigue_amount * 0.5)
        
        player.stamina = max(0, player.stamina - fatigue_amount)
        dur = player.attributes.get("DUR", 75)
        base_chance = 0.5 + (100 - dur) * 0.02
        if player.stamina < 30: base_chance += 2.0
        
        # TRAIT: Glass Cannon (Higher risk)
        if "Glass Cannon" in player.traits: risk_multiplier *= 3.0
        
        final_chance = base_chance * risk_multiplier
        if random.uniform(0, 100) < final_chance:
            severity_penalty = (100 - dur)
            severity_roll = random.randint(0, 100) + severity_penalty
            
            if severity_roll > 120: pool, lbl = INJURIES_SEVERE, "SEVERE"
            elif severity_roll > 90: pool, lbl = INJURIES_SERIOUS, "SERIOUS"
            elif severity_roll > 55: pool, lbl = INJURIES_MODERATE, "MODERATE"
            else: pool, lbl = INJURIES_MINOR, "MINOR"
            
            # TRAIT: Iron Man (Downgrades Minor/Moderate to Nothing)
            if "Iron Man" in player.traits and lbl in ["MINOR", "MODERATE"]:
                return f"[yellow]{player.last_name} shakes off a hit.[/yellow]"

            inj_name, min_w, max_w = random.choice(pool)
            player.weeks_injured = random.randint(min_w, max_w)
            player.injury_type = inj_name
            return f"[bold red]{player.last_name} INJURED ({inj_name} - {lbl})[/bold red]"
        return None

    def recover_stamina_step(self):
        teams = [self.home, self.away]
        for team in teams:
            for p in team.roster:
                if p.weeks_injured == 0 and p.stamina < 100:
                    p.stamina = min(100, p.stamina + 4)

    def call_plays(self, mode):
        coach = self.offense.coach
        qb = self.get_active_player(self.offense, "QB")
        
        # 3rd OT+ Rules: Shootout from 3-yard line. No kicking allowed.
        if self.is_overtime and self.ot_period >= 3:
            return ("RUN_POWER", "GOAL_LINE") if random.random() < 0.5 else ("PASS_QUICK", "MAN_1")

        if self.ball_on < 3: return "RUN_POWER", "GOAL_LINE"
        
        if self.down == 4:
            field_goal_range = 65 
            agg_score = coach.fourth_down_agg
            if self.quarter == 4 and self.stats[self.offense]["score"] < self.stats[self.defense]["score"]:
                if self.time_remaining < 180: agg_score += 50 

            # TRAIT: Gut Feeling (High Variance decision)
            if "Gut Feeling" in coach.traits and random.random() < 0.2:
                agg_score += random.randint(-20, 40)

            # TRAIT: Fourth Down Fire (Boost to aggressiveness)
            if "Fourth Down Fire" in coach.traits:
                agg_score += 15

            if self.ball_on >= field_goal_range:
                if self.ball_on > 40 and agg_score > 15: 
                     if self.distance <= 2: return "RUN_POWER", "GOAL_LINE"
                     return "PASS_QUICK", "MAN_1"
                return "FIELD_GOAL", "BLOCK"
            else:
                if agg_score > 25: return "PASS_DEEP", "BLITZ_HEAVY"
                return "PUNT", "RETURN"

        # --- ADJUSTED PLAYCALLING BIAS ---
        pass_prob = (coach.run_pass_bias * 0.08) 
        
        # Contextual Modifiers
        if self.distance > 8: pass_prob += 0.25 # Need yards, pass more
        if self.distance < 4: pass_prob -= 0.15 # Short yardage, run more
        
        if mode == "HURRY": pass_prob += 0.35
        if mode == "CHEW": pass_prob -= 0.40
        
        # Coach Trait adjustments
        if qb and "Gunslinger" in qb.traits: pass_prob += 0.15
        if qb and "Game Manager" in qb.traits: pass_prob -= 0.10
        
        # Clamp probability
        pass_prob = max(0.10, min(0.90, pass_prob))

        is_pass = random.random() < pass_prob
        
        # TRAIT: Hero Ball (Ignores safe calls when losing)
        score_diff = self.stats[self.offense]["score"] - self.stats[self.defense]["score"]
        if qb and "Hero Ball" in qb.traits and score_diff < -3 and self.quarter == 4:
            is_pass = True 

        if is_pass:
            roll = random.randint(0, 10)
            if roll < coach.aggressiveness:
                choices = ["PASS_DEEP", "PASS_PA", "PASS_STD"]
            else:
                choices = ["PASS_QUICK", "PASS_SCREEN", "PASS_STD"]
            
            if qb and "Gunslinger" in qb.traits and random.random() < 0.4: off_play_key = "PASS_DEEP"
            elif qb and "Game Manager" in qb.traits and random.random() < 0.4: off_play_key = "PASS_QUICK"
            else: off_play_key = random.choice(choices)
            
            def_play_key = random.choice(["COVER_2", "COVER_3", "BLITZ_ZONE", "MAN_1"])
        else:
            roll = random.randint(0, 10)
            if roll < coach.aggressiveness: choices = ["RUN_DRAW", "RUN_ZONE", "RUN_POWER"]
            else: choices = ["RUN_POWER", "RUN_ZONE", "RUN_POWER"] # Weighted towards POWER
            off_play_key = random.choice(choices)
            def_play_key = random.choice(["BLITZ_HEAVY", "MAN_1", "BLITZ_ZONE", "GOAL_LINE"])

        return off_play_key, def_play_key

    def get_defender_matchup(self, target_pos, def_key):
        is_zone = "COVER" in def_key or "ZONE" in def_key
        def_pos_key = "DB"
        if target_pos == "WR": def_pos_key = "DB"
        elif target_pos == "TE": def_pos_key = "LB" if random.random() < 0.7 else "DB"
        elif target_pos == "RB": def_pos_key = "LB"

        unit = self.get_active_player(self.defense, def_pos_key, count=3)
        if not isinstance(unit, list): unit = [unit]
        return random.choice(unit), is_zone

    def resolve_pass_target(self, off_key, def_key, qb):
        play_data = OFF_PLAYS[off_key]
        routes = play_data.get("routes", {"WR": ("Route", 10)})
        candidates = []
        eligible = []
        
        wrs = self.get_active_player(self.offense, "WR", count=2)
        tes = self.get_active_player(self.offense, "TE", count=1)
        rbs = self.get_active_player(self.offense, "RB", count=1)
        if wrs: eligible.extend([("WR", p) for p in (wrs if isinstance(wrs, list) else [wrs])])
        if tes: eligible.extend([("TE", p) for p in (tes if isinstance(tes, list) else [tes])])
        if rbs: eligible.extend([("RB", p) for p in (rbs if isinstance(rbs, list) else [rbs])])

        for pos_name, player in eligible:
            if pos_name not in routes: continue
            route_type, priority = routes[pos_name]
            if route_type == "Block": continue 
            defender, is_zone = self.get_defender_matchup(pos_name, def_key)
            
            off_skill = (player.attributes["SPD"] * 0.45) + (player.attributes["AGI"] * 0.55)
            def_skill = (defender.attributes["SPD"] * 0.50) + (defender.attributes["INT"] * 0.50)
            
            # TRAIT: Route Technician (Separation bonus)
            if "Route Technician" in player.traits: off_skill += 10
            # TRAIT: Satellite (RB acting like WR)
            if "Satellite" in player.traits and pos_name == "RB": off_skill += 15
            
            if is_zone: def_skill = (def_skill + 85) / 2
            
            # Variance added to separation
            raw_sep = off_skill - def_skill + random.randint(-15, 15)
            t_score = raw_sep + (priority * 3)
            candidates.append({"player": player, "defender": defender, "separation": raw_sep, "score": t_score})

        candidates.sort(key=lambda x: x["score"], reverse=True)
        if not candidates: return None, None, 0

        top_options = candidates[:3]
        weights = [max(1, c["score"] + 20) for c in top_options]
        best_opt = random.choices(top_options, weights=weights, k=1)[0]
        
        vision_roll = random.randint(0, 100) + (qb.attributes["INT"] * 0.3)
        if vision_roll > 50: 
            if best_opt["separation"] < -2:
                for alt in candidates:
                    if alt == best_opt: continue
                    # TRAIT: Game Manager (Always finds open man even if low priority)
                    thresh = 1 if "Game Manager" in qb.traits else 5
                    if alt["separation"] > (best_opt["separation"] + thresh):
                        best_opt = alt
                        break
        target = best_opt
        return target["player"], target["defender"], target["separation"]

    def resolve_play(self, off_key, def_key, mode):
        self.recover_stamina_step()
        
        # --- Coach & Scheme Logic ---
        coach_off = self.offense.coach
        coach_def = self.defense.coach
        
        # Scheme Flags
        is_air_raid = coach_off.run_pass_bias >= 7
        is_smashmouth = coach_off.run_pass_bias <= 3
        
        # Scheme Playcall Synergy Bonus
        scheme_bonus = 0
        if is_air_raid and "PASS" in off_key: scheme_bonus = 5
        if is_smashmouth and "RUN" in off_key: scheme_bonus = 5

        qb = self.get_active_player(self.offense, "QB")
        rb = self.get_active_player(self.offense, "RB")
        
        in_red_zone = self.ball_on > 80
        injuries_this_play = []
        
        # --- CLUTCH LOGIC ---
        score_diff = abs(self.stats[self.home]["score"] - self.stats[self.away]["score"])
        is_clutch_time = (self.quarter == 4 or self.is_overtime) and score_diff <= 8

        # --- Halftime Adjuster Trait ---
        halftime_boost = 0
        if self.quarter == 3:
            off_score = self.stats[self.offense]["score"]
            def_score = self.stats[self.defense]["score"]
            if off_score < def_score:
                halftime_boost += coach_off.get_game_bonus("halftime", score_diff=off_score-def_score)

        # --- SPECIAL TEAMS ---
        if off_key == "PUNT":
            # Check for Blocked Punt (Rare: 1%)
            if random.random() < 0.01:
                self.switch_possession(turnover=True)
                return "[bold red]PUNT BLOCKED![/bold red] Recovered by defense.", 0, 10

            puntr = self.get_active_player(self.offense, "P")
            dist = 35 + random.randint(0, 20)
            if "Big Leg" in puntr.traits: dist += 5
            
            puntr.stats["punts"] += 1; puntr.stats["punt_yds"] += dist
            self.switch_possession()
            self.ball_on = 100 - (self.ball_on + dist)
            if self.ball_on < 0: self.ball_on = 20
            return f"Punt for {dist} yds.", 0, 15
            
        if off_key == "FIELD_GOAL":
            # Check for Blocked FG (Rare: 1.5%)
            if random.random() < 0.015:
                self.switch_possession(turnover=True)
                return "[bold red]KICK BLOCKED![/bold red] Defense recovers!", 0, 10

            kicker = self.get_active_player(self.offense, "K")
            kicker.stats["fg_att"] += 1
            dist = 100 - self.ball_on + 17
            
            # TRAIT: Ice Veins (Clutch Kicking)
            acc_bonus = 10 if ("Ice Veins" in kicker.traits and is_clutch_time) else 0
            if "Choker" in kicker.traits and is_clutch_time: acc_bonus -= 20
            
            if dist <= 25: acc = 100
            else: acc = 100 - (dist - 25) * 1.0 + acc_bonus
            
            if random.randint(1, 100) < acc:
                kicker.stats["fg_made"] += 1
                self.stats[self.offense]["score"] += 3
                self.switch_possession(kickoff=not self.is_overtime, ot_reset=self.is_overtime)
                return f"{int(dist)} yd FG [bold green]GOOD[/bold green].", 3, 5
            else:
                self.switch_possession(kickoff=False, ot_reset=self.is_overtime, turnover=True)
                return f"{int(dist)} yd FG [bold red]MISSED[/bold red].", 0, 5

        # --- STANDARD PLAY RESOLUTION ---
        play_data = OFF_PLAYS[off_key]
        def_data = DEF_STRATEGIES[def_key]
        
        strat_mod = 0
        desc_add = ""
        
        # Strategy Counter Logic
        if off_key in def_data["bonus_vs"]: 
            strat_mod = -15
            desc_add = f" [red](Def Read!)[/red]"
        elif off_key in def_data["weak_vs"]: 
            strat_mod = 15
            desc_add = f" [green](Great Call!)[/green]"

        # TRAIT: The Analyst
        if "The Analyst" in coach_off.traits:
            if strat_mod < 0: 
                strat_mod = 0
                desc_add = f" [yellow](Analyst Save)[/yellow]"
            elif strat_mod > 0:
                strat_mod += 5

        # TRAIT: 4th Down Fire
        if self.down == 4:
            strat_mod += coach_off.get_game_bonus("4th_down")

        strat_mod += halftime_boost
        result_text = ""; yards = 0; time_used = play_data["time"]

        # >>> RUN PLAY LOGIC <<<
        if play_data["type"] == "RUN":
            rb.stats["rush_att"] += 1
            inj = self.process_fatigue_and_injury(rb, 12, risk_multiplier=1.0)
            if inj: injuries_this_play.append(inj)
            
            dl_core = self.get_active_player(self.defense, "DL", count=3)
            ol_core = self.get_active_player(self.offense, "OL", count=5)
            if not isinstance(dl_core, list): dl_core = [dl_core]
            if not isinstance(ol_core, list): ol_core = [ol_core]

            dl_avg = sum(p.attributes["STR"] + p.attributes["TKL"] for p in dl_core) / (len(dl_core)*2)
            ol_avg = sum(p.attributes["STR"] + p.attributes["BLK"] for p in ol_core) / (len(ol_core)*2)
            
            # -- SCHEME IMPACT --
            if is_smashmouth: ol_avg += 3 
            if is_air_raid: ol_avg -= 2   
            if "Field General" in qb.traits: ol_avg += 5
            
            # TRENCH CALCULATION (Increased Variance)
            trench_win = (ol_avg - dl_avg) + (random.randint(-20, 20)) + (strat_mod * 0.5) + (scheme_bonus * 0.5)
            if in_red_zone: trench_win += 4
            
            # TRAIT: First Step
            if any("First Step" in p.traits for p in dl_core): trench_win -= 5
            
            tackler = None
            
            # FUMBLE CHECK (Run)
            # 1.5% chance normally, higher if tired or low STR
            fumble_chance = 1.5
            if rb.stamina < 30: fumble_chance += 3
            if rb.attributes["STR"] < 50: fumble_chance += 1
            if "Butterfingers" in rb.traits: fumble_chance += 5
            
            if random.uniform(0, 100) < fumble_chance:
                self.switch_possession(turnover=True)
                self.stats[self.defense]["to"] += 1
                return f"[bold red]FUMBLE![/bold red] {rb.last_name} loses the ball! Recovered by defense.", 0, 10

            # Run Outcome Resolution
            if trench_win < -15: 
                yards = random.randint(-4, 0)
                tackler = random.choice(dl_core)
                result_text = f"Stuffed by {tackler.last_name}!"
            elif trench_win < 5:
                yards = random.randint(1, 5) 
                lb_core = self.get_active_player(self.defense, "LB", count=3)
                if not isinstance(lb_core, list): lb_core = [lb_core]
                tackler = random.choice(lb_core) 
                result_text = "Run up middle."
            else:
                # Good blocking, now RB vs defenders
                yards = random.randint(4, 12)
                
                # Breakaway Logic
                breakaway_chance = 0.03 + (rb.attributes["SPD"] / 2000)
                if random.random() < breakaway_chance:
                    bonus_yards = random.randint(20, 60)
                    yards += bonus_yards
                    result_text = f"[bold yellow]BREAKAWAY![/bold yellow]"
                else: 
                    result_text = "Nice run!"
                
                if random.random() < 0.7: 
                    lb_core = self.get_active_player(self.defense, "LB", count=3)
                    if not isinstance(lb_core, list): lb_core = [lb_core]
                    tackler = random.choice(lb_core)
                else: 
                    db_core = self.get_active_player(self.defense, "DB", count=3)
                    if not isinstance(db_core, list): db_core = [db_core]
                    tackler = random.choice(db_core)
            
            # TRAIT: Ankle Biter / Bruiser interactions
            if tackler:
                if "Ankle Biter" in tackler.traits and random.random() < 0.3:
                    yards += 4; result_text += " Missed tackle!"
                if "Bruiser" in rb.traits and random.random() < 0.3:
                    yards += 3; result_text += f" {rb.last_name} runs through contact!"

            rb.stats["rush_yds"] += yards
            if tackler: 
                tackler.stats["tackles"] += 1
                inj_t = self.process_fatigue_and_injury(tackler, 8, risk_multiplier=1.0)
                if inj_t: injuries_this_play.append(inj_t)
                
            yard_str = f"[green]{yards}[/green]" if yards > 0 else f"[red]{yards}[/red]"
            result_text += f" {yard_str} yds.{desc_add}"
            time_used += 5

        # >>> PASS PLAY LOGIC <<<
        else:
            target, defender, separation = self.resolve_pass_target(off_key, def_key, qb)
            
            if is_air_raid: separation += 2
            
            dl_core = self.get_active_player(self.defense, "DL", count=3)
            ol_core = self.get_active_player(self.offense, "OL", count=5)
            if not isinstance(dl_core, list): dl_core = [dl_core]
            if not isinstance(ol_core, list): ol_core = [ol_core]
            
            dl_pres = sum(p.attributes["STR"] for p in dl_core) / len(dl_core)
            ol_blk = sum(p.attributes["BLK"] for p in ol_core) / len(ol_core)
            
            if is_air_raid: ol_blk += 2    
            if is_smashmouth: ol_blk -= 3  
            if any("Brick Wall" in p.traits for p in ol_core): ol_blk += 8
            if any("Turnstile" in p.traits for p in ol_core): ol_blk -= 8
            
            pressure_roll = ((dl_pres - ol_blk) / 2) - strat_mod + random.randint(-20, 20)
            play_concluded = False

            # Pressure Outcomes
            if (pressure_roll > 20) or (target is None):
                escape_ability = (qb.attributes["SPD"] * 0.6) + (qb.attributes["AGI"] * 0.4)
                
                if "Statue" in qb.traits: escape_ability -= 20
                if "Escapist" in qb.traits: escape_ability += 15

                escape_roll = random.randint(0, 100)
                if escape_ability > (escape_roll + 30):
                    scramble_yards = random.randint(1, int(qb.attributes["SPD"] / 6) + 2)
                    qb.stats["rush_att"] += 1; qb.stats["rush_yds"] += scramble_yards
                    yards = scramble_yards
                    result_text = f"Pressure! {qb.last_name} scrambles for [green]{scramble_yards}[/green] yds."
                    inj_s = self.process_fatigue_and_injury(qb, 15, risk_multiplier=3.0)
                    if inj_s: injuries_this_play.append(inj_s)
                    time_used = 25; play_concluded = True
                
                elif not play_concluded:
                    # SACK logic with Fumble Chance
                    sacker = random.choice(dl_core)
                    loss = random.randint(2, 9)
                    
                    # FUMBLE CHECK (Sack)
                    if random.random() < 0.05: # 5% chance on sack
                        self.switch_possession(turnover=True)
                        self.stats[self.defense]["to"] += 1
                        qb.stats["sacks_taken"] += 1; sacker.stats["sacks"] += 1
                        return f"[bold red]STRIP SACK![/bold red] {sacker.last_name} knocks it loose! Defense ball.", 0, 30

                    qb.stats["sacks_taken"] += 1; sacker.stats["sacks"] += 1
                    yards = -loss; result_text = f"[bold red]SACK![/bold red] {sacker.last_name} drops QB for [red]-{loss}[/red]."; time_used = 45; play_concluded = True
                    inj_q = self.process_fatigue_and_injury(qb, 20, risk_multiplier=5.0)
                    if inj_q: injuries_this_play.append(inj_q)
            
            # Throwing Outcomes
            if not play_concluded:
                qb.stats["pass_att"] += 1 
                base_acc = (qb.attributes["ACC"] * 0.50)
                base_cth = (target.attributes["CTH"] * 0.50)
                sep_bonus = separation * 1.5 
                
                if is_air_raid: base_acc += 5
                base_acc += coach_off.get_game_bonus("qb_attributes")
                if "Stone Hands" in target.traits: base_cth -= 15
                
                catch_chance = max(40, min(99, 60 + base_acc + base_cth + sep_bonus))
                
                if "Safety Valve" in target.traits and self.down == 3 and self.distance < 5:
                    catch_chance += 15

                roll = random.randint(1, 100)
                
                # Check for DROP (Even if catch chance passed)
                drop_chance = 3
                if "Stone Hands" in target.traits: drop_chance = 10
                is_drop = False
                
                if roll <= catch_chance:
                    if random.randint(0, 100) < drop_chance:
                        is_drop = True
                        play_concluded = True
                        result_text = f"Incomplete. {target.last_name} [red]DROPPED[/red] the pass!"
                else:
                    play_concluded = True
                    result_text = f"Incomplete pass to {target.last_name}."

                if play_concluded:
                    self.process_fatigue_and_injury(qb, 5, risk_multiplier=0.1)
                    yards = 0; time_used = 15
            
            # Interception Logic
            if not play_concluded:
                risky_throw = separation < -5
                bad_read = random.randint(0, 100) > qb.attributes["INT"]
                
                if "Gunslinger" in qb.traits: bad_read = random.randint(0, 100) > (qb.attributes["INT"] - 10)

                int_chance = defender.attributes["INT"] * 0.16
                if "Ball Hawk" in defender.traits: int_chance *= 1.25
                int_chance_mod = coach_def.get_game_bonus("int_chance_defense")
                if int_chance_mod > 0: int_chance = int_chance * (1 + (int_chance_mod/100.0))

                if (risky_throw or bad_read) and random.randint(1, 100) < int_chance:
                    defender.stats["int_made"] += 1; qb.stats["pass_int"] += 1
                    self.switch_possession(turnover=True); self.stats[self.defense]["to"] += 1
                    return f"[bold red]INTERCEPTED[/bold red] by {defender.last_name}!", 0, 20

            # Completion & Yards
            if not play_concluded:
                qb.stats["pass_cmp"] += 1; target.stats["rec_cat"] += 1
                base_yards = 20 if "DEEP" in off_key else (10 if "STD" in off_key else 4)
                
                # Dynamic YAC (Yards After Catch)
                yac = 0
                if target.attributes["SPD"] > defender.attributes["SPD"]:
                    yac = random.randint(1, 8)
                    if random.random() < 0.1: yac += random.randint(10, 25) # Big play
                
                if "Human Joystick" in target.traits: yac += random.randint(2, 10)
                
                yards = max(1, base_yards + yac + random.randint(-2, 5))
                target.stats["rec_yds"] += yards; qb.stats["pass_yds"] += yards
                
                self.process_fatigue_and_injury(qb, 5, risk_multiplier=0.1)
                inj_t = self.process_fatigue_and_injury(target, 10, risk_multiplier=1.0)
                if inj_t: injuries_this_play.append(inj_t)
                
                # Tackle logic
                if random.random() < 0.3:
                    lb_core = self.get_active_player(self.defense, "LB", count=3)
                    if not isinstance(lb_core, list): lb_core = [lb_core]
                    tackler = random.choice(lb_core); tackler.stats["tackles"] += 1
                else: 
                    defender.stats["tackles"] += 1
                    tackler = defender
                
                if tackler:
                    inj_def = self.process_fatigue_and_injury(tackler, 8, risk_multiplier=1.0)
                    if inj_def: injuries_this_play.append(inj_def)

                yard_str = f"[green]{yards}[/green]"
                result_text = f"Pass to {target.last_name} for {yard_str} yds."; time_used += 5 

        if injuries_this_play: result_text += " " + " ".join(injuries_this_play)

        time_used += 10 
        
        # TRAIT: Clock Manager
        if mode == "HURRY": 
            time_used = 25
            if "Clock Manager" in coach_off.traits: time_used = 18 
        if mode == "CHEW": 
            time_used = 55
            if "Clock Manager" in coach_off.traits: time_used = 60 
        
        self.stats[self.offense]["yards"] += yards
        self.ball_on += yards
        
        score = 0
        if self.ball_on >= 100:
            result_text += f" [bold green]TOUCHDOWN![/bold green]"; score = 7; self.stats[self.offense]["score"] += 7
            if play_data["type"] == "RUN": rb.stats["rush_td"] += 1
            else: 
                qb.stats["pass_td"] += 1
                if "target" in locals() and target: target.stats["rec_td"] += 1
            self.switch_possession(kickoff=not self.is_overtime, ot_reset=self.is_overtime)
        elif self.ball_on <= 0:
            result_text += f" [bold red]SAFETY![/bold red]"; self.stats[self.defense]["score"] += 2 
            self.switch_possession(kickoff=True)
        else:
            if yards >= self.distance:
                self.down = 1; self.distance = 10; result_text += f" [cyan]1st Down![/cyan]"
            else:
                self.down += 1; self.distance -= yards
                if self.down > 4:
                    result_text += f" [magenta]Turnover on Downs![/magenta]"; self.switch_possession(ot_reset=self.is_overtime, turnover=True)

        return result_text, score, time_used
    
    
    def play_overtime(self, file_handle):
        self.is_overtime = True
        self.ot_period = 1
        
        if file_handle: file_handle.write("\n--- OVERTIME ---\n")
        
        # Loop until scores are NOT tied after equal possessions
        while self.stats[self.home]["score"] == self.stats[self.away]["score"]:
            self.log.append(f"\n[bold yellow]--- OVERTIME PERIOD {self.ot_period} ---[/bold yellow]")
            if file_handle: file_handle.write(f"\n--- OT PERIOD {self.ot_period} ---\n")
            
            teams = [self.away, self.home]
            
            # --- 3rd OT+ RULE: 2-Point Conversion Shootout ---
            is_shootout = self.ot_period >= 3

            for i, team in enumerate(teams):
                self.offense = team
                self.defense = self.home if team == self.away else self.away
                
                if is_shootout:
                    # Shootout: Ball on 3 yard line (97), 1 play only
                    self.ball_on = 97 
                    self.down = 4
                    self.distance = 3
                    
                    self.log.append(f"\n[bold]{team.name} 2-Point Attempt[/bold] (from 3-yd line)")
                    if file_handle: file_handle.write(f"\n{team.name} 2-Pt Attempt\n")
                    
                    if getattr(self.game, 'slow_mode', False):
                        self.draw_live_ui(f"2-Pt Shootout - {team.name}")
                        input()

                    # Run one play
                    off_key, def_key = self.call_plays("NORMAL") # Forces GOAL_LINE
                    desc, points, _ = self.resolve_play(off_key, def_key, "NORMAL")
                    
                    # Manual Score Adjustment for 2-Pt Logic
                    # resolve_play gives 7 for TD. In shootout, it's 2 pts.
                    if points == 7:
                        self.stats[self.offense]["score"] -= 5 # 7 - 5 = 2
                        desc = desc.replace("TOUCHDOWN", "2-PT CONVERSION GOOD")
                        if file_handle: file_handle.write(f"   RESULT: 2-PT GOOD\n")
                    else:
                        if "Turnover" in desc or "INTERCEPTED" in desc or "FUMBLE" in desc:
                             desc = desc + " [red]2-PT FAILED[/red]"
                        else:
                             desc = desc + " [red]2-PT FAILED[/red]"
                        if file_handle: file_handle.write(f"   RESULT: 2-PT FAILED\n")

                    self.log.append(f"   Result: {desc}")
                    if getattr(self.game, 'slow_mode', False):
                        self.draw_live_ui(desc)
                        input()

                else:
                    # Normal Overtime (Periods 1 & 2)
                    # Reset for OT possession (Start @ Opp 25)
                    self.ball_on = 75 
                    self.down = 1
                    self.distance = 10
                    
                    self.log.append(f"\n[bold]{team.name} Possession[/bold] (Start @ Opp 25)")
                    if file_handle: file_handle.write(f"\n{team.name} Possession\n")
                    
                    if getattr(self.game, 'slow_mode', False):
                        self.draw_live_ui(f"Start of OT Period {self.ot_period} - {team.name}")
                        input()

                    drive_over = False
                    while not drive_over:
                        off_key, def_key = self.call_plays("NORMAL")
                        desc, points, _ = self.resolve_play(off_key, def_key, "NORMAL")
                        
                        if getattr(self.game, 'slow_mode', False):
                            self.draw_live_ui(desc)
                            input()

                        log_entry = f"   {self.down}&{int(self.distance)}: {desc}"
                        self.log.append(log_entry)
                        if file_handle: file_handle.write(log_entry + "\n")
                        
                        # End drive on Score or Turnover
                        if "TOUCHDOWN" in desc or "FG GOOD" in desc or "INTERCEPTED" in desc or "Turnover" in desc or "FG MISSED" in desc or "SAFETY" in desc or "FUMBLE" in desc or "BLOCKED" in desc:
                            drive_over = True
            
            self.ot_period += 1

    def play_game(self):
        # UI: Simple start message if not in slow mode
        # This was previously a PRINT statement that spammed the log
        # Removed for silent simulation
        pass 

        file_handle = None
        if self.game.export_log:
            filename = f"Week{self.game.week}_{self.away.name.replace(' ','')}_vs_{self.home.name.replace(' ','')}.txt"
            try:
                file_handle = open(filename, "w")
                header = f"GAME LOG: {self.away.name} vs {self.home.name} | Week {self.game.week}\n"
                file_handle.write(header + "="*60 + "\n\n")
            except: pass

        while self.quarter <= 4:
            if getattr(self.game, 'slow_mode', False):
                last_desc = self.log[-1].split("PLAY:")[-1].strip() if self.log else "Game Start"
                self.draw_live_ui(last_desc)
                input()

            mode = self.check_time_management()
            clock = self.get_clock_str()
            situation = f"Q{self.quarter} {clock} | {self.offense.name} ball | {self.down} & {int(self.distance)} @ {self.get_field_pos_str()} [{mode}]"
            off_key, def_key = self.call_plays(mode)
            desc, _, time_used = self.resolve_play(off_key, def_key, mode)
            log_str = f"{situation}\n   PLAY: {desc}"
            self.log.append(log_str)
            if file_handle: file_handle.write(log_str + "\n\n")
            self.time_remaining -= time_used
            if self.time_remaining <= 0:
                if self.quarter < 4:
                    self.quarter += 1
                    self.time_remaining = 900 
                    if file_handle: file_handle.write(f"\n--- END OF QUARTER {self.quarter-1} ---\n\n")
                else: break 

        if self.stats[self.home]["score"] == self.stats[self.away]["score"]:
            self.play_overtime(file_handle)

        self.game.home_score = self.stats[self.home]["score"]
        self.game.away_score = self.stats[self.away]["score"]
        self.game.played = True
        self.game.game_log = self.log
        if file_handle:
            file_handle.write("="*60 + "\n")
            file_handle.write(f"FINAL: {self.away.name} {self.game.away_score} - {self.home.name} {self.game.home_score}\n")
            file_handle.close()
            self.game.export_log = False
        return self.game