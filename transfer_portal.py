import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def process_portal_entries(universe, silent=False):
    """
    Iterates through all college teams and determines which players enter the transfer portal.
    Returns a list of players in the portal.
    """
    portal_pool = []
    
    if not silent:
        console.print("\n[bold red]=== THE TRANSFER PORTAL IS OPEN ===[/bold red]")
        console.print("[dim]Players are making business decisions...[/dim]\n")
    
    total_entered = 0
    
    for school in universe.college_league:
        # 1. Update Depth Chart to know where players stand
        school.set_depth_chart()
        
        # 2. Identify Departures
        departing_players = []
        new_roster = []
        
        # Calculate rank for each player
        rank_map = {}
        for pos, players in school.depth_chart.items():
            for i, p in enumerate(players):
                rank_map[p.id] = i + 1
        
        for player in school.roster:
            # Skip graduating seniors (handled elsewhere) or already transferred
            if player.eligibility_year >= 4:
                new_roster.append(player)
                continue
                
            rank = rank_map.get(player.id, 99)
            
            # CHECK TRANSFER INTENT
            # Pass the SCHOOL object so traits can check coach stats
            wants_to_leave, reason = player.check_transfer_intent(
                school=school,
                depth_chart_rank=rank
            )
            
            if wants_to_leave:
                # CRITICAL: Archive the season stats BEFORE they leave the team
                # This ensures the year they played is recorded with their stats/record
                player.archive_season(school.name, school.record_str(), universe.year)

                # PLAYER LEAVES
                departing_players.append((player, reason))
                portal_pool.append(player)
                
                # Archive the Departure Event
                player.history.append({
                    "year": universe.year,
                    "event": "Transfer Portal",
                    "team": school.name,
                    "note": reason
                })
                total_entered += 1
            else:
                new_roster.append(player)
        
        # 3. Update School Roster
        school.roster = new_roster
        
        # 4. Log Chaos
        if departing_players and not silent:
            # Sort by OVR for display impact
            departing_players.sort(key=lambda x: x[0].overall, reverse=True)
            
            # Only show significant departures (Starters or high OVR) to keep log readable
            notable = [x for x in departing_players if x[0].overall >= 75]
            if notable:
                console.print(f"[bold white]{school.name}[/bold white] loses {len(departing_players)} players.")
                for p, reason in notable[:3]: # Show top 3
                    console.print(f"  -> [red]Leaves:[/red] {p.position} {p.full_name} ({p.overall} OVR) - [italic]{reason}[/italic]")

    if not silent:
        console.print(f"\n[bold yellow]Total Players in Portal: {total_entered}[/bold yellow]")
    
    return portal_pool

