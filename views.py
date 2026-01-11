
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.align import Align
from rich import box
from config import console
from coach_manager import get_coach_market_value

# --- DASHBOARD COMPONENTS ---

def draw_main_menu_dashboard(save_exists_flag):
    console.clear()
    
    title = Text("PYTHON-BALL 2026: DYNASTY MODE", style="bold yellow")
    subtitle = Text("The Ultimate Text-Based Football Simulation", style="dim white")
    
    menu_text = Text()
    menu_text.append("\n[1] ", style="green bold")
    menu_text.append("NEW CAREER     ", style="bold white")
    menu_text.append("Start a fresh universe\n", style="dim")
    
    if save_exists_flag:
        menu_text.append("[2] ", style="green bold")
        menu_text.append("LOAD CAREER    ", style="bold white")
        menu_text.append("Continue your legacy\n", style="dim")
    else:
        menu_text.append("[2] ", style="dim")
        menu_text.append("LOAD CAREER    ", style="dim")
        menu_text.append("(No Save File Found)\n", style="dim")
        
    menu_text.append("[3] ", style="red bold")
    menu_text.append("EXIT           ", style="bold white")
    menu_text.append("Quit to Desktop\n", style="dim")

    panel = Panel(
        Align.center(menu_text),
        title=title,
        subtitle=subtitle,
        border_style="cyan",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    console.print(panel)

def draw_season_dashboard(universe, context):
    console.clear()
    
    # Header Info
    league_name = "HIGH SCHOOL" if context == "HS" else "NCAA COLLEGE"
    team_count = len(universe.high_school_league) if context=='HS' else len(universe.college_league)
    
    # Top Grid
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_row(
        f"[bold cyan]YEAR:[/bold cyan] [yellow]{universe.year}[/yellow]",
        f"[bold cyan]WEEK:[/bold cyan] [green]{universe.current_week}[/green]",
        f"[bold cyan]TEAMS:[/bold cyan] [white]{team_count}[/white]"
    )
    
    header_panel = Panel(grid, title=f"[bold]{league_name} DASHBOARD[/bold]", border_style="cyan")
    console.print(header_panel)
    
    # Headlines
    ticker_text = Text()
    if universe.current_week == 1:
        ticker_text.append(" * Season Opener! All teams are 0-0.\n")
        ticker_text.append(f" * Experts predict a wild year in the {universe.high_school_league[0].region}.")
    elif universe.current_week >= 13:
        ticker_text.append(" * PLAYOFF MODE: The bracket is heating up!", style="yellow bold")
    else:
        prev_week = universe.current_week - 1
        games = universe.schedule.get(prev_week, [])
        if games:
            g = games[0] 
            res = f"{g.winner.name} def. {g.home_team.name if g.winner!=g.home_team else g.away_team.name}"
            ticker_text.append(f" * Last Week: {res}")
        else:
            ticker_text.append(" * Teams are preparing for the upcoming matchups.")
    
    # Portal Watch ticker
    if context == "COLLEGE":
        ticker_text.append("\n * PORTAL WATCH: Rumors are swirling about unhappy QBs...", style="italic dim")

    console.print(Panel(ticker_text, title="LATEST HEADLINES", border_style="white", padding=(0, 1)))
    
    # Actions Menu
    actions_table = Table(box=box.SIMPLE, show_header=False, expand=True)
    actions_table.add_column("Command", style="yellow bold", width=12)
    actions_table.add_column("Description", style="white")
    actions_table.add_column("Command", style="yellow bold", width=12)
    actions_table.add_column("Description", style="white")

    actions_table.add_row("sim", "Simulate Week", "view", "List Teams")
    actions_table.add_row("schedule", "View Matchups", "standings", "League Table")
    actions_table.add_row("switch", "Change League", "injuries", "Medical Report")
    
    if context == "COLLEGE":
        actions_table.add_row("rankings", "Top 25 Poll", "recruits", "Recruiting Board")
        actions_table.add_row("coaches", "Coach Database", "portal", "Transfer Portal")
    elif context == "HS":
        actions_table.add_row("bracket", "Playoff Tree", "", "")
        
    # Sim Season option (available if season isn't over)
    if universe.current_week <= 16:
        actions_table.add_row("sim season", "[bold red]Sim Entire Season[/bold red]", "sim 5", "[bold magenta]Sim 5 Seasons[/bold magenta]")
    else:
        actions_table.add_row("new season", "[green]Start Next Year[/green]", "sim 5", "[bold magenta]Sim 5 Seasons[/bold magenta]")
    
    actions_table.add_row("export logs", "[dim]Save Roster Debug Logs[/dim]", "", "")

    console.print(Panel(actions_table, title="ACTIONS", border_style="blue"))
    
    # --- UPDATED FOOTER INSTRUCTIONS ---
    console.print("[dim]Commands: [bold cyan]team <Name>[/bold cyan] View Detailed Team Info | [bold cyan]view[/bold cyan] List All Teams | [bold cyan]history <Name>[/bold cyan] Team History[/dim]", justify="center")

# --- DETAILED DISPLAYS ---

def display_team_list(schools):
    """Generates a rich Table of all teams matching the program's style."""
    table = Table(title="LEAGUE TEAMS", box=box.SIMPLE_HEAD, expand=True)
    table.add_column("ID", justify="right", style="dim", width=4)
    table.add_column("School", style="bold white")
    table.add_column("Conference/Region", style="cyan")
    table.add_column("Record", justify="center", style="yellow")
    table.add_column("Ovr", justify="center", style="green")
    table.add_column("Prestige", justify="center", style="magenta")
    
    for i, s in enumerate(schools):
        # Handle cases where Prestige might be missing in HS context
        prestige = str(getattr(s, 'prestige', '-'))
        ovr = str(getattr(s, 'team_overall', '-'))
        
        table.add_row(
            str(i+1),
            s.name,
            s.region,
            s.record_str(),
            ovr,
            prestige
        )
    return table

def display_player_history(player):
    """Displays the year-by-year history of a player."""
    
    if not player.history:
        console.print(Panel("[dim]No career history recorded yet (History updates at end of season).[/dim]", title="CAREER HISTORY", border_style="dim"))
        return

    table = Table(title=f"CAREER HISTORY: {player.full_name}", box=box.SIMPLE, expand=True, title_style="bold yellow")
    table.add_column("Year", style="yellow", width=6)
    table.add_column("Class", style="cyan", width=6)
    table.add_column("Team", style="bold white")
    table.add_column("Ovr", justify="right", style="green")
    table.add_column("Record", justify="center", style="dim")
    table.add_column("Stats Summary", style="white")

    for entry in player.history:
        # Check for Special Events (Recruited, Walk-on) that don't have standard stats
        if "event" in entry:
            event = entry["event"]
            year = entry.get("year", "-")
            if event == "Recruited":
                by_team = entry.get("by", "Unknown")
                stars = entry.get("stars", 0)
                star_str = "★" * stars
                table.add_row(
                    str(year), "", 
                    f"[bold blue]SIGNED NLI -> {by_team}[/bold blue]", 
                    "", "", 
                    f"[italic blue]Rated {star_str} Prospect[/italic blue]"
                )
            elif event == "Walk-on":
                team = entry.get("team", "Unknown")
                table.add_row(str(year), "", f"[dim]Joined {team} (Walk-on)[/dim]", "", "", "")
            elif event == "Transfer Portal":
                team = entry.get("team", "Unknown")
                reason = entry.get("note", "Unknown")
                table.add_row(
                    str(year), "",
                    f"[bold red]ENTERED PORTAL ({team})[/bold red]",
                    "", "",
                    f"[italic red]Reason: {reason}[/italic red]"
                )
            elif event == "Transfer Destination":
                team = entry.get("team", "Unknown")
                table.add_row(
                    str(year), "",
                    f"[bold green]TRANSFERRED TO {team}[/bold green]",
                    "", "",
                    "[italic green]Eligible Immediately[/italic green]"
                )
        else:
            # Standard Season Log
            stats_str = player.get_stat_summary(entry.get("stats", {}))
            
            table.add_row(
                str(entry.get("year", "-")),
                entry.get("year_class", "-"),
                entry.get("team", "Free Agent"),
                str(entry.get("overall", "-")),
                entry.get("record", "-"),
                stats_str
            )
    
    console.print(table)

def display_player_card(player):
    # Header
    console.print(f"\n[bold white on blue] {player.full_name.upper()} [/bold white on blue]", justify="center")
    
    # Main Info Table
    info_table = Table(show_header=False, box=box.ROUNDED, expand=True)
    info_table.add_column("Label", style="cyan")
    info_table.add_column("Value", style="bold white")
    info_table.add_column("Label", style="cyan")
    info_table.add_column("Value", style="bold white")
    
    stars = "[yellow]" + ("★" * player.stars) + "[/yellow]"
    ovr_color = "green" if player.overall >= 80 else ("yellow" if player.overall >= 60 else "white")
    pot_val = f"[magenta]{player.potential}[/magenta]" if player.potential > 80 else str(player.potential)
    
    # Display Loyalty
    loyalty_val = getattr(player, 'loyalty', 50)
    
    info_table.add_row("Position:", player.position, "Year:", player.year_str)
    info_table.add_row("Overall:", f"[{ovr_color}]{player.overall}[/{ovr_color}]", "Potential:", pot_val)
    info_table.add_row("Age:", str(getattr(player, 'age', '??')), "Stars:", stars)
    info_table.add_row("Loyalty:", str(loyalty_val), "", "")
    
    # Health Status
    h_status = "[green]HEALTHY[/green]" if player.weeks_injured == 0 else f"[red]INJURED ({player.injury_type})[/red]"
    info_table.add_row("Status:", h_status, "", "")
    
    console.print(info_table)
    
    # Attributes Grid
    attr_table = Table(title="Attributes", box=box.SIMPLE_HEAD, show_edge=False, expand=True)
    attr_table.add_column("Attr", style="dim")
    attr_table.add_column("Val", justify="right")
    attr_table.add_column("Attr", style="dim")
    attr_table.add_column("Val", justify="right")
    
    attrs = list(player.attributes.items())
    for i in range(0, len(attrs), 2):
        k1, v1 = attrs[i]
        c1 = "green" if v1 > 80 else "white"
        
        row_data = [k1, f"[{c1}]{v1}[/{c1}]"]
        
        if i + 1 < len(attrs):
            k2, v2 = attrs[i+1]
            c2 = "green" if v2 > 80 else "white"
            row_data.extend([k2, f"[{c2}]{v2}[/{c2}]"])
        else:
            row_data.extend(["", ""])
            
        attr_table.add_row(*row_data)
    
    console.print(Panel(attr_table, border_style="dim"))

    # Traits
    if player.traits:
        trait_str = ", ".join(player.traits)
        console.print(Panel(f"[yellow]{trait_str}[/yellow]", title="Traits / Intangibles", border_style="yellow"))
    else:
        console.print(Panel("[dim]No active traits.[/dim]", title="Traits / Intangibles"))

    # Stats Summary
    stat_line = player.get_stat_summary()
    console.print(Panel(stat_line, title="Current Season Stats", border_style="blue"))
    
    # History Table - ALWAYS Called now
    display_player_history(player)

def display_team_detail(school):
    console.print(Panel(f"[bold yellow]{school.name.upper()}[/bold yellow]", box=box.HEAVY))
    
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column()
    grid.add_column()
    grid.add_column()
    
    # --- Coach Info ---
    coach_name = "N/A"
    coach_arch = "N/A"
    coach_traits = "None"
    coach_support = "N/A"
    
    if hasattr(school, 'coach') and school.coach:
        coach_name = school.coach.full_name
        coach_arch = school.coach.development_archetype[:15]
        coach_support = str(school.coach.fan_support)
        if school.coach.traits:
            coach_traits = ", ".join(school.coach.traits)
    
    # --- Budget & Expectations ---
    budget_str = f"${getattr(school, 'budget', 0)/1_000_000:.1f}M"
    exp_str = getattr(school, 'expectations', "Unknown")

    grid.add_row(
        f"Record: [yellow]{school.record_str()}[/yellow]",
        f"Prestige: {school.prestige}",
        f"OVR: [bold]{school.team_overall}[/bold]"
    )
    grid.add_row(f"Budget: [green]{budget_str}[/green]", f"Expectation: [cyan]{exp_str}[/cyan]", "")
    grid.add_row("---", "---", "")
    
    # --- Coach Row ---
    support_color = "green"
    try:
        val = int(coach_support)
        if val < 50: support_color = "red"
        elif val < 75: support_color = "yellow"
    except:
        pass
        
    grid.add_row(f"Coach: {coach_name}", f"Style: {coach_arch}", f"Fan Support: [{support_color}]{coach_support}/100[/{support_color}]")
    grid.add_row(f"[italic]Traits: {coach_traits}[/italic]", "", "")
    
    console.print(grid)
    console.print()

    # Impact Players
    t = Table(title="IMPACT PLAYERS", box=box.SIMPLE, expand=True)
    t.add_column("Pos", style="cyan")
    t.add_column("Name", style="bold")
    t.add_column("Ovr", justify="right")
    t.add_column("Stars", style="yellow")
    t.add_column("Status")
    
    sorted_roster = sorted(school.roster, key=lambda x: x.overall, reverse=True)
    for p in sorted_roster[:3]:
        stars = "★" * p.stars
        inj = "[red][INJ][/red]" if p.weeks_injured > 0 else ""
        ovr_col = "green" if p.overall >= 80 else "white"
        t.add_row(p.position, p.full_name, f"[{ovr_col}]{p.overall}[/{ovr_col}]", stars, inj)
    
    console.print(t)
    
    console.print("[dim](Use 'roster <Name/ID>' for full roster, 'sched team <Name/ID>' for games)[/dim]")
    return sorted_roster

def display_team_history(school):
    console.clear()
    console.print(Panel(f"[bold yellow]{school.name.upper()} TEAM HISTORY[/bold yellow]", style="blue"))
    
    if not hasattr(school, 'team_history') or not school.team_history:
        console.print("[dim]No history recorded yet (History accumulates as seasons advance).[/dim]")
        return
        
    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column("Year", style="cyan", width=6)
    table.add_column("Head Coach", style="bold")
    table.add_column("Record", justify="center", width=8)
    table.add_column("PF", justify="right", style="green")
    table.add_column("PA", justify="right", style="red")
    table.add_column("Recruiting", justify="center", style="yellow")
    table.add_column("Result", style="magenta")
    table.add_column("Change", style="dim italic", width=20) 
    
    sorted_history = sorted(school.team_history, key=lambda x: x['year'], reverse=True)
    
    for entry in sorted_history:
        year = str(entry['year'])
        coach = entry['coach']
        record = f"{entry['wins']}-{entry['losses']}"
        pf = str(entry.get('pf', '-'))
        pa = str(entry.get('pa', '-'))
        rec_rank = str(entry.get('rec_rank', '-'))
        if rec_rank != '-': rec_rank = f"#{rec_rank}"
        result = entry.get('result', '-')
        
        note = entry.get('notes', "")
        if note:
             note = f"[{note}]"
        else:
             note = ""
        
        table.add_row(year, coach, record, pf, pa, rec_rank, result, note)
        
    console.print(table)

def display_full_roster(school):
    table = Table(title=f"{school.name.upper()} ROSTER", box=box.MINIMAL_DOUBLE_HEAD)
    
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Pos", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Ovr", justify="right")
    table.add_column("Yr")
    table.add_column("Status")

    pos_order = {"QB":0, "RB":1, "WR":2, "TE":3, "OL":4, "DL":5, "LB":6, "DB":7, "K":8, "P":9}
    
    sorted_roster = sorted(school.roster, key=lambda x: (pos_order.get(x.position, 99), -x.overall))
            
    for i, p in enumerate(sorted_roster):
        status = f"[red]Inj ({p.weeks_injured}w)[/red]" if p.weeks_injured > 0 else "[dim]OK[/dim]"
        ovr_col = "green" if p.overall >= 80 else "white"
        table.add_row(str(i+1), p.position, p.full_name, f"[{ovr_col}]{p.overall}[/{ovr_col}]", p.year_str, status)
    
    console.print(table)
    return sorted_roster

