
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box

console = Console()

# Target roster sizes for colleges
ROSTER_NEEDS = {
    "QB": 3, "RB": 5, "WR": 6, "TE": 3, 
    "OL": 9, "DL": 8, "LB": 7, "DB": 8, 
    "K": 1, "P": 1
}

# Map Conferences to Regions (Approximation)
CONF_REGION_MAP = {
    "SEC": "SOUTH", "ACC": "SOUTH", "Sun Belt": "SOUTH",
    "Big Ten": "NORTH", "MAC": "NORTH", "Independent": "NORTH",
    "Big 12": "MIDWEST", "C-USA": "MIDWEST", "AAC": "MIDWEST",
    "Pac-12": "WEST", "MWC": "WEST"
}

def get_team_needs(school):
    """
    Calculates how many players are needed at each position.
    Strict Replacement Only + Hole Filling.
    Accounts for players ALREADY committed during the season.
    """
    needs = {}
    
    # 1. Analyze Current Roster (Returning vs Graduating)
    returning_counts = {pos: 0 for pos in ROSTER_NEEDS}
    graduating_counts = {pos: 0 for pos in ROSTER_NEEDS}
    
    for p in school.roster:
        if p.eligibility_year < 4: 
            # Returning Player
            if p.position in returning_counts:
                returning_counts[p.position] += 1
        else:
            # Graduating Player
            if p.position in graduating_counts:
                graduating_counts[p.position] += 1
    
    # 2. Subtract Existing Commits (In-Season Recruits)
    committed_counts = {pos: 0 for pos in ROSTER_NEEDS}
    if hasattr(school, 'commits'):
        for p in school.commits:
            if p.position in committed_counts:
                committed_counts[p.position] += 1

    # 3. Calculate Needs
    for pos, target in ROSTER_NEEDS.items():
        returning = returning_counts.get(pos, 0)
        graduating = graduating_counts.get(pos, 0)
        already_committed = committed_counts.get(pos, 0)
        
        # STRICT REPLACEMENT RULE
        recruit_target = graduating
        
        # SAFETY VALVE: Fill empty holes
        total_projected = returning + recruit_target
        if total_projected < target:
            recruit_target += (target - total_projected)
        
        # Critical Shortage Check
        if returning == 0 and recruit_target == 0:
            recruit_target = 1
            
        # Adjust for commits
        final_need = max(0, recruit_target - already_committed)
        
        needs[pos] = final_need
        
    return needs

def calculate_interest_score(recruit, school, needs):
    """
    Calculates a score (0-1000+) representing the recruit's interest in the school.
    Factors: Geography, Prestige, Playing Time, Scheme Fit, Coach Traits.
    """
    score = 0
    
    # 1. PRESTIGE (Base Weight: High)
    score += school.prestige * 3.5
    
    # 2. GEOGRAPHY (Pipeline Bonus)
    school_region = CONF_REGION_MAP.get(school.conference, "MIDWEST")
    is_home_region = (recruit.home_region == school_region)
    
    # National Brand logic
    is_national_brand = school.prestige >= 85
    
    if is_home_region:
        score += 200 # Massive home field advantage
    elif is_national_brand:
        score += 100 # National brands can recruit nationally
    else:
        score -= 50 # Regional schools struggle out of region
        
    # 3. PLAYING TIME (Using updated Needs which accounts for commits)
    need_at_pos = needs.get(recruit.position, 0)
    
    if need_at_pos > 1:
        score += 150 # "We need you now!"
    elif need_at_pos == 0:
        score -= 200 # "No scholarship available"

    # 4. RANDOM FIT BIAS
    random.seed(recruit.id + school.name)
    fit_bonus = random.randint(-50, 100)
    score += fit_bonus
    random.seed() 

    # 5. COACH TRAITS & SCHEME FIT
    # (Delegates to the updated Coach.get_recruiting_bonus method)
    if hasattr(school, 'coach') and school.coach:
        score += school.coach.get_recruiting_bonus(recruit, school)
    
    return int(score)

