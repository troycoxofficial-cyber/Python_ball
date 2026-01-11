import sys
import random
from rich.prompt import Prompt
from config import console

def repair_save_data(universe):
    """Fixes potential data corruption from previous bugs."""
    count = 0
    all_teams = universe.high_school_league + universe.college_league
    for team in all_teams:
        if not hasattr(team, 'nat_champ'): team.nat_champ = False
        if not hasattr(team, 'conf_champ'): team.conf_champ = False
        if not hasattr(team, 'bowl_win'): team.bowl_win = False
        if not hasattr(team, 'team_history'): team.team_history = []
        
        for player in team.roster:
            # Check if stats dict is empty or missing keys
            if not player.stats or "tackles" not in player.stats:
                player.reset_stats()
                count += 1
            # Ensure loyalty attribute exists for old saves
            if not hasattr(player, 'loyalty'):
                player.loyalty = random.randint(0, 100)
                count += 1
                
    if count > 0:
        console.print(f"[yellow]System: Repaired {count} player(s) with corrupted stats/data.[/yellow]")

def find_school_by_input(universe, context, query):
    """
    Locates a school based on user input (ID integer OR Name string).
    Returns the School object or None.
    """
    active_league = universe.high_school_league if context == "HS" else universe.college_league
    
    # 1. Try ID (Integer)
    if query.isdigit():
        idx = int(query) - 1
        if 0 <= idx < len(active_league):
            return active_league[idx]
        else:
            console.print(f"[red]Invalid ID. Range: 1-{len(active_league)}[/red]")
            return None
            
    # 2. Try Name Search
    search_str = query.lower()
    matches = [s for s in active_league if search_str in s.name.lower()]
    
    if not matches:
        console.print(f"[red]No team found matching '{query}'.[/red]")
        return None
    
    if len(matches) == 1:
        return matches[0]
        
    # 3. Disambiguation (Multiple matches)
    console.print(f"[yellow]Multiple matches found for '{query}':[/yellow]")
    for i, m in enumerate(matches):
        console.print(f"[{i+1}] {m.name} [dim]({m.record_str()})[/dim]")
    
    choice = Prompt.ask("Select Team ID from list", choices=[str(i+1) for i in range(len(matches))])
    return matches[int(choice)-1]