def display_weekly_schedule(universe, week, active_league):
    table = Table(title=f"WEEK {week} SCHEDULE", box=box.SIMPLE)
    table.add_column("ID", justify="right", style="yellow")
    table.add_column("Away", justify="right")
    table.add_column("@", justify="center", style="dim")
    table.add_column("Home", justify="left")
    table.add_column("Result/Info", style="cyan")
    
    all_games = universe.schedule.get(week, [])
    active_team_set = set(active_league)
    active_games = [g for g in all_games if g.home_team in active_team_set or g.away_team in active_team_set]

    if not active_games:
        console.print("[red]No games found for this league.[/red]")
        return []

    for i, g in enumerate(active_games):
        idx = str(i + 1)
        title = f" [yellow][{g.title}][/yellow]" if g.title else ""
        
        status = "Upcoming"
        if g.played:
            w_team = g.home_team if g.home_score > g.away_score else g.away_team
            status = f"[dim]Final: {g.away_score}-{g.home_score} ({w_team.name})[/dim]"
        
        table.add_row(idx, g.away_team.name, "@", g.home_team.name, status + title)

    console.print(table)
    console.print("Type '[yellow]watch <ID>[/yellow]' to spectate.")
    return active_games

def display_standings(schools, context):
    console.print(Panel(f"[bold]{context} STANDINGS[/bold]", style="cyan"))
    groups = {}
    for school in schools:
        if school.region not in groups: groups[school.region] = []
        groups[school.region].append(school)
        
    for group_name in sorted(groups.keys()):
        table = Table(title=f"::: {group_name.upper()} :::", box=box.SIMPLE, expand=True)
        table.add_column("Rk", style="dim", width=4)
        table.add_column("Team", style="bold")
        table.add_column("Rec", justify="center")
        table.add_column("PF", justify="right", style="green")
        table.add_column("PA", justify="right", style="red")
        table.add_column("Diff", justify="right")
        
        team_list = groups[group_name]
        team_list.sort(key=lambda s: (-s.wins, -(s.points_for - s.points_against)))
        
        for i, s in enumerate(team_list):
            diff = s.points_for - s.points_against
            diff_str = f"[green]+{diff}[/green]" if diff > 0 else f"[red]{diff}[/red]"
            table.add_row(str(i+1), s.name, s.record_str(), str(s.points_for), str(s.points_against), diff_str)
        
        console.print(table)
        console.print()

