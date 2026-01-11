import sys
import time
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Local Imports
from config import console
from utils import repair_save_data, find_school_by_input
from logic import ensure_college_schedule, simulate_week
import views

# Import existing modules
from world_gen import generate_world
from league_manager import save_league, load_league, save_exists
from game_sim import GameSim
from season_manager import advance_season
from rankings import display_rankings, get_heisman_leaders
from coach_manager import view_coach_history
from transfer_portal import view_portal_hub
from news_manager import NewsManager  # Integration: Import NewsManager

# --- MAIN LOOP ---

def main():
    universe = None
    news_manager = None  # Integration: Variable to hold the manager instance
    context = "HS" 
    last_viewed_list = []
    last_schedule_list = []
    last_team_viewed = None # Track the School object of the last team viewed

    while True:
        if universe is None:
            views.draw_main_menu_dashboard(save_exists())
            choice = Prompt.ask("[cyan]Select Option[/cyan]", choices=["1", "2", "3"])
            
            if choice == "1":
                console.print("\n[green]Initializing Universe...[/green]")
                universe = generate_world(300)
                ensure_college_schedule(universe)
                
                # REPAIR CHECK
                repair_save_data(universe)
                
                # Integration: Initialize NewsManager
                news_manager = NewsManager(universe)
                
                save_league(universe)
            elif choice == "2":
                if save_exists():
                    universe = load_league()
                    ensure_college_schedule(universe)
                    
                    # REPAIR CHECK
                    repair_save_data(universe)
                    
                    # Integration: Initialize NewsManager with loaded universe
                    news_manager = NewsManager(universe)
                    
                else:
                    console.print("[red]No save found![/red]")
                    time.sleep(1)
            elif choice == "3": sys.exit()
        
        else:
            views.draw_season_dashboard(universe, context)
            cmd = console.input(f"\n[cyan]Dashboard Command:[/cyan] ").strip().lower()
            
            if cmd == "switch":
                context = "COLLEGE" if context == "HS" else "HS"
            
            elif cmd == "sim":
                simulate_week(universe)
                # Integration: Generate news after week sim
                if news_manager: 
                    news_manager.generate_weekly_news()
                
                save_league(universe)
                console.input("\n[dim]Press Enter to continue...[/dim]")

            elif cmd == "sim season":
                if universe.current_week > 16:
                    console.print("[red]Season is already over. Proceed to next season.[/red]")
                    time.sleep(1)
                else:
                    confirm = Prompt.ask("[bold red]Simulate REMAINDER of season and enter Recruiting?[/bold red]", choices=["y", "n"])
                    if confirm == "y":
                        # Loop until season end (Week 16 is final week logic, which increments to 17)
                        while universe.current_week <= 16:
                            simulate_week(universe)
                            # Integration: Generate news during loop
                            if news_manager: 
                                news_manager.generate_weekly_news()
                        
                        console.print("\n[bold green]SEASON COMPLETE! Entering Offseason...[/bold green]")
                        time.sleep(1)
                        
                        # Trigger Advance Season -> Recruiting Hub
                        advance_season(universe)
                        ensure_college_schedule(universe)
                        save_league(universe)
                        console.print(f"[bold green]Welcome to {universe.year}![/bold green]")
                        time.sleep(1)

            # --- CUSTOM MULTI-YEAR SIMULATION ---
            elif cmd.startswith("sim ") and len(cmd.split()) > 1 and cmd.split()[1].isdigit():
                years = int(cmd.split()[1])
                confirm = Prompt.ask(f"[bold red]Simulate next {years} seasons fully? (Bypasses interactive recruiting)[/bold red]", choices=["y", "n"])
                if confirm == "y":
                    target_year = universe.year + years
                    
                    # Rich Progress Bar for multi-year sim
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("{task.percentage:>3.0f}%"),
                    ) as progress:
                        season_task = progress.add_task(f"[green]Simulating {years} Seasons...", total=years)
                        
                        while universe.year < target_year:
                            # Update description
                            progress.update(season_task, description=f"[green]Simulating {universe.year}...")
                            
                            # 1. Finish Current Season (Sim Weeks)
                            while universe.current_week <= 16:
                                simulate_week(universe, silent=True)
                                # Integration: Generate news (keeps state updated even if not read)
                                if news_manager: 
                                    news_manager.generate_weekly_news()
                            
                            # 2. Advance (Recruiting/Portal) - SILENT MODE
                            advance_season(universe, interactive=False, silent=True)
                            ensure_college_schedule(universe)
                            save_league(universe)
                            
                            progress.advance(season_task)
                    
                    console.print(f"\n[bold green]Simulation Complete! Welcome to {universe.year}.[/bold green]")
                    time.sleep(2)

            elif cmd.startswith("schedule") or cmd.startswith("sched"):
                parts = cmd.split()
                # Check for "team" keyword in parts[1]
                if len(parts) > 1 and parts[1].lower() == "team":
                    try:
                        # Reconstruct the query string from remaining parts
                        # e.g., "sched team notre dame" -> "notre dame"
                        if len(parts) < 3:
                            console.print("[red]Usage: sched team <Name/ID>[/red]")
                        else:
                            query = " ".join(parts[2:])
                            school = find_school_by_input(universe, context, query)
                            if school:
                                views.display_team_schedule(school)
                                console.input("\n[dim]Press Enter...[/dim]")
                    except Exception:
                        console.print("[red]Error loading team schedule.[/red]")
                else:
                    target = universe.current_week
                    if len(parts) > 1 and parts[1].isdigit(): 
                        target = int(parts[1])
                    
                    active = universe.high_school_league if context == "HS" else universe.college_league
                    last_schedule_list = views.display_weekly_schedule(universe, target, active)
                    console.input("\n[dim]Press Enter to continue...[/dim]")

            elif cmd.startswith("watch"):
                if not last_schedule_list:
                    console.print("[red]View schedule first.[/red]")
                    time.sleep(1)
                else:
                    try:
                        idx = int(cmd.split()[1]) - 1
                        if 0 <= idx < len(last_schedule_list):
                            g = last_schedule_list[idx]
                            if g.played:
                                console.print("Game already played.")
                            else:
                                g.slow_mode = True
                                # PASS CONSOLE HERE TO ENABLE RICH UI IN GAME SIM
                                sim = GameSim(g, console=console)
                                sim.play_game()
                                # Stats commit
                                g.home_team.points_for += g.home_score; g.home_team.points_against += g.away_score
                                g.away_team.points_for += g.away_score; g.away_team.points_against += g.home_score
                                if g.home_score > g.away_score: g.home_team.wins += 1; g.away_team.losses += 1
                                else: g.away_team.wins += 1; g.home_team.losses += 1
                                console.input("[dim]Press Enter to return...[/dim]")
                    except: pass

            elif cmd == "view":
                active = universe.high_school_league if context == "HS" else universe.college_league
                
                # --- UPDATED TEAM LIST LOGIC ---
                table = views.display_team_list(active)
                
                with console.pager():
                    console.print(table)
                
                last_viewed_list = active

            elif cmd.startswith("team"):
                try:
                    # Strip "team " from command
                    if len(cmd) <= 5:
                        console.print("[red]Usage: team <Name/ID>[/red]")
                        time.sleep(1)
                        continue
                    
                    query = cmd[5:].strip() # "team " is 5 chars
                    school = find_school_by_input(universe, context, query)
                    
                    if school:
                        last_team_viewed = school
                        # Just used for player logic if user types "player 1" afterwards
                        # We reconstruct a roster list or something similar?
                        # Actually, last_viewed_list is usually a LIST.
                        # So we might want to just set it to [school] or the roster?
                        # Let's leave last_viewed_list alone or set it to school's roster?
                        # Original code set it to "display_team_detail" return (sorted roster)
                        
                        last_viewed_list = views.display_team_detail(school)
                        console.input("\n[dim]Press Enter...[/dim]")
                
                except Exception as e:
                    console.print(f"[red]Error loading team: {e}[/red]")
                    time.sleep(2)
            
            # --- UPDATED HISTORY COMMAND ---
            elif cmd.startswith("history"):
                parts = cmd.split()
                # Case 1: "history" alone -> Show League History (Champs/Heisman)
                if len(parts) == 1:
                    views.display_league_history(universe)
                    console.input("\n[dim]Press Enter...[/dim]")
                
                # Case 2: "history <Name>" -> Show Team History
                else:
                    try:
                        query = " ".join(parts[1:]).strip()
                        school = find_school_by_input(universe, context, query)
                        if school:
                            views.display_team_history(school)
                            console.input("\n[dim]Press Enter...[/dim]")
                    except:
                        console.print("[red]Invalid selection.[/red]")
                        time.sleep(1)

            elif cmd == "log":
                 if last_team_viewed:
                     # Toggle logging - SAFE TOGGLE
                     current_val = getattr(last_team_viewed, 'logging_enabled', False)
                     last_team_viewed.logging_enabled = not current_val
                     
                     status = "ENABLED" if last_team_viewed.logging_enabled else "DISABLED"
                     color = "green" if last_team_viewed.logging_enabled else "red"
                     
                     console.print(f"[bold {color}]Logging {status} for {last_team_viewed.name}[/bold {color}]")
                     
                     # Redisplay the header to reflect change
                     views.display_team_detail(last_team_viewed)
                     console.input("\n[dim]Press Enter...[/dim]")
                 else:
                     console.print("[red]No team selected. View a team first.[/red]")
                     time.sleep(1)

            elif cmd.startswith("roster"):
                try:
                    # Check if arg provided
                    if len(cmd) > 7:
                        query = cmd[7:].strip()
                        school = find_school_by_input(universe, context, query)
                    else:
                        # Fallback to last viewed if available?
                        # Original logic required an ID.
                        console.print("[red]Usage: roster <Name/ID>[/red]")
                        school = None

                    if school:
                        while True:
                            console.clear()
                            # Display and get list
                            roster_list = views.display_full_roster(school)
                            last_viewed_list = roster_list # Update last viewed list context for manual "player <ID>" cmd
                            
                            p_choice = Prompt.ask("\n[cyan]Enter Player ID for details (or Enter to exit)[/cyan]", default="exit")
                            
                            if p_choice == "exit" or p_choice == "":
                                break
                                
                            if p_choice.isdigit():
                                p_idx = int(p_choice) - 1
                                if 0 <= p_idx < len(roster_list):
                                    console.clear()
                                    views.display_player_card(roster_list[p_idx])
                                    console.input("\n[dim]Press Enter to return...[/dim]")
                except: pass

            elif cmd.startswith("player"):
                try:
                    idx = int(cmd.split()[1]) - 1
                    if last_viewed_list and hasattr(last_viewed_list[0], 'position'):
                        views.display_player_card(last_viewed_list[idx])
                        console.input("\n[dim]Press Enter...[/dim]")
                    else:
                        console.print("[red]View a roster first.[/red]")
                        time.sleep(1)
                except: pass
            
            elif cmd == "rankings" and context == "COLLEGE":
                active = universe.high_school_league if context == "HS" else universe.college_league
                # display_rankings is imported. If it uses basic print, it won't look "Rich"
                # but it will still work. 
                display_rankings(active, universe.current_week)
                console.input("\n[dim]Press Enter...[/dim]")

            # --- NEW HEISMAN COMMAND ---
            elif cmd == "heisman" and context == "COLLEGE":
                leaders = get_heisman_leaders(universe.college_league)
                views.display_heisman_race(leaders)
                console.input("\n[dim]Press Enter...[/dim]")

            # --- NEW DYNASTY RECORDS COMMAND ---
            elif cmd == "records" or cmd == "dynasty":
                if context == "COLLEGE":
                    views.display_dynasty_rankings(universe.college_league)
                else:
                    console.print("[dim]Dynasty records only available for College context.[/dim]")
                console.input("\n[dim]Press Enter...[/dim]")

            elif cmd == "standings":
                active = universe.high_school_league if context == "HS" else universe.college_league
                views.display_standings(active, context)
                console.input("\n[dim]Press Enter...[/dim]")

            elif cmd == "recruits" and context == "COLLEGE":
                last_viewed_list = views.display_recruits(universe)
                console.input("\n[dim]Press Enter...[/dim]")
                
            # --- NEW COACH COMMAND ---
            elif cmd == "coaches":
                view_coach_history(universe)

            # --- NEW PORTAL COMMAND ---
            elif cmd == "portal" and context == "COLLEGE":
                view_portal_hub(universe)
            
            # --- INTEGRATED NEWS COMMAND ---
            elif cmd == "news" and context == "COLLEGE":
                if news_manager:
                    news_manager.view_dashboard()
                else:
                    console.print("[red]News manager not initialized. Try reloading save.[/red]")
                    time.sleep(1)
                
            elif cmd == "bracket" and context == "HS":
                views.display_bracket(universe)
                console.input()

            elif cmd == "injuries":
                active = universe.high_school_league if context == "HS" else universe.college_league
                views.display_injury_report(active, context)
                console.input()
                
            elif cmd == "export logs":
                filename = "roster_debug_log.txt"
                with open(filename, "w") as f:
                    f.write("ROSTER DEBUG LOGS\n")
                    f.write("=================\n\n")
                    all_schools = universe.college_league + universe.high_school_league
                    for s in all_schools:
                        if hasattr(s, 'roster_log') and s.roster_log:
                            f.write(f"--- {s.name} ---\n")
                            for entry in s.roster_log:
                                f.write(entry + "\n")
                            f.write("\n")
                console.print(f"[green]Logs successfully exported to {filename}[/green]")
                time.sleep(1)

            elif cmd.startswith("toggle log"):
                # Fallback specific ID command - SAFE TOGGLE
                try:
                    # Parts: "toggle", "log", <Query>
                    if len(cmd) > 11:
                         query = cmd[11:].strip()
                         school = find_school_by_input(universe, context, query)
                         if school:
                            current_val = getattr(school, 'logging_enabled', False)
                            school.logging_enabled = not current_val
                            
                            status = "ENABLED" if school.logging_enabled else "DISABLED"
                            console.print(f"[yellow]Roster logging {status} for {school.name}.[/yellow]")
                            time.sleep(1)
                except:
                    console.print("[red]Invalid selection.[/red]")

            elif cmd == "new season" or cmd == "next season":
                if universe.current_week > 16:
                    confirm = Prompt.ask("[yellow]Advance to next season?[/yellow]", choices=["y", "n"])
                    if confirm == 'y':
                        advance_season(universe)
                        ensure_college_schedule(universe)
                        save_league(universe)
                        console.print(f"[bold green]Welcome to {universe.year}![/bold green]")
                        time.sleep(1)
                else:
                    console.print("[red]Finish the season first.[/red]")
                    time.sleep(1)

            elif cmd == "save":
                save_league(universe)
                time.sleep(1)

            elif cmd == "exit":
                save_league(universe)
                sys.exit()

if __name__ == "__main__":
    main()