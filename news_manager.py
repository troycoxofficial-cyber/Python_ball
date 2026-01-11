import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Local Imports
from rankings import get_top_25

console = Console()

class NewsStory:
    def __init__(self, headline, body, category, week, year, importance=0):
        self.headline = headline
        self.body = body
        self.category = category # GAME, RECRUIT, COACH, INJURY, RANKING, PLAYOFF
        self.week = week
        self.year = year
        self.importance = importance # 0-100, used for sorting
        self.read = False

class NewsNarrator:
    """
    A helper class to generate high-variability text based on context.
    Uses a component-based builder pattern to ensure no two stories sound exactly alike.
    """
    
    # --- COACHING NARRATIVES ---
    @staticmethod
    def get_coach_headline(coach, school, archetype):
        if archetype == "EXTENSION":
            return random.choice([
                f"PAYDAY: {school.name} planning massive extension for {coach.last_name}",
                f"STAYING PUT? {coach.last_name} and {school.name} in contract talks",
                f"Locked In: {school.name} moves to secure {coach.last_name}'s future",
                f"Source: {coach.last_name} nearing long-term deal with {school.name}",
                f"The Foundation: {school.name} to reward {coach.last_name} after {school.wins}-win season"
            ])
        elif archetype == "HOT_SEAT":
            return random.choice([
                f"HOT SEAT: {coach.last_name} in trouble at {school.name}?",
                f"Time Running Out? Pressure mounts on {coach.full_name}",
                f"BOOSTER BUZZ: {school.name} donors 'unhappy' with {coach.last_name}",
                f"Seat Sizzling: {school.last_name} at a crossroads after latest loss",
                f"Change in {school.name}? Rumors swirl around {coach.last_name}'s future"
            ])
        elif archetype == "RISING_STAR":
            return random.choice([
                f"MOVING UP? P5 programs eyeing {school.name}'s {coach.last_name}",
                f"RISING STAR: {coach.full_name} linked to vacant high-profile jobs",
                f"The Next Big Thing: {coach.last_name} is the hottest name in coaching",
                f"Poaching Season: Can {school.name} keep {coach.last_name}?",
                f"On the Radar: {coach.last_name}'s success at {school.name} drawing national interest"
            ])
        elif archetype == "RETIREMENT":
            return random.choice([
                f"LAST DANCE? Retirement rumors follow {coach.full_name}",
                f"End of an Era? {coach.last_name} non-committal on future",
                f"Coaching Legend {coach.last_name} considering stepping away",
                f"Speculation: Is this {coach.last_name}'s final year at {school.name}?",
                f"Legacy Watch: {coach.last_name} reflects on career as season winds down"
            ])
        return f"Coaching Update: {coach.full_name}"

    @staticmethod
    def get_coach_body(coach, school, archetype):
        record = school.record_str()
        
        if archetype == "EXTENSION":
            intro = random.choice([
                f"With a {record} record, the {school.name} administration is moving fast.",
                f"Success breeds stability. After leading {school.name} to {school.wins} wins, {coach.last_name} has all the leverage.",
                f"The {school.name} leadership is reportedly 'ecstatic' with the direction of the program under {coach.last_name}."
            ])
            mid = random.choice([
                f"Rumors are swirling of a multi-year deal that would place {coach.last_name} among the highest-paid in the conference.",
                f"Talks are centered on a buyout structure intended to ward off NFL or bigger collegiate suitors.",
                f"The proposed deal is said to include massive upgrades to the team's training facilities."
            ])
            outro = random.choice([
                f"\"We want him here for a long time,\" a source close to the AD mentioned.",
                f"Expect an official announcement before the bowl season begins.",
                f"Keeping {coach.last_name} is the #1 priority for the {school.name} boosters right now."
            ])
            
        elif archetype == "HOT_SEAT":
            intro = random.choice([
                f"The noise in {school.name} is getting deafening. At {record}, the season is spiraling.",
                f"Patience is a luxury {coach.last_name} may no longer have. The {school.name} faithful are restless.",
                f"It's been a season of 'what-ifs' for {school.name}, and the blame is falling squarely on the head coach."
            ])
            mid = random.choice([
                f"Sources say influential boosters are already gathering funds for a potential buyout.",
                f"The disconnect between the staff and the administration has reportedly reached a boiling point.",
                f"Recruiting targets are starting to notice the instability, adding further pressure to the situation."
            ])
            outro = random.choice([
                f"{coach.last_name} needs a signature win to change the narrative.",
                f"The next few weeks will likely determine if a change is made.",
                f"\"We evaluate everything at the end of the year,\" said the AD in a terse statement."
            ])
            
        elif archetype == "RISING_STAR":
            intro = random.choice([
                f"What {coach.last_name} has done at {school.name} with a {record} record has not gone unnoticed.",
                f"Every year there is a 'it' coach. This year, it's {coach.full_name}.",
                f"Small school, big results. {school.name} is punching above its weight class thanks to {coach.last_name}."
            ])
            mid = random.choice([
                f"His name is being linked to several high-profile openings in the Power Five.",
                f"Analysts believe his modern offensive system is a perfect fit for a program looking to modernize.",
                f"Agents have reportedly been busy fielding 'exploratory' calls from across the country."
            ])
            outro = random.choice([
                f"{school.name} will likely have to offer a massive raise to keep him around.",
                f"For {coach.last_name}, it might be a matter of 'when', not 'if' he moves to a bigger stage.",
                f"Enjoy him while he's here, {school.name} fans."
            ])

        elif archetype == "RETIREMENT":
            intro = random.choice([
                f"{coach.full_name} has spent {coach.years_at_school} years at {school.name}, but the grind may be taking its toll.",
                f"At {coach.age if hasattr(coach, 'age') else 'this stage of his career'}, {coach.last_name} is facing questions about his longevity.",
                f"The legendary coach was seen lingering on the field longer than usual after the last home game."
            ])
            mid = random.choice([
                f"Whispers within the building suggest he is looking to spend more time with family.",
                f"While {school.name} is having a {record} season, {coach.last_name} may want to go out on top.",
                f"Health and the changing landscape of the game are reportedly factors in his thinking."
            ])
            outro = random.choice([
                f"If he steps away, it will leave massive shoes to fill in {school.name}.",
                f"He has refused to address the rumors, focusing instead on the upcoming schedule.",
                f"A coaching search in {school.name} would be the story of the offseason."
            ])

        return f"{intro}\n\n{mid} {outro}"

    # --- INJURY NARRATIVES ---
    @staticmethod
    def get_injury_headline(player, team_name, severity_grade):
        structures = [
            f"{team_name} dealt blow: {player.position} {player.last_name} out",
            f"Injury Report: {player.full_name} sidelined",
            f"{player.position} {player.last_name} goes down, {team_name} holds breath",
            f"Breaking: {team_name} starter {player.last_name} injured",
            f"Depth Tested: {player.full_name} out for {team_name}",
            f"Next Man Up: {team_name} loses {player.last_name}",
            f"Medical Update: {player.full_name} diagnosis"
        ]
        if severity_grade == "CRITICAL":
            structures.extend([
                f"DEVASTATING: {player.full_name} lost for season",
                f"Heartbreak in {team_name}: {player.last_name} done for year",
                f"Title hopes take hit: {player.last_name} suffers major injury",
                f"CATASTROPHE: Star {player.position} {player.last_name} out indefinitely"
            ])
        return random.choice(structures)

    @staticmethod
    def get_injury_hook(player, team, weeks):
        phrases = [
            f"The mood in the {team.name} locker room was somber today.",
            f"Just as {team.name} seemed to be finding their rhythm, disaster struck.",
            f"Coaches held their breath on the sideline, and the news is not good.",
            f"The training staff has delivered the news fans were dreading.",
            f"It's the update no {team.name} fan wanted to hear.",
            f"Adversity has arrived for the {team.name} program.",
            f"The physical toll of the season has claimed another victim."
        ]
        return random.choice(phrases)

    @staticmethod
    def get_injury_stat_context(player, rating):
        # Skip stat context for OL/K/P usually
        if player.position in ["OL", "K", "P"]:
            return "He has been a key piece of the lineup this season."
            
        if rating == "elite":
            templates = [
                f"{player.last_name} was in the middle of a Heisman-caliber campaign, posting {player.get_stat_summary()}.",
                f"Widely considered the heartbeat of this team, he had already racked up {player.get_stat_summary()}.",
                f"He was dominating the competition this year with {player.get_stat_summary()}.",
                f"Replacing his production ({player.get_stat_summary()}) will be a nightmare for the coordinator."
            ]
        elif rating == "good":
            templates = [
                f"He has been a steady hand for the unit, contributing {player.get_stat_summary()}.",
                f"While not a superstar, his {player.get_stat_summary()} was vital to the team's success.",
                f"He was having a breakout year with {player.get_stat_summary()}.",
                f"Reliable and tough, he had posted {player.get_stat_summary()} so far."
            ]
        else:
            templates = [
                f"He had struggled to find rhythm this year, posting {player.get_stat_summary()}.",
                f"It's been a quiet season for him with {player.get_stat_summary()}, and this halts any chance of a turnaround.",
                f"Depth is now an issue, though his production ({player.get_stat_summary()}) was modest."
            ]
        return random.choice(templates)

    @staticmethod
    def get_injury_impact(team, replacement, team_status):
        impacts = []
        if replacement:
            rep_diff = replacement.overall 
            if rep_diff > 78:
                rep_str = f"Backup {replacement.last_name} is a high-quality option (OVR: {replacement.overall}) and should fill in admirably."
            elif rep_diff > 70:
                rep_str = f"The staff will turn to {replacement.full_name}, who has limited experience but talent."
            elif replacement.eligibility_year == 1:
                rep_str = f"True Freshman {replacement.full_name} will be thrown into the fire immediately."
            else:
                rep_str = f"Depth is thin. {replacement.full_name} is the likely replacement, but it's a significant drop-off."
        else:
            rep_str = "The depth chart is barren. Coaches may have to get creative with positioning."

        if team_status == "CONTENDER":
            impacts.append(f"For a team chasing a playoff spot, this is a gut punch. {rep_str}")
            impacts.append(f"Championship teams overcome adversity. {team.name} needs to prove they can. {rep_str}")
        elif team_status == "REBUILDING":
            impacts.append(f"In a rebuilding year, this offers younger players a chance to shine. {rep_str}")
        else:
            impacts.append(f"The coaching staff challenged the reserves to step up. {rep_str}")

        return random.choice(impacts)

    # --- RECRUITING NARRATIVES ---
    @staticmethod
    def get_recruit_headline(player, school, hs_name):
        headlines = []
        # Use position in headline
        pos_str = player.position
        
        if player.stars == 5:
            headlines = [
                f"BOOM! 5-Star {pos_str} {player.full_name} commits to {school.name}",
                f"The Rich Get Richer: {school.name} lands elite {pos_str} {player.last_name}",
                f"PROGRAM CHANGER: #1 Target {player.full_name} picks {school.name}",
                f"{school.name} wins massive battle for {hs_name} star {pos_str}",
                f"5-Star Alert: {player.full_name} is a {school.mascot if hasattr(school, 'mascot') else 'Player'}"
            ]
        else:
            headlines = [
                f"Blue Chip: 4-Star {pos_str} {player.full_name} heads to {school.name}",
                f"{school.name} secures commitment from {hs_name} standout",
                f"Recruiting Update: {pos_str} {player.full_name} picks {school.name}",
                f"Pipeline: {school.name} adds talented {pos_str} from {hs_name}",
                f"{player.full_name} commits, boosts {school.name} class"
            ]
        return random.choice(headlines)

    @staticmethod
    def get_recruit_analysis(player, school, week, hs_name):
        # 1. Geographic Context
        geo_options = [
            f"The {hs_name} product hails from {player.home_state}.",
            f"Coming out of {player.home_state}, the {hs_name} standout has made his decision.",
            f"A native of {player.home_state}, he was a star at {hs_name}."
        ]
        geo_str = random.choice(geo_options)

        # 2. Performance/Trait Context (Position Aware)
        no_stat_positions = ["OL", "K", "P"]
        stats_ref = ""
        
        if player.position in no_stat_positions:
            # Physical/Trait descriptions for non-stat players
            descriptions = [
                "Scouts rave about his fundamentals and footwork.",
                "He is widely considered one of the most technically sound players in the class.",
                f"At {random.randint(6,6)}'{random.randint(2,6)}, he possesses the ideal frame for the next level.",
                "He dominates the point of attack and plays with a mean streak.",
                "A consistent performer who rarely misses an assignment."
            ]
            stats_ref = random.choice(descriptions)
        else:
            # Skill positions get stat references
            if week < 4 and player.history:
                last_season = player.history[-1]
                if 'stats' in last_season:
                    s_sum = player.get_stat_summary(last_season['stats'])
                    stats_ref = f"Coming off a dominant junior campaign where he posted {s_sum}, his stock has skyrocketed."
            else:
                s_sum = player.get_stat_summary()
                stats_ref = f"He is currently tearing up the high school circuit with {s_sum} this season."

        # 3. Fit Logic
        fit_str = ""
        if school.prestige > 80:
            fit_str = "He joins a loaded class expected to contend for titles immediately."
        elif school.prestige < 50:
            fit_str = "He instantly becomes the jewel of this class and a likely day-one starter."
        else:
            fit_str = "A solid pickup that addresses a key positional need for the future."

        # 4. Scout Quote
        quotes = [
            f"\"He has Sunday potential written all over him,\" said one scout. {stats_ref}",
            f"\"The combination of size and speed is rare.\" {stats_ref}",
            f"\"He plays with a mean streak that coaches love.\" {stats_ref}",
            f"\"One of the most polished prospects in the region.\" {stats_ref}",
            f"\"An absolute steal for {school.name}.\" {stats_ref}"
        ]
        
        return f"{geo_str} {random.choice(quotes)}\n\n{fit_str}"

    # --- GAME NARRATIVES ---
    @staticmethod
    def get_game_headline(winner, loser, archetype, score_str, r_w, r_l):
        # r_w / r_l are ranks (None if unranked)
        headlines = []
        
        if archetype == "TITAN_FALLS":
            headlines = [
                f"SHOCKER: {winner.name} Topples #{r_l} {loser.name}",
                f"DOWN GOES #{r_l}: {winner.name} Stuns the Nation",
                f"CHAOS: {winner.name} Ends {loser.name}'s Hopes",
                f"The Giant Killers: {winner.name} beats #{r_l} {loser.name}",
                f"Bracket Buster! {winner.name} {score_str}"
            ]
        elif archetype == "UPSET":
            headlines = [
                f"UPSET: {winner.name} Surprise Winner over #{r_l} {loser.name}",
                f"{winner.name} Spoils {loser.name}'s Season",
                f"Rankings Shakeup: {winner.name} Defeats Ranked {loser.name}",
                f"Statement Win: {winner.name} Takes Down {loser.name}"
            ]
        elif archetype == "CLASH":
            headlines = [
                f"HEAVYWEIGHTS: #{r_w} {winner.name} Outlasts #{r_l} {loser.name}",
                f"Playoff Preview: {winner.name} Wins Top-10 Showdown",
                f"Clash of Titans: {winner.name} Proves Superior",
                f"Statement Made: {winner.name} Takes Control"
            ]
        elif archetype == "THRILLER":
            headlines = [
                f"INSTANT CLASSIC: {winner.name} {score_str}",
                f"HEARTBREAKER: {loser.name} Falls Short Late",
                f"SURVIVAL: {winner.name} Escapes with Narrow Win",
                f"Down to the Wire: {winner.name} Edges {loser.name}"
            ]
        elif archetype == "SHOOTOUT":
            headlines = [
                f"OFFENSIVE EXPLOSION: {winner.name} Wins Track Meet",
                f"SCOREBOARD BREAKER: {winner.name} {score_str}",
                f"FIREWORKS: No Defense Found in {winner.name} Win"
            ]
        elif archetype == "ZERO_HOUR":
            headlines = [
                f"SHUTOUT: {winner.name} Blanks {loser.name}",
                f"DONUT: {loser.name} Scoreless against {winner.name}",
                f"PERFECTION: {winner.name} Defense Dominates in {score_str} Win"
            ]
        elif archetype == "STATEMENT":
            headlines = [
                f"DOMINATION: {winner.name} Routs {loser.name}",
                f"MESSAGE SENT: {winner.name} Crushes {loser.name}",
                f"NO CONTEST: {winner.name} Blows Out {loser.name}"
            ]
        else:
            headlines = [
                f"{winner.name} Defeats {loser.name}",
                f"{winner.name} Adds Win vs {loser.name} {score_str}",
                f"{winner.name} {score_str} {loser.name}"
            ]
        return random.choice(headlines)

    @staticmethod
    def get_game_atmosphere(winner, loser, archetype, r_w, r_l):
        # The "Lede"
        conf_name = getattr(winner, 'conference', 'League')
        
        if archetype == "TITAN_FALLS":
            return random.choice([
                "In one of the most shocking results of the decade,",
                "Fans rushed the field as the clock hit zero,",
                "There was stunned silence on the sideline as",
                "The college football landscape has been turned upside down after"
            ])
        elif archetype == "CLASH":
            return random.choice([
                f"In a game with massive {conf_name} title implications,",
                "The atmosphere was electric from kickoff to the final whistle as",
                "Millions tuned in for the marquee matchup of the week, and"
            ])
        elif archetype == "THRILLER":
            return random.choice([
                "Fans got their money's worth and then some today as",
                "It took every last second on the clock to decide this one, but",
                "In a game that will be replayed on highlights for years,"
            ])
        elif archetype == "ZERO_HOUR":
            return random.choice([
                f"The {winner.name} defensive coordinator deserves a raise after today,",
                "Points were impossible to come by for the visiting team as",
                "It was a masterclass in defensive football as"
            ])
        elif archetype == "STATEMENT":
            return random.choice([
                f"{winner.name} left no doubt about who was the better team today,",
                "From the opening drive, it was clear only one team came to play.",
                "In a performance that will terrify the rest of the conference,"
            ])
        else:
            return random.choice([
                f"Under the lights at {winner.name if random.random()>0.5 else loser.name},",
                "It was a hard-fought contest in the trenches, but",
                f"{winner.name} continued their season with a professional performance where"
            ])

    @staticmethod
    def get_game_flow(winner, loser, archetype, score_str, turnovers):
        if turnovers > 4:
            return f"despite a combined {turnovers} turnovers, {winner.name} made the critical plays when it mattered most to win {score_str}."
        elif archetype == "SHOOTOUT":
            return f"both offenses traded blows in a dizzying display of scoring, but {winner.name} had the ball last to win {score_str}."
        elif archetype == "ZERO_HOUR":
            return f"{winner.name} suffocated the {loser.name} offense, refusing to yield a single point in the {score_str} victory."
        elif archetype == "STATEMENT":
            return f"{winner.name} imposed their will on both sides of the ball, cruising to a {score_str} victory."
        elif archetype == "THRILLER":
            return f"it came down to the final possession, but {winner.name} held on to seal the {score_str} win."
        else:
            return f"{winner.name} executed their gameplan and walked away with the {score_str} victory."

    @staticmethod
    def get_game_quote(winner, loser, archetype):
        w_coach = winner.coach.last_name if winner.coach else "The Coach"
        l_coach = loser.coach.last_name if loser.coach else "The Coach"
        
        if archetype in ["TITAN_FALLS", "UPSET"]:
            return random.choice([
                f"\"We shocked the world today,\" said {winner.name} HC {w_coach}. \"Nobody believed in us but the guys in this locker room.\"",
                f"\"This is a program-defining win,\" {w_coach} told reporters. \"We proved we belong.\"",
                f"On the other side, {loser.name} HC {l_coach} was blunt: \"We weren't prepared. That's on me.\""
            ])
        elif archetype == "THRILLER":
            return random.choice([
                f"\"My heart can't take many more of these,\" joked {w_coach}. \"But a win is a win.\"",
                f"\"It's a tough pill to swallow,\" said {l_coach}. \"We were one play away.\"",
                f"\"Credit to {loser.name}, they gave us everything we could handle,\" {w_coach} admitted."
            ])
        elif archetype == "ZERO_HOUR":
             return random.choice([
                f"\"Goose eggs. That's what we like to see,\" grinned {w_coach}.",
                f"\"I don't think they crossed the 50 all day,\" noted an analyst.",
                f"\"We wanted to pitch the shutout,\" said {w_coach}."
            ])
        elif archetype == "STATEMENT":
            return random.choice([
                f"\"We wanted to send a message,\" said {w_coach}. \"I think they heard us.\"",
                f"\"Complete performance. Offense, defense, special teams,\" praised {w_coach}.",
                f"\"We got punched in the mouth and didn't respond,\" admitted {l_coach}."
            ])
        else:
             return f"\"We'll enjoy this for 24 hours, then it's on to the next one,\" said {w_coach}."