def display_injury_report(schools, context):
    table = Table(title=f"MEDICAL REPORT ({context})", box=box.HEAVY_HEAD, style="red")
    table.add_column("Team", style="white")
    table.add_column("Pos", style="cyan")
    table.add_column("Player", style="bold")
    table.add_column("Injury", style="red")
    table.add_column("Wks", justify="right")
    
    count = 0
    for school in schools:
        for p in school.roster:
            if p.weeks_injured > 0:
                table.add_row(school.name, p.position, p.full_name, p.injury_type, str(p.weeks_injured))
                count += 1
    
    if count == 0:
        console.print("[green]No active injuries reported.[/green]")
    else:
        console.print(table)

def display_team_schedule(school):
    table = Table(title=f"{school.name} Schedule", box=box.SIMPLE)
    table.add_column("Wk", justify="right")
    table.add_column("Opponent")
    table.add_column("Result")
    
    for game in school.schedule:
        opp = game.away_team if game.home_team == school else game.home_team
        loc = "vs" if game.home_team == school else "@"
        res = ""
        if game.played:
            ms = game.home_score if game.home_team == school else game.away_score
            os = game.away_score if game.home_team == school else game.home_score
            wl = "[green]W[/green]" if ms > os else "[red]L[/red]"
            res = f"({wl} {ms}-{os})"
        
        table.add_row(str(game.week), f"{loc} {opp.name}", res)
    console.print(table)

