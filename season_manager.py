import random
from player import Player
from world_gen import POSITION_TEMPLATE, load_names
from scheduler import generate_schedule
from recruiting import process_signing_day, recruiting_hub
from transfer_portal import process_portal_entries, resolve_portal_destinations
from coach_manager import process_coaching_carousel
from rankings import get_heisman_leaders, get_top_25

def update_school_prestige(school, silent=False):
    """
    Dynamically updates a school's prestige based on recent performance vs expectation.
    """
    # 1. Determine Target Performance
    target_wins = int((school.prestige - 10) / 10) + 2
    target_wins = max(2, min(10, target_wins))
    
    delta = school.wins - target_wins
    
    change = 0
    if delta > 0: change = delta 
    elif delta < 0: change = delta 
        
    if school.nat_champ: change += 5
    elif school.conf_champ: change += 2
    
    if school.wins >= 11: change += 1
    if school.wins <= 2: change -= 2
    
    change = max(-5, min(5, change))
    
    school.prestige += change
    school.prestige = max(10, min(99, school.prestige))

def export_season_stat_log(schools, year, silent=False):
    """Generates a text file with average stats per position for simulation tuning."""
    filename = f"season_{year}_stat_log.txt"
    if not silent:
        print(f" - Generating season stat log: {filename}...")
    
    pos_data = {}
    
    for school in schools:
        for p in school.roster:
            if p.position not in pos_data:
                pos_data[p.position] = {}
            
            for stat, val in p.stats.items():
                if stat not in pos_data[p.position]:
                    pos_data[p.position][stat] = []
                pos_data[p.position][stat].append(val)
                
    with open(filename, "w") as f:
        f.write(f"SEASON {year} AVERAGE STATS REPORT\n")
        f.write("="*50 + "\n\n")
        
        sorted_pos = sorted(pos_data.keys())
        for pos in sorted_pos:
            stats = pos_data[pos]
            count = len(stats[list(stats.keys())[0]])
            f.write(f"--- {pos} (Sample Size: {count}) ---\n")
            
            relevant_stats = {k: v for k, v in stats.items() if sum(v) > 0}
            
            for s_name, values in relevant_stats.items():
                avg = sum(values) / len(values)
                mx = max(values)
                f.write(f"   {s_name:<12}: Avg {avg:>6.1f} | Max {mx:>4}\n")
            f.write("\n")