def process_weekly_recruiting(universe):
    """
    Runs weekly during the season. 
    Allows recruits to verbally commit before Signing Day.
    """
    week = universe.current_week
    # Probability of committing rises as season goes on
    # Week 1: ~5%, Week 12: ~60%
    commit_threshold_bonus = week * 5
    
    new_commits = 0
    
    # Ensure all schools have commits list
    for school in universe.college_league:
        if not hasattr(school, 'commits'): school.commits = []

    # Pre-calculate needs for performance
    team_needs = {school.name: get_team_needs(school) for school in universe.college_league}

    for school in universe.high_school_league:
        for p in school.roster:
            # Only HS Seniors who haven't committed
            if p.eligibility_year == 4 and p.commitment is None:
                
                # Logic: Find top school
                interested_schools = []
                for clg in universe.college_league:
                    needs = team_needs[clg.name]
                    if needs.get(p.position, 0) > 0:
                        score = calculate_interest_score(p, clg, needs)
                        interested_schools.append((clg, score))
                
                if not interested_schools: continue
                
                # Sort by score
                interested_schools.sort(key=lambda x: x[1], reverse=True)
                top_school, top_score = interested_schools[0]
                
                # COMMIT LOGIC
                # Base score for a 5-star is ~600-800.
                # If score is high and random chance hits, they commit.
                
                # Higher stars wait longer?
                patience = 0
                if p.stars >= 4: patience = 200 # Elite players wait
                
                # Check if they pull the trigger
                # Random factor + Week Bonus vs Inertia
                trigger = random.randint(0, 1000)
                if top_score > (600 + patience - commit_threshold_bonus) and trigger > 500:
                    # COMMIT!
                    p.commitment = top_school.name
                    top_school.commits.append(p)
                    
                    # Update Needs for that school immediately so they don't oversign
                    team_needs[top_school.name][p.position] -= 1
                    new_commits += 1

    return new_commits

def process_signing_day(universe, silent=False):
    """
    1. Finalizes commitments for anyone still undecided.
    2. Processes Enrollment (Moves committed players to College rosters).
    """
    if not silent:
        console.print("\n[bold yellow]=== NATIONAL SIGNING DAY ===[/bold yellow]")
    
    # 1. Identify Recruits (HS Seniors)
    hs_seniors = []
    for school in universe.high_school_league:
        for p in school.roster:
            if p.eligibility_year == 4:
                hs_seniors.append(p)
    
    # Sort by PERCEIVED rating
    hs_seniors.sort(key=lambda x: x.recruit_rating, reverse=True)
    
    # 2. Calculate College Needs (Taking into account early commits)
    # Ensure commits list exists
    for school in universe.college_league:
        if not hasattr(school, 'commits'): school.commits = []

    team_needs = {school.name: get_team_needs(school) for school in universe.college_league}
    class_rankings = {school: {"points": 0, "commits": []} for school in universe.college_league}
    
    signed_count = 0
    
    # 3. The Domino Effect (For Uncommitted Players)
    if not silent:
        status_context = console.status("[bold green]Finalizing undecided recruits...[/bold green]")
        status_context.start()

    try:
        for recruit in hs_seniors:
            # If already committed, skip logic, just add to rankings
            if recruit.commitment:
                # Find school obj
                school = next((s for s in universe.college_league if s.name == recruit.commitment), None)
                if school:
                    # Calculate points for rankings
                    star_points = {5: 250, 4: 140, 3: 75, 2: 20, 1: 5}
                    class_rankings[school]["points"] += star_points.get(recruit.stars, 0)
                    class_rankings[school]["commits"].append(recruit)
                continue

            # --- UNDECIDED LOGIC ---
            interested_schools = []
            for school in universe.college_league:
                needs = team_needs[school.name]
                if needs.get(recruit.position, 0) > 0:
                    score = calculate_interest_score(recruit, school, needs)
                    interested_schools.append((school, score))
            
            interested_schools.sort(key=lambda x: x[1], reverse=True)
            
            # Try to sign with top choice
            for school, score in interested_schools[:3]: 
                needs = team_needs[school.name]
                if needs[recruit.position] > 0:
                    # SIGNED!
                    recruit.commitment = school.name
                    school.commits.append(recruit)
                    
                    # Update Needs
                    team_needs[school.name][recruit.position] -= 1
                    
                    # Add to rankings
                    star_points = {5: 250, 4: 140, 3: 75, 2: 20, 1: 5}
                    class_rankings[school]["points"] += star_points.get(recruit.stars, 0)
                    class_rankings[school]["commits"].append(recruit)
                    
                    signed_count += 1
                    break
    finally:
        if not silent:
            status_context.stop()
            
    if not silent:
        console.print(f"[green]Processing Enrollment...[/green]")
        
    # 4. ENROLLMENT: Transfer all committed players to new rosters
    # This officially moves them from HS context to College Incoming Class
    for school, data in class_rankings.items():
        # Clean list to just the player objects
        final_class = []
        for p in data["commits"]:
            p.context = "COLLEGE"
            p.eligibility_year = 1 # Freshman
            p.reset_stats() 
            p.history.append({"event": "Recruited", "by": school.name, "stars": p.stars})
            final_class.append(p)
            
        school.incoming_class = final_class
        # Clear the temp commits list for next year
        school.commits = [] 
        
    return class_rankings