def display_bracket(universe):
    console.print("\n[bold cyan]=== PLAYOFF BRACKET ===[/bold cyan]")
    schedule = universe.schedule
    if 13 not in schedule:
        console.print("[dim]Bracket generated Week 13.[/dim]")
        return

    # Use a Tree for visualization
    bracket_tree = Tree("[bold yellow]Playoffs[/bold yellow]")
    
    # Just visualizing the Round of 16 / Conf Championships (Week 13)
    round_node = bracket_tree.add("[bold]Round 1 / Conf Champs[/bold]")
    for g in schedule.get(13, []):
        if not g.title: continue
        
        match_str = f"{g.away_team.name} vs {g.home_team.name}"
        if g.played:
            winner = g.winner.name
            match_str += f" -> [green]{winner}[/green]"
        else:
            match_str += " -> [dim]???[/dim]"
            
        round_node.add(Text.from_markup(f"{g.title}: {match_str}"))
        
    console.print(bracket_tree)

def display_recruits(universe):
    seniors = []
    for school in universe.high_school_league:
        for p in school.roster:
            if p.eligibility_year == 4: seniors.append((p, school.name))
    seniors.sort(key=lambda x: (getattr(x[0], 'recruit_rating', x[0].overall), x[0].overall), reverse=True)
    
    table = Table(title="TOP 50 RECRUITING BOARD", box=box.ROUNDED)
    table.add_column("Rk", justify="right")
    table.add_column("Stars", style="yellow")
    table.add_column("Name", style="bold")
    table.add_column("Pos", style="cyan")
    table.add_column("Ovr")
    table.add_column("Pot", style="magenta")
    table.add_column("High School")
    table.add_column("Committed", style="green bold") # NEW COLUMN
    
    for i, (p, school) in enumerate(seniors[:50]):
        stars = "★" * p.stars
        pot = str(p.potential)
        
        # Check Commitment Status
        commit_status = p.commitment if p.commitment else "-"
        
        table.add_row(str(i+1), stars, p.full_name, p.position, str(p.overall), pot, school, commit_status)
    
    console.print(table)
    return [x[0] for x in seniors[:50]]