def advance_season(universe, interactive=True, silent=False):
    if not silent:
        print("\n" + "="*40)
        print("      ADVANCING TO NEXT SEASON      ")
        print("="*40)

    current_year = universe.year
    first_names, last_names = load_names()
    
    # --- STEP 0: Generate Average Stat Log ---
    export_season_stat_log(universe.high_school_league, current_year, silent=silent)

    # --- STEP 0.5: PROCESS SEASON AWARDS & HISTORY (NEW) ---
    if not silent:
        print(" [Processing Season Awards & History...]")
        
    # 1. HEISMAN TROPHY
    heisman_leaders = get_heisman_leaders(universe.college_league)
    if heisman_leaders:
        winner, w_team, w_score = heisman_leaders[0]
        
        if not silent:
            print(f" [HEISMAN] The {current_year} Heisman Trophy goes to:")
            print(f"           {winner.position} {winner.full_name}, {w_team.name} ({w_score} pts)")
            
        # Store in Player
        winner.history.append({"event": "Heisman Trophy Winner", "year": current_year})
        
        # Store in Team
        w_team.heisman_winners.append((current_year, winner.full_name))
        
        # Store in Universe
        universe.heisman_history.append({
            "year": current_year,
            "player": f"{winner.position} {winner.full_name}",
            "team": w_team.name,
            "score": w_score,
            "stats": winner.get_stat_summary()
        })

    # 2. NATIONAL CHAMPIONSHIP HISTORY
    nat_champ_team = None
    runner_up_team = None
    
    # Find participants of the Final Game
    final_game = None
    if 16 in universe.schedule:
        for g in universe.schedule[16]:
            if "NATIONAL CHAMPIONSHIP" in g.title and g.played:
                final_game = g
                break
                
    if final_game:
        nat_champ_team = final_game.winner
        runner_up_team = final_game.home_team if final_game.winner != final_game.home_team else final_game.away_team
        
        # Update Stats
        nat_champ_team.national_championships += 1
        
        universe.championship_history.append({
            "year": current_year,
            "champion": nat_champ_team.name,
            "runner_up": runner_up_team.name,
            "score": f"{final_game.winner.name} {max(final_game.home_score, final_game.away_score)} - {min(final_game.home_score, final_game.away_score)} {runner_up_team.name}"
        })
        
    # 3. PLAYOFF APPEARANCES (Check schedule for 'CFP')
    # Use a set to avoid double counting
    playoff_participants = set()
    for week in [14, 15, 16]:
        if week in universe.schedule:
            for g in universe.schedule[week]:
                if "CFP" in g.title:
                    playoff_participants.add(g.home_team)
                    playoff_participants.add(g.away_team)
    
    for team in playoff_participants:
        team.playoff_appearances += 1
        
    # 4. TOP 25 FINISHES
    top_25 = get_top_25(universe.college_league)
    for team in top_25:
        team.top_25_finishes += 1

    # --- STEP 1: COACH HISTORY & PROGRESSION ---
    if not silent:
        print(f" [Archiving Coach History & Processing XP...]")
        
    for school in universe.college_league:
        coach = school.coach
        
        school.temp_season_coach_name = coach.full_name if coach else "Vacancy"
        
        awards = []
        if getattr(school, 'nat_champ', False): awards.append("National Champ")
        if getattr(school, 'conf_champ', False): awards.append("Conf Champ")
        if school.wins >= 10: awards.append("10+ Win Season")
        
        if coach and hasattr(coach, 'archive_season'):
            coach.archive_season(
                year=universe.year,
                team_name=school.name,
                wins=school.wins,
                losses=school.losses,
                conf_wins=0, 
                conf_losses=0,
                awards=awards
            )
            
            # --- CONTRACT DECREMENT ---
            if coach.contract_years > 0:
                coach.contract_years -= 1
        
        if coach:
            xp_gain = (school.wins * 100)
            if school.wins > school.losses: xp_gain += 500
            if "National Champ" in awards: xp_gain += 5000
            
            if hasattr(coach, 'development_skill'):
                 if xp_gain > 0 and coach.development_skill < 10 and random.random() < 0.2:
                     coach.development_skill += 1
                     if not silent:
                         print(f"   > {coach.full_name} improved Development Skill to {coach.development_skill}!")

    # --- NEW STEP: UPDATE PRESTIGE ---
    for school in universe.college_league:
        update_school_prestige(school, silent=silent)

    # --- STEP 1.5: COACHING CAROUSEL ---
    process_coaching_carousel(universe, silent=silent)

    # --- STEP 2: ARCHIVE HIGH SCHOOL STATS ---
    if not silent:
        print(f" [Archiving High School Season Data...]")
    for school in universe.high_school_league:
        for player in school.roster:
            player.archive_season(school.name, school.record_str(), current_year)
    
    # --- STEP 2.5: TRANSFER PORTAL OPENS ---
    portal_pool = process_portal_entries(universe, silent=silent)

    # --- STEP 3: NATIONAL SIGNING DAY ---
    recruiting_rankings = process_signing_day(universe, silent=silent)
    
    if interactive and not silent:
        recruiting_hub(recruiting_rankings)
    elif not silent:
        print(f" [Sim Mode] Skipping Interactive Recruiting Hub.")
        print(f" [Sim Mode] {len(recruiting_rankings)} players signed to colleges.")
    
    # --- STEP 3.25: ARCHIVE TEAM HISTORY ---
    sorted_recruit_ranks = []
    for s, data in recruiting_rankings.items():
        sorted_recruit_ranks.append((s, data['points'])) 
    sorted_recruit_ranks.sort(key=lambda x: x[1], reverse=True)
    
    school_rank_map = {}
    for i, (s, score) in enumerate(sorted_recruit_ranks):
        school_rank_map[s.name] = i + 1

    for school in universe.college_league:
        result = "Missed Bowl"
        if school.nat_champ: result = "National Champ"
        elif school.conf_champ: result = "Conf Champ"
        elif school.wins >= 6: result = "Bowl Eligible"
        
        rec_rank = school_rank_map.get(school.name, 999)
        notes = getattr(school, 'coach_change_event', None)
        coach_name = getattr(school, 'temp_season_coach_name', "Unknown")
        
        if not hasattr(school, 'team_history'): school.team_history = []
        
        history_entry = {
            "year": current_year,
            "coach": coach_name,
            "wins": school.wins,
            "losses": school.losses,
            "pf": school.points_for,
            "pa": school.points_against,
            "rec_rank": rec_rank,
            "result": result,
            "notes": notes 
        }
        school.team_history.append(history_entry)
        
        school.coach_change_event = None
        if hasattr(school, 'temp_season_coach_name'):
            del school.temp_season_coach_name

    # --- STEP 3.5: TRANSFER PORTAL CLOSES ---
    resolve_portal_destinations(universe, portal_pool, silent=silent)
    
    # --- STEP 4: HIGH SCHOOL LEAGUE TRANSITION ---
    if not silent:
        print(f"\n[Processing High School Rosters...]")
    total_hs_new = 0
    
    for school in universe.high_school_league:
        new_roster = []
        for player in school.roster:
            if player.context == "COLLEGE": continue 

            if player.eligibility_year >= 4:
                pass 
            else:
                player.eligibility_year += 1
                player.age += 1
                player.train(coach=school.coach)
                player.reset_stats()
                player.weeks_injured = 0
                player.injury_type = None
                
                if player.eligibility_year == 4:
                    player.calculate_stars()
                    
                new_roster.append(player)
        
        school.roster = new_roster
        
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
                    if getattr(school, 'logging_enabled', False):
                        school.log_event(current_year+1, f"FRESHMAN GENERATED: {new_p.position} {new_p.full_name}")
                    total_hs_new += 1
        
        school.set_depth_chart()
        school.wins = 0; school.losses = 0; school.points_for = 0; school.points_against = 0
        school.schedule = []
        school.conf_champ = False
        school.nat_champ = False

    # --- STEP 5: COLLEGE LEAGUE TRANSITION ---
    if not silent:
        print(f"[Processing College Rosters...]")
    total_college_grads = 0
    
    for school in universe.college_league:
        new_roster = []
        graduating_counts = {}
        recruits_signed = {}
        
        for player in school.roster:
            if player.context == "COLLEGE" and player.eligibility_year > 0:
                already_archived = any(
                    h.get('year') == current_year and h.get('team') == school.name 
                    for h in player.history
                )
                just_arrived = any(
                    h.get('event') == "Transfer Destination" and h.get('year') == current_year
                    for h in player.history
                )

                if not already_archived and not just_arrived:
                     player.archive_season(school.name, school.record_str(), current_year)
            
            if player.eligibility_year >= 4:
                total_college_grads += 1
                if getattr(school, 'logging_enabled', False):
                    school.log_event(current_year, f"GRADUATED: {player.position} {player.full_name}")
                graduating_counts[player.position] = graduating_counts.get(player.position, 0) + 1
            else:
                player.eligibility_year += 1
                player.age += 1
                if school.coach:
                    player.train(coach=school.coach)
                else:
                    player.train(coach=None)
                player.reset_stats()
                player.weeks_injured = 0
                player.injury_type = None
                player.calculate_stars()
                new_roster.append(player)
        
        if hasattr(school, 'incoming_class'):
            for recruit in school.incoming_class:
                if school.coach:
                    recruit.train(coach=school.coach)
                new_roster.append(recruit)
                if getattr(school, 'logging_enabled', False):
                    school.log_event(current_year+1, f"RECRUIT SIGNED: {recruit.position} {recruit.full_name}")
                recruits_signed[recruit.position] = recruits_signed.get(recruit.position, 0) + 1
            del school.incoming_class
            
        school.roster = new_roster

        for pos, target in POSITION_TEMPLATE:
            current_count = sum(1 for p in school.roster if p.position == pos)
            needed = target - current_count
            
            if needed > 0:
                if len(school.roster) >= 55 and current_count > 0:
                    continue

                for _ in range(needed):
                    f_name = random.choice(first_names)
                    l_name = random.choice(last_names)
                    walk_on = Player(f_name, l_name, pos, 1, 10, age=18, context="COLLEGE")
                    walk_on.history.append({"event": "Walk-on", "team": school.name, "year": current_year + 1})
                    school.roster.append(walk_on)
                    if getattr(school, 'logging_enabled', False):
                        school.log_event(current_year+1, f"WALK-ON ADDED: {walk_on.position} {walk_on.full_name}")
                    
        school.set_depth_chart()
        school.wins = 0; school.losses = 0; school.points_for = 0; school.points_against = 0
        school.schedule = []
        school.conf_champ = False
        school.nat_champ = False

    universe.year += 1
    universe.current_week = 1
    universe.schedule = {}
    
    if not silent:
        print(f"\n[Summary]")
        print(f" - HS Freshmen Generated: {total_hs_new}")
        print(f" - College Seniors Graduated: {total_college_grads}")
        print(" - Generating new 12-game schedule...")
        
    universe.schedule = generate_schedule(universe.high_school_league)
    
    if not silent:
        print(f"\nSeason transition complete! Welcome to {universe.year}.")