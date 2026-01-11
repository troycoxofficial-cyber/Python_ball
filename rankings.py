# --- HELPER: Colors (Duplicate of Main Theme for standalone use) ---
class Theme:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    BORDER = f"{CYAN}║{RESET}"
    
    @staticmethod
    def box_header(title, width=70):
        print(f"\n{Theme.CYAN}╔{'═'*(width-2)}╗{Theme.RESET}")
        print(f"{Theme.BORDER} {Theme.BOLD}{Theme.WHITE}{title.center(width-4)}{Theme.RESET} {Theme.BORDER}")
        print(f"{Theme.CYAN}╠{'═'*(width-2)}╣{Theme.RESET}")

    @staticmethod
    def box_footer(width=70):
        print(f"{Theme.CYAN}╚{'═'*(width-2)}╝{Theme.RESET}")

def calculate_rpi(team):
    """
    Calculates a 'Rankings Power Index' score for a team.
    Formula:
    - Base: Wins * 100
    - Penalty: Losses * 60
    - Prestige Bonus: Prestige * 3 (Poll Inertia/Bias)
    - Point Diff: +1 per point (Capped at +20 per game to prevent stat padding)
    - Strength of Schedule: Opponent Wins * 5
    """
    
    # 1. Base Record Score
    score = (team.wins * 100) - (team.losses * 60)
    
    # 2. Poll Inertia (Prestige Bias)
    # A 99 Prestige team starts with +297 points (roughly equal to 3 wins)
    score += (team.prestige * 3)
    
    # 3. Strength of Schedule (SoS)
    opp_wins = 0
    opp_games = 0
    for game in team.schedule:
        if game.played:
            opp = game.home_team if game.away_team == team else game.away_team
            # FCS Teams might not have tracked wins/losses correctly in main loop if generic
            if hasattr(opp, 'wins'):
                opp_wins += opp.wins
                opp_games += 1
    
    score += (opp_wins * 5)

    # 4. Margin of Victory (Capped)
    diff = team.points_for - team.points_against
    max_diff = (team.wins + team.losses) * 25
    effective_diff = max(-max_diff, min(max_diff, diff))
    
    score += effective_diff * 0.5

    return score

def get_top_25(college_league):
    """Returns a sorted list of the top 25 teams."""
    ranked_teams = sorted(college_league, key=calculate_rpi, reverse=True)
    return ranked_teams[:25]

def display_rankings(college_league, week):
    top_25 = get_top_25(college_league)
    
    w = 70
    Theme.box_header(f"COLLEGE FOOTBALL TOP 25 (WEEK {week})", w)
    
    # Header Row
    print(f"{Theme.BORDER} {Theme.DIM}{'RK':<4} {'TEAM':<26} {'REC':<8} {'CONF':<14} {'RPI':<6}{Theme.RESET}    {Theme.BORDER}")
    print(f"{Theme.CYAN}╠{'═'*(w-2)}╣{Theme.RESET}")
    
    for i, team in enumerate(top_25):
        rank = i + 1
        rpi = int(calculate_rpi(team))
        
        # Determine Color
        color = Theme.BOLD
        if rank <= 4: color = f"{Theme.GREEN}{Theme.BOLD}" # Playoff Spots
        elif rank <= 12: color = Theme.CYAN               # CFP Contention
        
        # 1. Format the content plain
        rk_txt = f"{rank}"
        
        # 2. Pad to fixed width
        rk_padded = f"{rk_txt:<4}"
        
        # 3. Apply color to the padded string
        rk_final = f"{color}{rk_padded}{Theme.RESET}"
        
        # Format other columns
        name_final = f"{team.name:<26}"
        rec_final = f"{team.record_str():<8}"
        conf_final = f"{team.conference:<14}"
        rpi_final = f"{Theme.YELLOW}{str(rpi):<6}{Theme.RESET}"
        
        print(f"{Theme.BORDER} {rk_final} {name_final} {rec_final} {conf_final} {rpi_final}    {Theme.BORDER}")
        
    Theme.box_footer(w)
    
    # Projected Playoff Picture Footer
    if week >= 10:
        print(f"\n {Theme.GREEN}* Ranks 1-4:{Theme.RESET} Projected First Round Byes")
        print(f" {Theme.CYAN}* Ranks 5-12:{Theme.RESET} Projected Playoff At-Large")

# --- NEW: HEISMAN LOGIC ---

def calculate_heisman_score(player, team_wins):
    """Calculates a heuristic score for the Heisman Trophy."""
    score = 0.0
    s = player.stats
    
    # TEAM SUCCESS MULTIPLIER (Heisman winners usually on winning teams)
    # 25 points per win for QBs, less for others
    
    if player.position == "QB":
        score += s.get("pass_yds", 0) * 0.05
        score += s.get("pass_td", 0) * 4.0
        score -= s.get("pass_int", 0) * 4.0
        score += s.get("rush_yds", 0) * 0.05
        score += s.get("rush_td", 0) * 4.0
        score += (team_wins * 25.0)
        
    elif player.position == "RB":
        score += s.get("rush_yds", 0) * 0.08
        score += s.get("rush_td", 0) * 5.0
        score += s.get("rec_yds", 0) * 0.08
        score += s.get("rec_td", 0) * 5.0
        score += (team_wins * 15.0)
        
    elif player.position in ["WR", "TE"]:
        score += s.get("rec_yds", 0) * 0.08
        score += s.get("rec_td", 0) * 6.0
        score += (team_wins * 10.0)
        
    elif player.position in ["DL", "LB", "DB"]:
        # Defensive Heisman is rare, so weights must be high for stats
        score += s.get("tackles", 0) * 1.0
        score += s.get("sacks", 0) * 4.0
        score += s.get("int_made", 0) * 15.0
        score += s.get("def_td", 0) * 20.0
        score += (team_wins * 5.0)
        
    return int(score)

def get_heisman_leaders(college_league):
    """Returns top 10 Heisman candidates."""
    candidates = []
    
    for team in college_league:
        for player in team.roster:
            # Filter: Must be starter-ish (have stats)
            if not player.stats: continue
            
            # Optimization: Skip players with 0 stats in key areas
            if player.position == "QB" and player.stats.get("pass_att", 0) < 10: continue
            
            score = calculate_heisman_score(player, team.wins)
            candidates.append((player, team, score))
            
    # Sort by score descending
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[:10]