class NewsManager:
    def __init__(self, universe):
        self.universe = universe
        if not hasattr(universe, 'news'):
            universe.news = []
        
        # State tracking for delta detection
        self.prev_rankings = {}
        self.known_commits = set()
        self.known_injuries = {} 
        self.coach_mentions = {} 
        
        # Initialize state
        self._capture_state()

    def _capture_state(self):
        """Captures current state to compare against next week."""
        top_25 = get_top_25(self.universe.college_league)
        self.prev_rankings = {t.name: i+1 for i, t in enumerate(top_25)}
        
        self.known_commits = set()
        for s in self.universe.college_league:
            if hasattr(s, 'commits'):
                for p in s.commits:
                    self.known_commits.add(p.id)
                    
        self.known_injuries = {}
        for s in self.universe.college_league:
            for p in s.roster:
                if p.weeks_injured > 0:
                    self.known_injuries[p.id] = p.weeks_injured

    def generate_weekly_news(self):
        """Main generation loop called after a week is simulated."""
        week = self.universe.current_week - 1
        year = self.universe.year
        
        stories = []
        
        # Pre-calculate Player -> HS Map for Recruiting News
        recruit_hs_map = {}
        for hs in self.universe.high_school_league:
            for p in hs.roster:
                recruit_hs_map[p.id] = hs.name

        # 1. GAME RECAPS
        if week in self.universe.schedule:
            games = self.universe.schedule[week]
            random.shuffle(games)
            
            game_stories = []
            for game in games:
                if game.played:
                    # Guard Clause: Skip High School Games
                    if not hasattr(game.home_team, 'conference'): continue
                    
                    story = self._generate_game_story(game, week, year)
                    if story: game_stories.append(story)
            
            game_stories.sort(key=lambda x: x.importance, reverse=True)
            stories.extend(game_stories[:6]) 

        # 2. RANKING SHAKEUPS
        stories.extend(self._generate_ranking_stories(week, year))

        # 3. RECRUITING NEWS
        stories.extend(self._generate_recruiting_stories(week, year, recruit_hs_map))

        # 4. INJURY REPORTS
        stories.extend(self._generate_injury_stories(week, year))

        # 5. COACHING NEWS
        stories.extend(self._generate_coach_stories(week, year))
        
        # 6. WEEKLY PREVIEW
        next_week = self.universe.current_week
        if next_week in self.universe.schedule:
            stories.extend(self._generate_previews(self.universe.schedule[next_week], next_week, year))
            
        # 7. PLAYOFF WATCH (Late Season Variety)
        if week >= 10:
             stories.extend(self._generate_playoff_watch(week, year))

        # Sort and Trim
        stories.sort(key=lambda x: x.importance, reverse=True)
        self.universe.news.extend(stories)
        self._capture_state()
        
        if len(self.universe.news) > 80: 
            self.universe.news = self.universe.news[-80:]

    # --- INTELLIGENCE HELPERS ---

    def _analyze_player_season(self, player):
        """Returns a dict with performance analysis: 'rating' (bad/avg/good/elite), 'desc'."""
        s = player.stats
        pos = player.position
        
        # Default
        rating = "avg"
        desc = "quiet season"
        
        if pos == "QB":
            tds = s.get('pass_td', 0)
            ints = s.get('pass_int', 0)
            yds = s.get('pass_yds', 0)
            if yds < 50 and tds == 0 and ints == 0: return {"rating": "n/a", "desc": "limited action"}
            
            ratio = tds - ints
            if ratio >= 8 and yds > 1000: 
                rating, desc = "elite", "Heisman-caliber campaign"
            elif ratio >= 3: 
                rating, desc = "good", "strong season"
            elif ratio < 0: 
                rating, desc = "bad", "turnover-plagued season"
            elif yds < 150 * (self.universe.current_week or 1): 
                rating, desc = "bad", "underwhelming performance"
                
        elif pos == "RB":
            yds = s.get('rush_yds', 0)
            tds = s.get('rush_td', 0)
            avg = yds / max(1, s.get('rush_att', 1))
            if yds < 50: return {"rating": "n/a", "desc": "limited action"}
            
            if avg > 6.0 or tds > 8: rating, desc = "elite", "dominant ground game"
            elif avg > 4.0: rating, desc = "good", "reliable production"
            elif avg < 3.0: rating, desc = "bad", "struggles to find lanes"

        elif pos in ["WR", "TE"]:
            yds = s.get('rec_yds', 0)
            tds = s.get('rec_td', 0)
            if yds < 50: return {"rating": "n/a", "desc": "limited action"}
            
            if tds > 6 or yds > 600: rating, desc = "elite", "explosive playmaking"
            elif tds > 2: rating, desc = "good", "consistent target"
            else: rating, desc = "avg", "steady contribution"

        elif pos in ["LB", "DB", "DL"]:
            tkl = s.get('tackles', 0)
            scks = s.get('sacks', 0)
            ints = s.get('int_made', 0)
            
            impact_score = tkl + (scks * 5) + (ints * 10)
            if impact_score > 40: rating, desc = "elite", "defensive player of the year candidacy"
            elif impact_score > 15: rating, desc = "good", "defensive anchor"
            elif impact_score < 5: rating, desc = "bad", "quiet year"

        return {"rating": rating, "desc": desc}

    def _get_replacement_info(self, team, position, injured_id):
        """Finds the next best player at the position."""
        depth_chart = [p for p in team.roster if p.position == position and p.id != injured_id and p.weeks_injured == 0]
        depth_chart.sort(key=lambda x: x.overall, reverse=True)
        return depth_chart[0] if depth_chart else None

    def _scan_game_log_for_context(self, game):
        """Reads the raw game log to find narrative hooks."""
        log_text = " ".join(game.game_log)
        turnovers = log_text.count("INTERCEPTED") + log_text.count("FUMBLE") + log_text.count("Fumble")
        
        context = "clean"
        if turnovers >= 4: context = "sloppy"
        if "OT" in log_text: context = "ot_thriller"
        
        return context, turnovers

    # --- GENERATORS ---

    def _generate_game_story(self, game, week, year):
        winner = game.winner
        loser = game.home_team if game.winner != game.home_team else game.away_team
        w_score = max(game.home_score, game.away_score)
        l_score = min(game.home_score, game.away_score)
        diff = w_score - l_score
        total_pts = w_score + l_score
        score_str = f"{w_score}-{l_score}"
        
        w_rank = self.prev_rankings.get(winner.name, None)
        l_rank = self.prev_rankings.get(loser.name, None)
        
        # Intelligent Context Scanning
        log_context, turnovers = self._scan_game_log_for_context(game)
        
        # --- ARCHETYPE SELECTION ---
        importance = 10
        archetype = "STANDARD"
        
        if l_rank and l_rank <= 5 and (not w_rank or w_rank > 20):
            archetype = "TITAN_FALLS"; importance = 95
        elif l_rank and l_rank <= 25 and not w_rank:
            archetype = "UPSET"; importance = 75
        elif w_rank and l_rank and w_rank <= 12 and l_rank <= 12:
            archetype = "CLASH"; importance = 90
        elif log_context == "ot_thriller" or diff <= 3:
            archetype = "THRILLER"; importance = 45 + (20 if w_rank else 0)
        elif l_score == 0 and diff > 17:
            archetype = "ZERO_HOUR"; importance = 50 + (10 if w_rank else 0)
        elif log_context == "sloppy" and diff < 10:
            archetype = "SLOPPY"; importance = 30
        elif total_pts > 80:
            archetype = "SHOOTOUT"; importance = 40
        elif diff >= 28 and (w_rank and l_rank):
            archetype = "STATEMENT"; importance = 65
            
        # SELECTIVITY: Ignore boring games
        if importance < 30 and not w_rank and not l_rank: return None 
        if importance < 20: return None

        # --- DYNAMIC TEXT GENERATION ---
        headline = NewsNarrator.get_game_headline(winner, loser, archetype, score_str, w_rank, l_rank)
        intro = NewsNarrator.get_game_atmosphere(winner, loser, archetype, w_rank, l_rank)
        flow = NewsNarrator.get_game_flow(winner, loser, archetype, score_str, turnovers)
        
        context_lines = []
        if winner.wins > 5 and winner.losses == 0:
            context_lines.append(f"With the win, {winner.name} keeps their perfect season alive at {winner.record_str()}.")
        elif loser.losses > 3: 
            context_lines.append(f"The loss compounds a frustrating season for {loser.name}, who fall to {loser.record_str()}.")
        else:
            context_lines.append(f"{winner.name} improves to {winner.record_str()}.")
            
        if l_rank and l_rank <= 12: 
            context_lines.append(f"{loser.name}'s playoff hopes have taken a massive hit.")
            
        context = " ".join(context_lines)
        quote = NewsNarrator.get_game_quote(winner, loser, archetype)
        
        body = f"{intro} {flow}\n\n{context}\n\n{quote}"
        
        return NewsStory(headline, body, "GAME", week, year, importance)

    def _generate_ranking_stories(self, week, year):
        stories = []
        current_top_25 = get_top_25(self.universe.college_league)
        curr_ranks = {t.name: i+1 for i, t in enumerate(current_top_25)}
        
        old_no1 = next((name for name, r in self.prev_rankings.items() if r == 1), None)
        new_no1 = current_top_25[0].name
        
        # NEW #1
        if old_no1 and new_no1 != old_no1:
            headline = f"NEW KING: {new_no1} Takes #1 Spot"
            body_opts = [
                f"The polls have shifted. Following a chaotic week, voters have crowned {new_no1} as the new number one team.",
                f"There is a new team atop the mountain. {new_no1} has claimed the #1 ranking.",
                f"Heavy is the head that wears the crown. {new_no1} is the new #1 team in the nation."
            ]
            body = f"{random.choice(body_opts)}\n\nThey overtake {old_no1}. The question now becomes: can {new_no1} handle the pressure?"
            stories.append(NewsStory(headline, body, "RANKING", week, year, 80))

        # RISERS AND FALLERS
        biggest_rise = 0
        riser_team = None
        biggest_fall = 0
        faller_team = None
        
        for name, rank in curr_ranks.items():
            prev = self.prev_rankings.get(name, 26)
            diff = prev - rank
            if diff > biggest_rise:
                biggest_rise = diff
                riser_team = name
            if diff < biggest_fall: # Negative diff means fall
                biggest_fall = diff
                faller_team = name
                
        if biggest_rise >= 5:
            headline = f"MOVER: {riser_team} Jumps {biggest_rise} Spots"
            body = f"{riser_team} is the darling of the voters this week, skyrocketing to #{curr_ranks[riser_team]}.\n\nExperts are starting to buy stock in {riser_team} as a legitimate contender."
            stories.append(NewsStory(headline, body, "RANKING", week, year, 40))
            
        if biggest_fall <= -5 and faller_team:
             headline = f"FREEFALL: {faller_team} Plummets to #{curr_ranks[faller_team]}"
             body = f"After a disappointing performance, {faller_team} has been punished by the voters, dropping {abs(biggest_fall)} spots.\n\nThey will need to rebound quickly to regain respect."
             stories.append(NewsStory(headline, body, "RANKING", week, year, 40))
            
        return stories

    def _generate_recruiting_stories(self, week, year, hs_map):
        stories = []
        for school in self.universe.college_league:
            if not hasattr(school, 'commits'): continue
            
            for p in school.commits:
                if p.id not in self.known_commits:
                    # Filter for only 4 and 5 stars
                    if p.stars < 4: continue
                    
                    hs_name = hs_map.get(p.id, "High School")
                    
                    headline = NewsNarrator.get_recruit_headline(p, school, hs_name)
                    analysis = NewsNarrator.get_recruit_analysis(p, school, week, hs_name)
                    
                    body = f"{analysis}"
                    
                    importance = 80 if p.stars == 5 else 50
                    stories.append(NewsStory(headline, body, "RECRUITING", week, year, importance))
        return stories

    def _generate_injury_stories(self, week, year):
        stories = []
        for school in self.universe.college_league:
            for p in school.roster:
                if p.weeks_injured > 0 and p.id not in self.known_injuries:
                    # SELECTIVITY FILTERS (ADJUSTED)
                    
                    # 1. Random Chance to Ignore (Reduced from 30% to 15%)
                    if random.random() < 0.15: continue
                    
                    # 2. Depth Chart Rank (Must be Starter)
                    depth_rank = 1
                    same_pos = [x for x in school.roster if x.position == p.position]
                    same_pos.sort(key=lambda x: x.overall, reverse=True)
                    try:
                        depth_rank = same_pos.index(p) + 1
                    except: pass
                    
                    if depth_rank > 1 and p.position != "QB": continue # Ignore backups unless QB
                    
                    # 3. Quality Check (Lowered threshold)
                    if p.overall < 80: continue # Was 82
                    
                    # 4. Severity Check (Lowered threshold)
                    if p.weeks_injured < 3 and p.overall < 88 and p.position != "QB": continue

                    analysis = self._analyze_player_season(p)
                    rating = analysis['rating']
                    
                    severity_grade = "CRITICAL" if p.weeks_injured > 8 else "MAJOR" if p.weeks_injured > 3 else "MINOR"
                    
                    headline = NewsNarrator.get_injury_headline(p, school.name, severity_grade)
                    hook = NewsNarrator.get_injury_hook(p, school, p.weeks_injured)
                    stats_ctx = NewsNarrator.get_injury_stat_context(p, rating)
                    
                    replacement = self._get_replacement_info(school, p.position, p.id)
                    team_status = "CONTENDER" if school.prestige > 80 or (school.wins > 5 and school.losses < 2) else "REBUILDING"
                    if school.prestige < 50: team_status = "REBUILDING"
                    
                    impact = NewsNarrator.get_injury_impact(school, replacement, team_status)
                    
                    body = f"{hook}\n\n{p.position} {p.full_name} has suffered a {p.injury_type} and will miss {p.weeks_injured} weeks. {stats_ctx}\n\n{impact}"

                    # Low Importance so it floats to bottom
                    importance = 25
                    if p.stars == 5: importance += 10
                    if rating == "elite": importance += 10

                    stories.append(NewsStory(headline, body, "INJURY", week, year, importance))
        return stories

    def _generate_coach_stories(self, week, year):
        stories = []
        
        for school in self.universe.college_league:
            coach = school.coach
            if not coach: continue
            
            last_mention = self.coach_mentions.get(coach.full_name, -10)
            if week - last_mention < 4: continue 

            archetype = None
            importance = 50

            # 1. HOT SEAT (Poor performance at good school)
            if coach.years_at_school >= 2 and school.prestige > 60:
                if (school.losses > 5 and week > 7) or (school.wins < 2 and week > 5):
                    archetype = "HOT_SEAT"
                    importance = 85

            # 2. RISING STAR (Great performance at small school)
            elif school.prestige < 55 and school.wins > 6 and school.losses < 3:
                archetype = "RISING_STAR"
                importance = 70

            # 3. EXTENSION (Great performance at established school)
            elif school.wins > 8 and week > 9:
                # Randomize so it doesn't happen for every single 9+ win team
                if random.random() < 0.3:
                    archetype = "EXTENSION"
                    importance = 60

            # 4. RETIREMENT (Old coach / long tenure)
            elif (coach.years_at_school > 8 or (hasattr(coach, 'age') and coach.age > 60)) and week > 10:
                if random.random() < 0.1:
                    archetype = "RETIREMENT"
                    importance = 65

            if archetype:
                headline = NewsNarrator.get_coach_headline(coach, school, archetype)
                body = NewsNarrator.get_coach_body(coach, school, archetype)
                stories.append(NewsStory(headline, body, "COACHING", week, year, importance))
                self.coach_mentions[coach.full_name] = week

        return stories
        
    def _generate_previews(self, games, week, year):
        stories = []
        ranked_games = []
        curr_ranks = {t.name: i+1 for i, t in enumerate(get_top_25(self.universe.college_league))}
        
        for g in games:
            if not hasattr(g.home_team, 'conference'): continue 

            r_home = curr_ranks.get(g.home_team.name, 99)
            r_away = curr_ranks.get(g.away_team.name, 99)
            if r_home <= 25 and r_away <= 25:
                ranked_games.append((g, r_home + r_away))
        
        if ranked_games:
            ranked_games.sort(key=lambda x: x[1])
            top_game = ranked_games[0][0]
            
            h_rank = curr_ranks.get(top_game.home_team.name)
            a_rank = curr_ranks.get(top_game.away_team.name)
            
            headline = f"GAME OF THE WEEK: #{a_rank} {top_game.away_team.name} @ #{h_rank} {top_game.home_team.name}"
            
            body = f"All eyes will be on {top_game.home_team.name} this weekend as they host {top_game.away_team.name} in a massive top-25 showdown. "
            body += f"Both teams enter the contest with high playoff aspirations, and this game could serve as an elimination match.\n\n"
            
            if h_rank < a_rank: 
                body += f"The home team is favored, looking to defend their turf and prove they belong in the national title conversation."
            else: 
                body += f"The road team comes in as the underdog by ranking, but they have the firepower to pull off the upset if they can control the tempo."
            
            stories.append(NewsStory(headline, body, "PREVIEW", week, year, 85))
            
        return stories

    def _generate_playoff_watch(self, week, year):
        stories = []
        top_25 = get_top_25(self.universe.college_league)
        if not top_25: return stories
        
        # 1. Bubble Watch
        bubble_teams = top_25[10:14] # Ranks 11-14
        if bubble_teams:
            headline = "BUBBLE WATCH: Who is in and who is out?"
            body = "As we approach the end of the season, the playoff picture is getting blurry.\n\n"
            for t in bubble_teams:
                body += f"- {t.name} ({t.record_str()}): Needs to win out.\n"
            body += "\nEvery game matters from here on out."
            stories.append(NewsStory(headline, body, "PLAYOFF", week, year, 75))
            
        return stories

    def view_dashboard(self):
        """Interactive News Feed."""
        while True:
            console.clear()
            console.print(Panel("[bold yellow]COLLEGE FOOTBALL NEWS WIRE[/bold yellow]", style="blue"))
            
            # --- UPDATED DISPLAY LOGIC ---
            # If news exists, get the Week/Year of the LATEST story
            if not self.universe.news:
                console.print("[dim]No news generated yet. Simulate a week![/dim]")
            else:
                last_story = self.universe.news[-1]
                target_week = last_story.week
                target_year = last_story.year
                
                # Filter for ALL stories from that week
                current_stories = [
                    s for s in self.universe.news 
                    if s.week == target_week and s.year == target_year
                ]
                
                # Sort: Important first
                current_stories.sort(key=lambda x: x.importance, reverse=True)
                
                table = Table(box=None, show_header=False, padding=(0, 0, 1, 0))
                table.add_column("Details")
                
                for i, s in enumerate(current_stories):
                    cat_style = {
                        "GAME": "bold green", "RANKING": "bold cyan", 
                        "RECRUITING": "bold yellow", "INJURY": "bold red",
                        "PREVIEW": "bold magenta", "COACHING": "bold blue",
                        "PLAYOFF": "bold white"
                    }.get(s.category, "white")
                    
                    header = f"[{cat_style}]{s.category}[/{cat_style}] | Wk {s.week}, {s.year}"
                    content = f"[bold]{s.headline}[/bold]\n[dim]{s.body}[/dim]"
                    table.add_row(Panel(content, title=header, title_align="left", border_style="dim"))
                    
                console.print(table)
            
            console.print("\n[dim]Press Enter to return...[/dim]")
            input()
            break