def display_recruiting_rankings(rankings_dict):
    # Sort by points
    sorted_ranks = sorted(rankings_dict.items(), key=lambda x: x[1]['points'], reverse=True)
    
    table = Table(title="NATIONAL RECRUITING CLASS RANKINGS", box=box.SIMPLE_HEAVY)
    table.add_column("Rk", justify="right", style="bold")
    table.add_column("School", style="cyan")
    table.add_column("Pts", justify="right", style="green")
    table.add_column("Signees", justify="center")
    table.add_column("5★", style="yellow")
    table.add_column("4★", style="magenta")
    table.add_column("Top Signee")
    
    for i, (school, data) in enumerate(sorted_ranks):
        commits = data['commits']
        commits.sort(key=lambda x: x.overall, reverse=True) 
        
        c5 = sum(1 for p in commits if p.stars == 5)
        c4 = sum(1 for p in commits if p.stars == 4)
        top_player = commits[0].last_name if commits else "N/A"
        
        table.add_row(
            str(i+1), 
            school.name, 
            str(data['points']), 
            str(len(commits)), 
            str(c5), 
            str(c4), 
            top_player
        )
        
    with console.pager():
        console.print(table)

def display_conference_rankings(rankings_dict):
    conf_data = {}
    
    for school, data in rankings_dict.items():
        conf = school.conference
        if conf not in conf_data: 
            conf_data[conf] = {"points": 0, "commits": 0, "teams": 0}
            
        conf_data[conf]["points"] += data["points"]
        conf_data[conf]["commits"] += len(data["commits"])
        conf_data[conf]["teams"] += 1
        
    table = Table(title="CONFERENCE RECRUITING RANKINGS", box=box.DOUBLE_EDGE)
    table.add_column("Conference", style="bold cyan")
    table.add_column("Total Pts", justify="right", style="green")
    table.add_column("Avg Pts/Team", justify="right", style="yellow")
    table.add_column("Total Signees", justify="right")
    
    sorted_confs = sorted(conf_data.items(), key=lambda x: x[1]['points'], reverse=True)
    
    for conf, stats in sorted_confs:
        avg_pts = stats['points'] / stats['teams'] if stats['teams'] > 0 else 0
        table.add_row(
            conf, 
            str(stats['points']), 
            f"{avg_pts:.1f}", 
            str(stats['commits'])
        )
        
    console.print(table)