def resolve_portal_destinations(universe, portal_pool, silent=False):
    """
    Finds new homes for players in the portal pool.
    
    PHASE 1: STRATEGIC ACQUISITION (Teams only take Starters/Depth)
    PHASE 2: ROSTER MANAGEMENT (Teams cut to 55)
    PHASE 3: SECOND ROUND (Filling empty spots)
    """
    if not silent:
        console.print("\n[bold green]=== TRANSFER PORTAL RESOLUTION ===[/bold green]")
        console.print("[dim]The scramble for talent begins...[/dim]\n")
    
    ROSTER_LIMIT = 55
    
    # ---------------------------------------------------------
    # PHASE 1: STRATEGIC ACQUISITION
    # Teams are selective: Only take players who improve depth (Rank 2) or Start (Rank 1).
    # ---------------------------------------------------------
    if not silent:
        console.print("[bold cyan]--- Phase 1: Strategic Acquisition ---[/bold cyan]")
    
    # Sort pool by Overall (Better players get first pick)
    portal_pool.sort(key=lambda x: x.overall, reverse=True)
    
    round1_signed = 0
    still_looking = [] # Players who didn't sign in Round 1
    
    for player in portal_pool:
        best_school = None
        best_score = -1
        
        # Candidate list: 40 random schools
        candidate_schools = random.sample(universe.college_league, k=40)
        
        for school in candidate_schools:
            # 1. PRESTIGE CHECK (Gatekeeper)
            if player.stars >= 4 and school.prestige < 50:
                continue
            
            # 2. STRATEGIC DEPTH CHECK
            # Calculate where the player fits
            players_at_pos = [p for p in school.roster if p.position == player.position]
            
            # Include Incoming Recruits in this calculation to be truly strategic
            if hasattr(school, 'incoming_class'):
                players_at_pos.extend([p for p in school.incoming_class if p.position == player.position])
            
            players_at_pos.sort(key=lambda x: x.overall, reverse=True)
            
            my_rank = 1
            for p in players_at_pos:
                if p.overall >= player.overall:
                    my_rank += 1
            
            # SELECTIVITY: If I'm not a Starter (1) or Key Backup (2), the team isn't interested.
            if my_rank > 2:
                continue 
            
            score = 0
            score += school.prestige * 2.5
            
            if school.region == player.home_region:
                score += 50
            
            # Huge bonus for being a starter
            if my_rank == 1:
                score += 500 
            elif my_rank == 2:
                score += 150
            
            # Coach Traits
            coach_traits = getattr(school.coach, 'traits', [])
            if "Portal Shark" in coach_traits: score += 150
            if "Mercenary Hunter" in coach_traits and player.eligibility_year == 3: score += 200
            if "Pipeline: South" in coach_traits and player.home_region == "SOUTH": score += 100
            if "Pipeline: North" in coach_traits and player.home_region == "NORTH": score += 100
            if "Pipeline: West" in coach_traits and player.home_region == "WEST": score += 100

            score += random.randint(0, 100)
            
            if score > best_score:
                best_score = score
                best_school = school
        
        # Decision
        if best_school and best_score > 250:
            _sign_player(best_school, player, universe, "Round 1 Transfer", silent)
            round1_signed += 1
        else:
            still_looking.append(player)

    if not silent:
        console.print(f"[dim]Round 1 Complete. {round1_signed} impact players signed.[/dim]")

    # ---------------------------------------------------------
    # PHASE 2: ROSTER MANAGEMENT (CUTS)
    # Teams drop players to get under the limit of 55.
    # ---------------------------------------------------------
    if not silent:
        console.print("\n[bold red]--- Phase 2: Roster Cuts (Limit 55) ---[/bold red]")
    total_cuts = 0
    
    for school in universe.college_league:
        # Calculate Projected Roster
        # Existing Roster (minus Seniors) + Incoming Recruits
        projected_roster = []
        
        # 1. Recruits are safe
        if hasattr(school, 'incoming_class'):
            projected_roster.extend(school.incoming_class)
            
        # 2. Returning players
        returning_players = []
        for p in school.roster:
            # Skip seniors (they leave naturally)
            if p.eligibility_year >= 4:
                continue
            
            # Skip players we JUST signed in Round 1 (Event check)
            is_new_transfer = False
            if p.history and p.history[-1].get("year") == universe.year and "Transfer" in p.history[-1].get("event", ""):
                is_new_transfer = True
            
            if is_new_transfer:
                projected_roster.append(p)
            else:
                returning_players.append(p)
                projected_roster.append(p)
                
        # 3. Check Limit
        if len(projected_roster) > ROSTER_LIMIT:
            num_to_cut = len(projected_roster) - ROSTER_LIMIT
            
            # Sort returning players by Overall (Cut the weak)
            # Protect Fan Favorites?
            returning_players.sort(key=lambda x: x.overall)
            
            cuts_made = 0
            # Iterate through potential cuts
            # Note: We must remove from 'school.roster'
            for candidate in returning_players:
                if cuts_made >= num_to_cut:
                    break
                
                if "Fan Favorite" in candidate.traits:
                    continue # Saved by the fans
                
                # CUT LOGIC
                school.roster.remove(candidate)
                
                candidate.history.append({
                    "year": universe.year,
                    "event": "Cut",
                    "team": school.name,
                    "note": "Roster Limit Casualty"
                })
                
                # Add to pool for Round 2
                still_looking.append(candidate)
                
                if getattr(school, 'logging_enabled', False):
                    school.log_event(universe.year, f"CUT: {candidate.full_name} ({candidate.overall}) to meet roster limit.")
                
                cuts_made += 1
                total_cuts += 1
    
    if not silent:
        console.print(f"[dim]Teams trimmed rosters. {total_cuts} players released back to pool.[/dim]")

    # ---------------------------------------------------------
    # PHASE 3: SECOND ROUND (LEFTOVERS)
    # Filling empty spots with remaining players.
    # ---------------------------------------------------------
    if not silent:
        console.print("\n[bold yellow]--- Phase 3: Filling Open Spots ---[/bold yellow]")
    
    # Re-sort pool (includes cuts)
    still_looking.sort(key=lambda x: x.overall, reverse=True)
    
    round2_signed = 0
    retired_count = 0
    
    for player in still_looking:
        best_school = None
        best_score = -1
        
        candidate_schools = random.sample(universe.college_league, k=20)
        
        for school in candidate_schools:
            # 1. SPACE CHECK
            # Recalculate size (simplified)
            current_size = len([p for p in school.roster if p.eligibility_year < 4])
            if hasattr(school, 'incoming_class'): current_size += len(school.incoming_class)
            
            if current_size >= ROSTER_LIMIT:
                continue # Full
            
            # 2. NEED CHECK
            # In Round 2, teams just want bodies, but prefer higher OVR
            score = school.prestige
            if school.region == player.home_region: score += 50
            
            # Random 'Need' factor / Fit
            score += random.randint(0, 50)
            
            if score > best_score:
                best_score = score
                best_school = school
        
        if best_school and best_score > 50: # Low bar for Round 2
            _sign_player(best_school, player, universe, "Round 2 Depth", silent)
            round2_signed += 1
        else:
            retired_count += 1
            
    if not silent:
        console.print(f"[dim]Round 2 Complete. {round2_signed} found homes. {retired_count} retired/JuCo.[/dim]")

