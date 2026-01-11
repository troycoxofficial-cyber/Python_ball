import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from coach import Coach
from world_gen import load_names

console = Console()

# --- UTILITY FUNCTIONS ---

def calculate_expectations(school):
    """
    Returns a target win count and a text description of expectations based on prestige.
    """
    if school.prestige >= 95:
        return 11, "National Championship Contender"
    elif school.prestige >= 90:
        return 10, "Playoff or Bust"
    elif school.prestige >= 80:
        return 9, "Conference Championship Contender"
    elif school.prestige >= 70:
        return 8, "Top 25 Finish"
    elif school.prestige >= 60:
        return 6, "Bowl Eligibility"
    elif school.prestige >= 40:
        return 4, "Improvement / Rebuild"
    else:
        return 3, "Competitiveness"

def update_school_budget(school):
    """
    Updates school budget based on current prestige.
    """
    # Base budget tiers
    if school.prestige >= 90: 
        base = random.randint(15_000_000, 20_000_000)
    elif school.prestige >= 80: 
        base = random.randint(10_000_000, 15_000_000)
    elif school.prestige >= 60: 
        base = random.randint(6_000_000, 10_000_000)
    elif school.prestige >= 40: 
        base = random.randint(3_000_000, 6_000_000)
    else: 
        base = random.randint(1_000_000, 3_000_000)
        
    # Fluctuation based on recent success (Winning makes money)
    if school.wins >= 10: base = int(base * 1.1)
    elif school.wins <= 3: base = int(base * 0.9)
    
    school.budget = base

def get_coach_market_value(coach):
    """Calculates a coach's fair market salary."""
    value = coach.development_skill * 500_000 
    value += (coach.career_wins * 30_000)
    if coach.championships > 0: value += 3_000_000
    
    # Momentum from last season
    if coach.history:
        last = coach.history[-1]
        if "National Champ" in last.get('awards', []): value *= 1.5
        elif "Conf Champ" in last.get('awards', []): value *= 1.2
        elif "10+ Win Season" in last.get('awards', []): value *= 1.1
        
    return int(value)

def determine_contract_length(coach, school):
    """
    Decides contract length based on context.
    """
    length = 4
    if coach.age >= 68: length = 1
    elif coach.age >= 64: length = 2
    elif coach.age >= 60: length = 3
    
    if coach.fan_support < 50: length = min(length, 2)
    elif coach.fan_support > 90 and coach.championships > 0: length = random.randint(6, 10) 
    elif coach.fan_support > 80: length += 1
        
    if coach.career_wins == 0: length = random.choice([3, 4, 4, 5])
    return length

def evaluate_coach_performance(school):
    """
    Adjusts Fan Support based on expectations vs reality.
    Includes 'Goodwill' logic to prevent firing great coaches after one dip.
    """
    coach = school.coach
    if not coach: return

    target_wins, exp_text = calculate_expectations(school)
    school.expectations = exp_text
    
    delta = school.wins - target_wins
    change = delta * 10 
    
    # --- PERFORMANCE CONTEXT MODIFIERS ---
    
    # 1. Penalty for missing elite expectations
    if school.prestige >= 90 and school.wins < 10: 
        change -= 15
    # 2. Reward for exceeding low expectations
    if school.prestige < 50 and school.wins >= 6: 
        change += 20
        
    # 3. Championship Immunity / Major Success
    if school.nat_champ: 
        coach.fan_support = 100
        return # Max support, no math needed
    elif school.conf_champ:
        change += 25
        
    # --- GRACE PERIOD & GOODWILL LOGIC ---
    if change < 0:
        # A. Tenure Grace Period (New hires get slack)
        if coach.years_at_school <= 2:
            change = int(change * 0.5) # Half penalty
            
        # B. Banked Goodwill (Recent success buffers bad years)
        # Check last year's history
        elif coach.history:
            last_year = coach.history[-1]
            # Parse record string "W-L"
            try:
                wins = int(last_year['record'].split('-')[0])
                if wins >= 10 or "National Champ" in last_year['awards']:
                    change = int(change * 0.4) # Huge reduction in penalty
                elif wins >= 8:
                    change = int(change * 0.7)
            except:
                pass

    coach.fan_support += change
    
    # Cap
    coach.fan_support = max(0, min(100, coach.fan_support))
    
    # Consistency Floor: 
    # If you made a bowl game (6 wins) at a non-elite school, floor support at 45
    if school.wins >= 6 and school.prestige < 85:
        if coach.fan_support < 45: coach.fan_support = 45