def display_heisman_race(leaders):
    """Displays the current Heisman Trophy race."""
    console.clear()
    
    # Header
    grid = Table.grid(expand=True)
    grid.add_column(justify="center", ratio=1)
    grid.add_row("[bold yellow]HEISMAN WATCH[/bold yellow]")
    grid.add_row("[dim]The most outstanding player in college football[/dim]")
    console.print(Panel(grid, style="yellow"))

    if not leaders:
        console.print("[dim]No candidates have emerged yet (Check back later in the season).[/dim]")
        return

    table = Table(box=box.SIMPLE_HEAD, expand=True)
    table.add_column("Rk", style="cyan", width=4)
    table.add_column("Player", style="bold white")
    table.add_column("Team", style="white")
    table.add_column("Pos", style="dim", justify="center")
    table.add_column("Stats Summary", style="green")
    table.add_column("Score", justify="right", style="magenta")

    for i, (player, team, score) in enumerate(leaders):
        rank = i + 1
        stats = player.get_stat_summary()
        
        # Highlight the frontrunner
        rank_style = "bold yellow" if rank == 1 else "cyan"
        
        table.add_row(
            f"[{rank_style}]#{rank}[/{rank_style}]", 
            player.full_name, 
            team.name, 
            player.position, 
            stats, 
            str(score)
        )
    
    console.print(table)
    console.print("\n[dim]* Score is a projection based on team success and individual stats.[/dim]")

