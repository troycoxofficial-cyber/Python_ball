
from rich.panel import Panel
from config import console
from game_sim import GameSim
from recruiting import process_weekly_recruiting
from scheduler import (
    generate_schedule,
    generate_playoffs_round_of_16, 
    generate_next_playoff_round, 
    generate_conference_championships,
    generate_cfp_round1,  
    generate_cfp_qf,      
    generate_cfp_semis,   
    generate_cfp_final    
)

# --- HELPER: Schedule Merging ---
def ensure_college_schedule(universe):
    if universe.college_league and not any(g.home_team in universe.college_league for g in universe.schedule.get(1, [])):
        console.print("[dim italic]System: Generating inaugural College Schedule...[/dim italic]")
        college_sched = generate_schedule(universe.college_league)
        for week, games in college_sched.items():
            if week not in universe.schedule: universe.schedule[week] = []
            universe.schedule[week].extend(games)

def process_weekly_injuries(universe, silent=False):
    if not silent:
        console.print(" [dim]- Processing Medical Reports...[/dim]")
    for league in [universe.high_school_league, universe.college_league]:
        for team in league:
            for player in team.roster:
                player.recover_health_weekly()

def simulate_week(universe, silent=False):
    week = universe.current_week
    schedule = universe.schedule
    
    if week not in schedule:
        if week > 16:
            if not silent:
                console.print("[red]Season Complete.[/red]")
            return
        if not silent:
            console.print(f"No games Week {week}.")
        return

    if not silent:
        console.print(f"\n[green]>>> SIMULATING WEEK {week}...[/green]")
    
    games = schedule.get(week, [])
    games.sort(key=lambda x: x.export_log)
    
    sim_count = 0
    
    # Inner Sim Function
    def _run_sim_loop():
        nonlocal sim_count
        for game in games:
            if game.played: continue
            
            # PASS CONSOLE TO GAME SIM for consistent output
            sim = GameSim(game, console=console)
            sim.play_game()
            
            # Stats Aggregation
            game.home_team.points_for += game.home_score
            game.home_team.points_against += game.away_score
            game.away_team.points_for += game.away_score
            game.away_team.points_against += game.home_score
            
            if game.home_score > game.away_score:
                game.home_team.wins += 1; game.away_team.losses += 1
                winner = game.home_team
            else:
                game.away_team.wins += 1; game.home_team.losses += 1
                winner = game.away_team
            
            # --- CHAMPIONSHIP LOGIC ---
            if game.title:
                if "Conference Championship" in game.title:
                    winner.conf_champ = True
                elif "National Championship" in game.title:
                    winner.nat_champ = True
            
            sim_count += 1
            if (game.export_log or game.title) and not silent:
                 console.print(f" FINAL: {game.away_team.name} {game.away_score} - {game.home_team.name} {game.home_score} [{game.title}]")

    # Run Loop (With or Without Spinner)
    if not silent:
        with console.status("[bold green]Simulating games...[/bold green]", spinner="dots"):
            _run_sim_loop()
        console.print(f" [dim]Simulated {sim_count} games.[/dim]")
    else:
        _run_sim_loop()

    process_weekly_injuries(universe, silent=silent)
    
    # --- WEEKLY RECRUITING UPDATE ---
    if universe.college_league:
        new_commits = process_weekly_recruiting(universe)
        if new_commits > 0 and not silent:
            console.print(f" [bold yellow]Recruiting:[/bold yellow] {new_commits} high school seniors committed this week!")
    
    # Logic copied from original main.py
    if week == 12:
        if not silent:
            console.print(" [bold cyan][System] Generating HS Bracket & Conf Championships...[/bold cyan]")
        universe.schedule[13] = generate_playoffs_round_of_16(universe.high_school_league, 13)
        if universe.college_league:
            universe.schedule[13].extend(generate_conference_championships(universe.college_league, 13))
            
    elif week == 13:
        nr = generate_next_playoff_round(universe.schedule, week)
        if nr: universe.schedule[14] = nr
        if universe.college_league:
            r1, seeds = generate_cfp_round1(universe.college_league, 14)
            universe.cfp_seeds = seeds
            if 14 not in universe.schedule: universe.schedule[14] = []
            universe.schedule[14].extend(r1)

    elif week == 14:
        nr = generate_next_playoff_round(universe.schedule, week)
        if nr: universe.schedule[15] = nr
        if universe.college_league and hasattr(universe, 'cfp_seeds'):
            qf = generate_cfp_qf(universe.schedule, universe.cfp_seeds, 15)
            if 15 not in universe.schedule: universe.schedule[15] = []
            universe.schedule[15].extend(qf)

    elif week == 15:
        nr = generate_next_playoff_round(universe.schedule, week)
        if nr: universe.schedule[16] = nr
        if universe.college_league:
            sf = generate_cfp_semis(universe.schedule, 16)
            if 16 not in universe.schedule: universe.schedule[16] = []
            universe.schedule[16].extend(sf)

    elif week == 16:
        if universe.college_league:
            finals = generate_cfp_final(universe.schedule, 16)
            if finals:
                f = finals[0]
                universe.schedule[16].append(f)
                if not silent:
                    console.print(Panel(f"[bold yellow]NATIONAL CHAMPIONSHIP SET: {f.away_team.name} vs {f.home_team.name}[/bold yellow]", style="red"))
                
                # Auto-Sim final (Pass console)
                sim = GameSim(f, console=console)
                sim.play_game()
                # Manually set nat_champ here since it's outside simulate_week loop
                f.winner.nat_champ = True 
                
                if not silent:
                    console.print(f" [bold magenta]*** CHAMPION: {f.winner.name.upper()} ***[/bold magenta]")

    universe.current_week += 1