def generate_new_coach(target_prestige, context="Coordinator"):
    """
    Creates a generated coach to fill vacancies.
    """
    first_names, last_names = load_names()
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    
    if context == "Retread":
        age = random.randint(52, 68)
        rating = random.randint(55, 78)
    elif context == "G5_Star":
        age = random.randint(35, 48)
        rating = random.randint(40, 85) 
    else: 
        age = random.randint(32, 50)
        min_r = max(10, target_prestige - 20)
        max_r = min(99, target_prestige + 10)
        if min_r >= max_r: min_r = max_r - 1
        rating = random.randint(min_r, max_r)
    
    new_coach = Coach(f_name, l_name, rating=rating, age=age)
    new_coach.fan_support = 50 
    
    if context == "G5_Star" and random.random() < 0.5:
        new_coach.traits.append("Program Builder")
    
    return new_coach

# --- COMPREHENSIVE SEARCH LOGIC ---

def assess_roster_fit(school, coach):
    """
    Analyzes if the coach's scheme fits the current roster talent.
    Returns a score modifier (0 to 20).
    """
    if not hasattr(school, 'roster') or not school.roster:
        return 10 # Neutral if no roster data

    # Analyze Roster Strengths
    avg_thp = 0
    avg_str = 0
    qb_count = 0
    ol_count = 0
    
    for p in school.roster:
        if p.position == "QB":
            avg_thp += p.attributes.get("THP", 50)
            qb_count += 1
        elif p.position == "OL":
            avg_str += p.attributes.get("STR", 50)
            ol_count += 1
            
    if qb_count > 0: avg_thp /= qb_count
    if ol_count > 0: avg_str /= ol_count
    
    # Determine Roster Lean
    roster_style = "Balanced"
    if avg_thp > 80: roster_style = "Spread"
    elif avg_str > 80: roster_style = "Power"
    
    # Compare to Coach Scheme
    score = 10 # Base
    
    if coach.scheme_type == "Spread":
        if roster_style == "Spread": score += 10
        elif roster_style == "Power": score -= 5
    elif coach.scheme_type == "Power":
        if roster_style == "Power": score += 10
        elif roster_style == "Spread": score -= 5
        
    return max(0, score)

def calculate_comprehensive_score(school, candidate, origin_school=None):
    """
    The Master Algorithm for hiring. 
    Factors: Talent, Resume, Scheme Fit, Geography, Alma Mater, Budget, Interest.
    Returns a total 'Suitability Score' (0-150).
    """
    score = 0
    
    # 1. BASE QUALITY (0-50 pts)
    score += candidate.development_skill * 4
    
    # 2. RESUME & MOMENTUM (0-30 pts)
    score += min(20, candidate.career_wins / 10) 
    score += (candidate.championships * 10)
    
    if origin_school and origin_school.wins >= 9:
        score += 10
    if candidate.history and "National Champ" in candidate.history[-1].get('awards', []):
        score += 15
        
    # 3. SCHEME FIT (0-20 pts)
    fit_score = assess_roster_fit(school, candidate)
    score += fit_score
    
    # 4. GEOGRAPHY & PIPELINES (0-15 pts)
    region_map = {
        "SOUTH": "Pipeline: South",
        "NORTH": "Pipeline: North",
        "WEST": "Pipeline: West"
    }
    needed_trait = region_map.get(school.region, None)
    if needed_trait and needed_trait in candidate.traits:
        score += 10
    
    # 5. ALMA MATER BONUS (0 or 25 pts)
    if candidate.alma_mater == school.name:
        score += 25
        
    # 6. NEGATIVE FILTERS
    if origin_school and origin_school.wins < 5:
        score -= 40
    if candidate.fan_support < 40:
        score -= 30
        
    return int(score)

def perform_coaching_search(school, universe, free_agents):
    """
    Conducts a full search for a single school.
    Generates candidates, ranks them, and returns a prioritized list.
    """
    candidates = []
    
    # A. ACTIVE COACHES (Poach Targets)
    for other_school in universe.college_league:
        target = other_school.coach
        if not target or other_school == school: continue
        
        # BASIC FILTER
        if other_school.wins < 6 and target.years_at_school > 1: continue
        
        # INTEREST CHECK
        if school.prestige < other_school.prestige - 5: continue
        if target.loyalty_rating >= 9:
            if school.prestige < other_school.prestige + 10: continue

        score = calculate_comprehensive_score(school, target, origin_school=other_school)
        market_val = get_coach_market_value(target)
        
        candidates.append({
            "coach": target,
            "score": score,
            "type": "Poach",
            "cost": market_val,
            "origin": other_school
        })

    # B. FREE AGENTS
    for fa in free_agents:
        score = calculate_comprehensive_score(school, fa, origin_school=None)
        score -= 5 # Unemployment penalty
        market_val = get_coach_market_value(fa)
        
        candidates.append({
            "coach": fa,
            "score": score,
            "type": "FA",
            "cost": market_val,
            "origin": None
        })
        
    # C. NEW CANDIDATES
    # 1. Coordinator
    coord = generate_new_coach(school.prestige, "Coordinator")
    c_score = calculate_comprehensive_score(school, coord)
    c_cost = int(school.budget * 0.45)
    candidates.append({"coach": coord, "score": c_score, "type": "Coordinator", "cost": c_cost, "origin": None})
    
    # 2. G5 Star (for P5 schools)
    if school.prestige > 50:
        g5 = generate_new_coach(school.prestige, "G5_Star")
        g5_score = calculate_comprehensive_score(school, g5) + 5
        g5_cost = int(school.budget * 0.6)
        candidates.append({"coach": g5, "score": g5_score, "type": "G5_Star", "cost": g5_cost, "origin": None})
        
    # 3. Retread (for lower schools)
    if school.prestige < 60:
        ret = generate_new_coach(school.prestige, "Retread")
        r_score = calculate_comprehensive_score(school, ret)
        r_cost = int(school.budget * 0.4)
        candidates.append({"coach": ret, "score": r_score, "type": "Retread", "cost": r_cost, "origin": None})

    # D. SORT BY SCORE
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    return candidates