def display_league_history(universe):
    """Displays historical winners for Heisman and National Championships."""
    console.clear()
    console.print(Panel("[bold white]LEAGUE HISTORY[/bold white]", style="blue"))

    # --- CHAMPIONSHIP HISTORY ---
    console.print("\n[bold yellow]NATIONAL CHAMPIONSHIP HISTORY[/bold yellow]")
    if not universe.championship_history:
        console.print("[dim]No championships played yet.[/dim]")
    else:
        champ_table = Table(box=box.SIMPLE, expand=True)
        champ_table.add_column("Year", style="cyan", width=6)
        champ_table.add_column("Champion", style="bold green")
        champ_table.add_column("Runner-Up", style="white")
        champ_table.add_column("Score/Result", style="dim")

        # Sort by year descending
        sorted_champs = sorted(universe.championship_history, key=lambda x: x['year'], reverse=True)
        
        for entry in sorted_champs:
            champ_table.add_row(
                str(entry['year']),
                entry['champion'],
                entry['runner_up'],
                entry['score']
            )
        console.print(champ_table)

    # --- HEISMAN HISTORY ---
    console.print("\n[bold yellow]HEISMAN TROPHY HISTORY[/bold yellow]")
    if not universe.heisman_history:
        console.print("[dim]No Heisman trophies awarded yet.[/dim]")
    else:
        heisman_table = Table(box=box.SIMPLE, expand=True)
        heisman_table.add_column("Year", style="cyan", width=6)
        heisman_table.add_column("Winner", style="bold yellow")
        heisman_table.add_column("Team", style="white")
        heisman_table.add_column("Key Stats", style="dim")

        # Sort by year descending
        sorted_heisman = sorted(universe.heisman_history, key=lambda x: x['year'], reverse=True)

        for entry in sorted_heisman:
            heisman_table.add_row(
                str(entry['year']),
                entry['player'],
                entry['team'],
                entry['stats']
            )
        console.print(heisman_table)