def _sign_player(school, player, universe, note, silent=False):
    player.context = "COLLEGE"
    school.roster.append(player)
    player.history.append({
        "year": universe.year,
        "event": "Transfer Destination",
        "team": school.name,
        "note": note
    })
    
    if getattr(school, 'logging_enabled', False):
        school.log_event(universe.year, f"TRANSFER ADDED ({note}): {player.position} {player.full_name} ({player.overall})")
    
    # Log high profile moves
    if not silent and player.overall >= 80:
        console.print(f" [green]NEWS:[/green] {player.position} {player.full_name} ([bold]{player.overall}[/bold]) signs with [bold cyan]{school.name}[/bold cyan] ({note})")

def view_portal_hub(universe):
    """
    A view-only function to see recent portal activity.
    Since portal clears every offseason, we look at the 'history' logs of active players 
    or just display a generic message if it's mid-season.
    """
    console.print(Panel("[bold yellow]TRANSFER PORTAL HUB[/bold yellow]", style="blue"))
    console.print("The portal is most active during the offseason (Post-Sim).")
    console.print("Below are recent significant movements from the last window:\n")
    
    table = Table(box=box.SIMPLE)
    table.add_column("Player", style="bold")
    table.add_column("Pos", style="cyan")
    table.add_column("Ovr", justify="right")
    table.add_column("From", style="red")
    table.add_column("To", style="green")
    
    count = 0
    # Scan all players in college for recent transfer history
    for school in universe.college_league:
        for p in school.roster:
            if len(p.history) >= 2:
                # Check last two entries
                last = p.history[-1]
                prev = p.history[-2]
                
                if last.get("event") == "Transfer Destination" and last.get("year") == universe.year:
                    # Found a recent transfer
                    from_team = "Unknown"
                    for h in reversed(p.history[:-1]):
                        if h.get("event") == "Transfer Portal":
                            from_team = h.get("team")
                            break
                    
                    if p.overall >= 78: # Only show impact players
                        table.add_row(
                            p.full_name, 
                            p.position, 
                            str(p.overall), 
                            from_team, 
                            school.name
                        )
                        count += 1
    
    if count == 0:
        console.print("[dim]No significant active transfers found for this year yet.[/dim]")
    else:
        console.print(table)
    
    # Pause
    from rich.prompt import Prompt
    Prompt.ask("\n[dim]Press Enter to return...[/dim]")