def display_star_breakdown(rankings_dict):
    """Displays the total count of 5/4/3/2/1 star recruits in the class."""
    counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total = 0
    
    for school_data in rankings_dict.values():
        for player in school_data['commits']:
            if player.stars in counts:
                counts[player.stars] += 1
            total += 1
            
    table = Table(title="NATIONAL RECRUITING CLASS BREAKDOWN", box=box.SIMPLE_HEAVY)
    table.add_column("Star Rating", justify="center", style="cyan")
    table.add_column("Total Recruits", justify="center", style="green")
    table.add_column("% of Class", justify="center", style="yellow")
    
    for stars in range(5, 0, -1):
        c = counts[stars]
        pct = (c / total * 100) if total > 0 else 0
        stars_str = "★" * stars
        table.add_row(
            stars_str,
            str(c),
            f"{pct:.1f}%"
        )
    
    console.print(table)
    console.print(f"[dim]Total Signees: {total}[/dim]")

def view_team_details(rankings_dict):
    search_query = Prompt.ask("[cyan]Enter Team Name (search)[/cyan]").strip().lower()
    
    matches = [s for s in rankings_dict.keys() if search_query in s.name.lower()]
    
    if not matches:
        console.print("[red]No teams found.[/red]")
        return
        
    target_school = matches[0]
    if len(matches) > 1:
        console.print("[yellow]Multiple teams found:[/yellow]")
        for i, s in enumerate(matches):
            console.print(f"[{i+1}] {s.name}")
        
        choice = Prompt.ask("Select Team", choices=[str(i+1) for i in range(len(matches))])
        target_school = matches[int(choice)-1]
        
    commits = rankings_dict[target_school]['commits']
    commits.sort(key=lambda x: x.overall, reverse=True)
    
    console.print(Panel(f"[bold white]{target_school.name.upper()} SIGNING CLASS[/bold white]", style="blue"))
    
    table = Table(box=box.SIMPLE)
    table.add_column("Pos", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Stars", style="yellow")
    table.add_column("Ovr", justify="right", style="green")
    table.add_column("Pot", justify="right", style="magenta")
    table.add_column("Dur", justify="right", style="dim")
    
    if not commits:
        console.print("[dim]No recruits signed.[/dim]")
    else:
        for p in commits:
            stars = "★" * p.stars
            dur = p.attributes.get('durability', p.attributes.get('toughness', 'N/A'))
            
            table.add_row(
                p.position,
                p.full_name,
                stars,
                str(p.overall),
                str(p.potential),
                str(dur)
            )
        console.print(table)

def recruiting_hub(rankings_dict):
    """Main interactive hub for the recruiting season."""
    while True:
        console.clear()
        
        # Dashboard Header
        grid = Table.grid(expand=True)
        grid.add_column(justify="center")
        grid.add_row("[bold yellow]NATIONAL SIGNING DAY HUB[/bold yellow]")
        grid.add_row("[dim]Review the future stars of College Football[/dim]")
        
        console.print(Panel(grid, style="blue"))
        
        # Stats summary
        total_commits = sum(len(d['commits']) for d in rankings_dict.values())
        if rankings_dict:
            top_class_data = max(rankings_dict.items(), key=lambda x: x[1]['points'])
            top_class = top_class_data[0].name
        else:
            top_class = "N/A"
        
        console.print(f" Total Signees: [green]{total_commits}[/green] | #1 Class: [yellow]{top_class}[/yellow]\n")
        
        # Menu
        console.print("[1] National Recruiting Rankings")
        console.print("[2] Conference Rankings")
        console.print("[3] View Team Signing Class")
        console.print("[4] Class Star Breakdown")
        console.print("[5] [bold green]Advance Season[/bold green]")
        
        choice = Prompt.ask("\n[cyan]Select Option[/cyan]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            display_recruiting_rankings(rankings_dict)
        elif choice == "2":
            display_conference_rankings(rankings_dict)
            Prompt.ask("\n[dim]Press Enter to return...[/dim]")
        elif choice == "3":
            view_team_details(rankings_dict)
            Prompt.ask("\n[dim]Press Enter to return...[/dim]")
        elif choice == "4":
            display_star_breakdown(rankings_dict)
            Prompt.ask("\n[dim]Press Enter to return...[/dim]")
        elif choice == "5":
            break