def process_coaching_carousel(universe, silent=False):
    """
    Main loop for handling firings, retirements, and the hiring search.
    """
    if not silent:
        console.print(Panel("[bold yellow]OFFSEASON COACHING CAROUSEL[/bold yellow]", style="blue"))

    # 1. Update Budgets & Evaluate Performance
    for school in universe.college_league:
        update_school_budget(school)
        if school.coach:
            evaluate_coach_performance(school)
            school.coach.contract_years -= 1

    vacancies = []
    free_agents = []

    # --- PHASE 1: RETIREMENTS ---
    for school in universe.college_league:
        coach = school.coach
        if not coach: continue
        if coach.check_retirement():
            if not silent:
                console.print(f" [red]RETIREMENT:[/red] [bold]{coach.full_name}[/bold] retired from {school.name} (Age: {coach.age}).")
            school.coach_change_event = f"Retired ({coach.full_name})"
            school.coach = None
            vacancies.append(school)

    # --- PHASE 2: FIRINGS & EXPIRATIONS ---
    for school in universe.college_league:
        if school in vacancies: continue 
        coach = school.coach
        if not coach: 
            vacancies.append(school)
            continue
            
        fired = False
        reason = ""
        
        # FIRING LOGIC - REFINED WITH GRACE PERIODS
        
        # 1. MUTINY (Always fire)
        if coach.fan_support < 10: 
            fired = True
            reason = "Mutiny (0-10 Support)"
            
        # 2. HOT SEAT (10-30)
        elif coach.fan_support < 30:
            # Safe if: New (<=3 years) AND not terrible record (>=4 wins)
            if coach.years_at_school <= 3 and school.wins >= 4:
                pass # Safe, given time to rebuild
            elif random.random() < 0.7:
                fired = True
                reason = "Hot Seat (10-30 Support)"
                
        # 3. FAILED EXPECTATIONS (Elite Schools)
        elif coach.fan_support < 50 and school.prestige > 80:
            # Safe if: New (<=3 years) OR had winning record (>=8 wins)
            # Elite schools shouldn't fire a guy going 9-3 even if support is dipping
            if coach.years_at_school <= 3:
                pass
            elif school.wins >= 8:
                pass # Safe for now
            elif random.random() < 0.4:
                fired = True
                reason = "Failed Expectations"

        if not fired and coach.contract_years <= 0:
            if coach.fan_support >= 50:
                market_val = get_coach_market_value(coach)
                if market_val <= school.budget:
                    new_years = determine_contract_length(coach, school)
                    coach.sign_contract(market_val, new_years)
                    if not silent:
                        console.print(f" [green]EXTENSION:[/green] {school.name} extends {coach.full_name} ({new_years} yrs).")
                else:
                    fired = True; reason = "Budget Constraint (Too Expensive)"
            else:
                fired = True; reason = "Contract Expired (Low Support)"

        if fired:
            if not silent:
                console.print(f" [red]FIRED/LEFT:[/red] {school.name} parts ways with {coach.full_name}. Reason: {reason}")
            school.coach_change_event = f"Left: {reason}"
            coach.job_security = 50 
            coach.fan_support = 50 
            free_agents.append(coach)
            school.coach = None
            vacancies.append(school)

    # --- PHASE 3: COMPREHENSIVE SEARCH & HIRING ---
    
    vacancies.sort(key=lambda s: s.prestige, reverse=True)
    
    iteration_limit = 0
    # INCREASED LIMIT: With 300 schools, chains can get long. 1000 is safe.
    while vacancies and iteration_limit < 1000:
        current_school = vacancies.pop(0)
        iteration_limit += 1
        
        ranked_candidates = perform_coaching_search(current_school, universe, free_agents)
        
        hired_candidate = None
        deal_info = None
        
        for cand in ranked_candidates:
            coach = cand['coach']
            cost = cand['cost']
            score = cand['score']
            
            # Affordability (Ambition Check)
            max_budget = current_school.budget
            if score > 85: max_budget = int(max_budget * 1.2)
                
            if cost > max_budget:
                continue 
                
            if cand['type'] == "Poach":
                origin = cand['origin']
                wants_to_keep = (coach.fan_support >= 60 and origin.wins >= 6)
                
                if wants_to_keep:
                    counter_offer = int(cost * 1.1)
                    if origin.budget >= counter_offer:
                        leave_score = 50 + (current_school.prestige - origin.prestige) * 2 - (coach.loyalty_rating * 5)
                        
                        if leave_score < 50:
                            if not silent:
                                console.print(f" [yellow]RETAINED:[/yellow] {origin.name} matched offer to keep {coach.full_name}.")
                            coach.sign_contract(counter_offer, 5)
                            continue # Move to next candidate
            
            hired_candidate = coach
            deal_info = cand
            break
            
        if hired_candidate:
            years = determine_contract_length(hired_candidate, current_school)
            hired_candidate.sign_contract(deal_info['cost'], years)
            current_school.coach = hired_candidate
            
            if hired_candidate in free_agents:
                free_agents.remove(hired_candidate)
                
            if deal_info['type'] == "Poach":
                origin = deal_info['origin']
                origin.coach = None
                origin.coach_change_event = f"Poached by {current_school.name}"
                vacancies.append(origin) 
                vacancies.sort(key=lambda s: s.prestige, reverse=True) 
                
                if not silent:
                     console.print(f" [green]HIRE:[/green] {current_school.name} poaches {hired_candidate.full_name} from {origin.name}!")
            else:
                if not silent:
                    src = deal_info['type']
                    console.print(f" [cyan]HIRE:[/cyan] {current_school.name} hires {hired_candidate.full_name} ({src}).")
        else:
            # Immediate Fallback
            fallback = generate_new_coach(current_school.prestige)
            current_school.coach = fallback
            if not silent:
                console.print(f" [dim]HIRE:[/dim] {current_school.name} hires {fallback.full_name} (Emergency).")

    # --- PHASE 4: CLEANUP (Safety Net) ---
    # Ensure NO team is left without a coach if loop limit hit
    if vacancies:
        if not silent:
            console.print(f"\n[red]WARNING: Carousel limit reached. Force-filling {len(vacancies)} vacancies.[/red]")
        for school in vacancies:
            if school.coach is None:
                emergency_coach = generate_new_coach(school.prestige)
                school.coach = emergency_coach
                school.coach.sign_contract(school.budget * 0.5, 2)
                if not silent:
                    console.print(f" [dim]FORCE HIRE:[/dim] {school.name} -> {emergency_coach.full_name}")

    if not silent:
        console.print("[dim]Carousel Complete.[/dim]\n")