def display_dynasty_rankings(schools):
    """Sorts teams by Championships, Playoff Appearances, and Prestige."""
    console.clear()
    console.print(Panel("[bold white]DYNASTY PROGRAM RANKINGS[/bold white]", style="magenta"))
    
    sorted_schools = sorted(schools, key=lambda s: (
        getattr(s, 'national_championships', 0),
        getattr(s, 'playoff_appearances', 0),
        getattr(s, 'top_25_finishes', 0),
        s.wins
    ), reverse=True)

    table = Table(box=box.HEAVY_HEAD, expand=True)
    table.add_column("Rk", style="dim", width=4)
    table.add_column("School", style="bold white")
    table.add_column("Nat Titles", justify="center", style="bold yellow")
    table.add_column("Playoffs", justify="center", style="cyan")
    table.add_column("Top 25", justify="center", style="green")
    table.add_column("Prestige", justify="center", style="dim")

    for i, school in enumerate(sorted_schools):
        # Only show relevant schools
        nat_titles = getattr(school, 'national_championships', 0)
        playoffs = getattr(school, 'playoff_appearances', 0)
        top25 = getattr(school, 'top_25_finishes', 0)
        
        if nat_titles == 0 and playoffs == 0 and top25 == 0:
            continue
            
        rank = i + 1
        
        title_str = f"[bold yellow]{nat_titles}[/bold yellow]" if nat_titles > 0 else "-"
        playoff_str = str(playoffs) if playoffs > 0 else "-"
        top25_str = str(top25) if top25 > 0 else "-"

        table.add_row(
            str(rank),
            school.name,
            title_str,
            playoff_str,
            top25_str,
            str(school.prestige)
        )

    console.print(table)
    console.print("[dim]* Ordered by Titles, then Playoff Appearances, then Top 25 Finishes.[/dim]")

def display_coach_profile(coach, current_school):
    console.clear()
    
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    
    c_name = coach.full_name if coach else "VACANT"
    c_age = str(coach.age) if coach else "-"
    c_tenure = str(coach.years_at_school) if coach else "-"
    c_arch = coach.development_archetype if coach else "-"
    c_sec = str(coach.fan_support) if coach else "-"
    
    # Financials
    c_sal = f"${coach.salary/1000000:.1f}M" if coach and coach.salary > 0 else "N/A"
    c_yrs = str(coach.contract_years) if coach else "-"
    
    # Estimate Value
    c_val = "-"
    if coach:
         mv = get_coach_market_value(coach)
         c_val = f"${mv/1_000_000:.2f}M"
    
    sec_color = "green"
    if coach and coach.fan_support < 50: sec_color = "yellow"
    if coach and coach.fan_support < 25: sec_color = "red"
    
    grid.add_row(f"[bold white]{c_name}[/bold white]", f"[cyan]{current_school.name}[/cyan]")
    grid.add_row(f"Age: {c_age} | Tenure: {c_tenure} yrs", f"Fan Support: [{sec_color}]{c_sec}/100[/{sec_color}]")
    grid.add_row(f"Salary: [green]{c_sal}[/green]", f"Contract Left: {c_yrs} yrs")
    grid.add_row(f"Est. Market Value: {c_val}", f"Loyalty: {coach.loyalty_rating if coach else '-'} / 10")
    grid.add_row(f"Archetype: {c_arch}", f"Alma Mater: {coach.alma_mater if coach and coach.alma_mater else 'N/A'}")
    
    console.print(Panel(grid, title="COACH PROFILE", style="blue"))
    
    if not coach: return
    
    console.print(f"\n[bold underline]Active Traits:[/bold underline]")
    if coach.traits:
        for t in coach.traits: console.print(f" - [bold]{t}[/bold]")
    else: console.print(" [dim]No active traits.[/dim]")
        
    table = Table(title="CAREER HISTORY", box=box.SIMPLE_HEAVY, expand=True)
    table.add_column("Year", style="cyan")
    table.add_column("Team", style="bold")
    table.add_column("Record", justify="center")
    table.add_column("Awards/Notes", style="yellow")
    
    history = getattr(coach, 'history', [])
    sorted_hist = sorted(history, key=lambda x: x['year'], reverse=True)
    
    if not sorted_hist:
         table.add_row("-", "-", "-", "[dim]No history recorded[/dim]")
    else:
        for entry in sorted_hist:
            awards_str = ", ".join(entry['awards']) if entry['awards'] else "-"
            table.add_row(str(entry['year']), entry['team'], entry['record'], awards_str)
        
    console.print(table)
    console.print(f"\n[italic dim]Career Totals: {coach.career_wins}-{coach.career_losses} | National Titles: {coach.championships}[/italic dim]")