# --- INTERACTIVE VIEW ---

def view_coach_history(universe):
    from views import display_coach_profile

    while True:
        console.clear()
        console.print(Panel("[bold yellow]COACHING CAROUSEL & HISTORY[/bold yellow]", style="blue"))
        
        search_query = Prompt.ask("[cyan]Enter Team Name OR Coach Name (or 'exit')[/cyan]").strip().lower()
        if search_query == 'exit': break
        
        team_matches = [s for s in universe.college_league if search_query in s.name.lower()]
        coach_matches = []
        for s in universe.college_league:
            if s.coach:
                c = s.coach
                if (search_query in c.first_name.lower() or 
                    search_query in c.last_name.lower() or 
                    search_query in c.full_name.lower()):
                    coach_matches.append((c, s))
        
        if not team_matches and not coach_matches:
            console.print("[red]No teams or coaches found.[/red]")
            Prompt.ask("Press Enter...")
            continue
            
        all_options = []
        for tm in team_matches:
            all_options.append({'type': 'Team', 'obj': tm, 'label': f"[Team] {tm.name}"})
        for cm, school in coach_matches:
            all_options.append({'type': 'Coach', 'obj': cm, 'school': school, 'label': f"[Coach] {cm.full_name} ({school.name})"})
            
        target_selection = all_options[0]
        if len(all_options) > 1:
            console.print("[yellow]Multiple matches found:[/yellow]")
            for i, opt in enumerate(all_options):
                console.print(f"[{i+1}] {opt['label']}")
            choices = [str(i+1) for i in range(len(all_options))]
            choice = Prompt.ask("Select Option", choices=choices)
            target_selection = all_options[int(choice)-1]
            
        if target_selection['type'] == 'Team':
            school = target_selection['obj']
            display_coach_profile(school.coach, school)
        else:
            coach = target_selection['obj']
            school = target_selection['school']
            display_coach_profile(coach, school)
            
        Prompt.ask("\n[dim]Press Enter to return...[/dim]")