import logging

import pandas as pd


logger = logging.getLogger(__name__)


def process_game(game_df):
    return GameProcessor(game_df).process_game()


class GameProcessor:
    def __init__(self, game_df):
        self.game_df = game_df.copy()

        self.game_df['SECONDS_REMAINING'] = self.game_df['PCTIMESTRING'].map(clock_to_seconds_remaining)
        self.game_df['DESCRIPTION'] = self.game_df['HOMEDESCRIPTION'].fillna('') + game_df['VISITORDESCRIPTION'].fillna('')
        self.game_df['SCORE'] = self.game_df['SCORE'].fillna(method='ffill').fillna('0 - 0')
        self.game_df['HOME_SCORE'] = self.game_df['SCORE'].map(lambda val: int(val.split(' - ')[1]))
        self.game_df['AWAY_SCORE'] = self.game_df['SCORE'].map(lambda val: int(val.split(' - ')[0]))

        self.home_team_id, self.away_team_id, home_team, away_team = self._find_team_info(self.game_df)
        

        self._template_possession = {
            # Constant data
            'game_id': game_df['GAME_ID'].iloc[0],
            'season': game_df['SEASON'].iloc[0],
            'season_type': game_df['SEASON_TYPE'].iloc[0],
            'home_team': home_team,
            'away_team': away_team,

            # Data from the previous possession
            'time': None,  # comes from previous possession ending event
            'period': None,  # comes from previous possession ending event
            'home_score': None,  # comes from previous possession ending event
            'away_score': None,  # comes from previous possession ending event

            # Data from this possession
            'duration': None,  # time minus time of this possession's ending event
            'home_poss': None,  # comes from this possession's ending event (except for rebounds and fouls)

            # Defaults overridden by data from this possession
            'turnover': False,
            '2pt_attempt': False,
            '3pt_attempt': False,
            'shot_made': False,
            'fta': 0,
            'ftm': 0,
            'reboundable': False,
            'oreb': False
        }

    def _find_team_info(self, game_df):
        first_home_make = game_df[(game_df['EVENTMSGTYPE'] == 1) & ~(game_df['HOMEDESCRIPTION'].isna())].iloc[0]
        home_team_id = first_home_make['PLAYER1_TEAM_ID']
        home_team = first_home_make['PLAYER1_TEAM_ABBREVIATION']
        first_away_make = game_df[(game_df['EVENTMSGTYPE'] == 1) & ~(game_df['VISITORDESCRIPTION'].isna())].iloc[0]
        away_team_id = first_away_make['PLAYER2_TEAM_ID']
        away_team = first_away_make['PLAYER2_TEAM_ABBREVIATION']
        return home_team_id, away_team_id, home_team, away_team

    def process_game(self):
        return pd.DataFrame(self._find_possessions())

    def _new_possession(self, row):
        next_possession = self._template_possession.copy()
        next_possession['time'] = row.SECONDS_REMAINING
        next_possession['period'] = row.PERIOD
        next_possession['home_score'] = row.HOME_SCORE
        next_possession['away_score'] = row.AWAY_SCORE
        return next_possession

    def _find_possessions(self):
        """
        Iterator that steps through the game, yielding possessions as it finds them.
        """
        self._rows = self.game_df.itertuples(index=False)
        row = next(self._rows)
        possession = self._new_possession(row)
        while True:
            try:
                if self._is_turnover(row):
                    row, next_possession = self._handle_turnover(row, possession)
                elif self._is_make(row):
                    row, next_possession = self._handle_make(row, possession)
                elif self._is_miss(row):
                    row, next_possession = self._handle_miss(row, possession)
                elif self._is_shooting_foul(row):
                    row, next_possession = self._handle_shooting_foul(row, possession)
                elif self._is_foul_with_fts(row):
                    row, next_possession = self._handle_foul_with_fts(row, possession)
                elif self._is_end_of_period(row):
                    row, possession = self._handle_end_of_period(row, possession)
                    continue  # possessions that end with a period are ignored, so we just set the next one up
                else:
                    if self._is_fta(row):
                        logger.warning(f'Found unassociated, non-technical free throw attempt in game {row.GAME_ID}, event {row.EVENTNUM}')
                    row = next(self._rows)
                    continue
            except StopIteration:
                break
            yield possession
            possession = next_possession

    @staticmethod
    def _assign_duration(row, possession):
        possession['duration'] = possession['time'] - row.SECONDS_REMAINING

    def _handle_turnover(self, row, possession):
        possession['turnover'] = True
        self._assign_duration(row, possession)
        possession['home_poss'] = row.PLAYER1_TEAM_ID == self.home_team_id
        return next(self._rows), self._new_possession(row)

    def _handle_make(self, row, possession):
        is_three = self._is_three(row)
        possession['3pt_attempt'] = is_three
        possession['2pt_attempt'] = not is_three
        possession['shot_made'] = True
        possession['home_poss'] = row.PLAYER1_TEAM_ID == self.home_team_id
        return self._find_and_one_foul(row, possession)

    def _handle_miss(self, row, possession):
        is_three = self._is_three(row)
        possession['3pt_attempt'] = is_three
        possession['2pt_attempt'] = not is_three
        possession['home_poss'] = row.PLAYER1_TEAM_ID == self.home_team_id
        return self._find_rebound(row, possession)

    def _handle_shooting_foul(self, row, possession):
        possession['home_poss'] = row.PLAYER2_TEAM_ID == self.home_team_id
        return self._find_freethrows(row, possession)

    def _handle_foul_with_fts(self, row, possession):
        possession['home_poss'] = row.PLAYER1_TEAM_ID != self.home_team_id
        return self._find_freethrows(row, possession)

    def _handle_end_of_period(self, row, possession):
        """
        Ignore possessions that end with the period, so just get the next posseesion ready
        """
        next_row = next(self._rows)
        return next_row, self._new_possession(next_row)

    def _find_and_one_foul(self, shot_row, possession):
        shooter_id = shot_row.PLAYER1_ID
        row = next(self._rows)
        while True:
            if self._is_shooting_foul(row) & (row.PLAYER2_ID == shooter_id):
                return self._find_freethrows(row, possession)
            elif self._is_actionable(row):
                self._assign_duration(shot_row, possession)
                return row, self._new_possession(shot_row)
            row = next(self._rows)

    def _find_freethrows(self, foul_row, possession):
        shooter_id = foul_row.PLAYER2_ID
        # Shooting fouls on a miss must also assign the shot type
        assign_shot_type = self._is_shooting_foul(foul_row) and not (possession['2pt_attempt'] or possession['3pt_attempt'])
        row = next(self._rows)
        while True:
            if self._is_fta(row) and ((row.PLAYER1_ID == shooter_id) or (shooter_id is None)):
                if assign_shot_type and self._is_first_fta(row):
                    is_three = self._num_fts(row) == 3
                    possession['3pt_attempt'] = is_three
                    possession['2pt_attempt'] = not is_three
                    assign_shot_type = False
                possession['fta'] += 1
                made = self._is_ftm(row)
                if made:
                    possession['ftm'] += 1
                if self._is_final_fta(row):
                    if made:
                        self._assign_duration(row, possession)
                        return next(self._rows), self._new_possession(row)
                    else:
                        return self._find_rebound(row, possession)
            elif self._is_turnover(row) and foul_row.PLAYER1_ID == row.PLAYER1_ID:
                # Sometimes a foul resulting in free throws precedes a turnover, so we have to handle that here
                # by returning a turnover possession and the foul row as the next to be processed
                possession['home_poss'] = row.PLAYER1_TEAM_ID == self.home_team_id
                possession['turnover'] = True
                self._assign_duration(row, possession)
                return foul_row, self._new_possession(foul_row)
            elif self._is_actionable(row):
                logger.warning(f'Unable to find final free throw associated with foul in game {foul_row.GAME_ID}, event {foul_row.EVENTNUM}')
                self._assign_duration(foul_row, possession)
                return row, self._new_possession(foul_row)
            row = next(self._rows)

    def _find_rebound(self, shot_row, possession):
        """Treat fouls during a rebounding event as a rebound"""
        shooting_team = shot_row.PLAYER1_TEAM_ID
        row = next(self._rows)
        while True:
            if self._is_reb(row):
                possession['reboundable'] = True
                possession['oreb'] = self._is_oreb(row, shooting_team)
                self._assign_duration(row, possession)
                return next(self._rows), self._new_possession(row)
            elif self._is_foul(row):
                possession['reboundable'] = True
                possession['oreb'] = not self._is_oreb(row, shooting_team)  # Player 1 is fouler, so other team gets the ball
                self._assign_duration(row, possession)
                if self._is_actionable(row):
                    # This foul has fts, so it both ends this possession and the next
                    return row, self._new_possession(row)
                else:
                    return next(self._rows), self._new_possession(row)
            elif self._is_end_of_period(row):
                self._assign_duration(row, possession)
                return next(self._rows), self._new_possession(row)
            elif self._is_actionable(row):
                logger.warning(f'Unable to find rebound associated with missed shot in game {shot_row.GAME_ID}, event {shot_row.EVENTNUM}')
                self._assign_duration(shot_row, possession)
                return row, self._new_possession(shot_row)
            row = next(self._rows)
            

    @staticmethod
    def _is_make(row):
        return row.EVENTMSGTYPE == 1

    @staticmethod
    def _is_three(row):
        return ' 3PT ' in row.DESCRIPTION

    @staticmethod
    def _is_miss(row):
        return row.EVENTMSGTYPE == 2

    @staticmethod
    def _is_fta(row):
        if row.EVENTMSGTYPE != 3:
            return False
        return row.EVENTMSGACTIONTYPE not in {16, 21, 22}  # ignore technicals

    @staticmethod
    def _is_ftm(row):
        # WARNING: Only use after confirming it is a fta
        return row.SCOREMARGIN is not None

    @staticmethod
    def _is_first_fta(row):
        # WARNING: Only use after confirming it is a fta
        return row.EVENTMSGACTIONTYPE in {10, 11, 13, 18, 20, 21, 25, 27}

    @staticmethod
    def _is_final_fta(row):
        # WARNING: Only use after confirming it is a fta
        return row.EVENTMSGACTIONTYPE in {10, 12, 15, 19, 20, 22, 26, 29}

    @staticmethod
    def _num_fts(row):
        # WARNING: Only use after confirming it is a fta
        if row.EVENTMSGACTIONTYPE in {10, 20}:
            return 1
        if row.EVENTMSGACTIONTYPE in {11, 12, 18, 19, 21, 22, 25, 26}:
            return 2
        return 3

    @staticmethod
    def _is_reb(row):
        return row.EVENTMSGTYPE == 4

    @staticmethod
    def _is_oreb(row, shooting_team):
        # WARNING: Only use after confirming it is a reb
        return (shooting_team == row.PLAYER1_TEAM_ID) or (shooting_team == row.PLAYER1_ID)

    @staticmethod
    def _is_turnover(row):
        return row.EVENTMSGTYPE == 5

    @staticmethod
    def _is_foul(row):
        return row.EVENTMSGTYPE == 6

    @classmethod
    def _is_shooting_foul(cls, row):
        if not cls._is_foul(row):
            return False
        return row.EVENTMSGACTIONTYPE in {2, 29}  # shooting foul, shooting block foul

    @classmethod
    def _is_foul_with_fts(cls, row):
        if not cls._is_foul(row):
            return False
        if row.EVENTMSGACTIONTYPE in {26, 11}:  # charges never, and we ignore technicals
            return False
        if row.EVENTMSGACTIONTYPE in {5, 6, 9, 14, 15}:  # Inbound, clear-path, flagrant 1/2 always
            return True
        return '.PN)' in row.DESCRIPTION  # only team-fouls in the penalty

    @staticmethod
    def _is_jump_ball(row):
        return row.EVENTMSGTYPE == 10

    @staticmethod
    def _is_end_of_period(row):
        return row.EVENTMSGTYPE == 13

    @classmethod
    def _is_actionable(cls, row):
        return (
            cls._is_turnover(row) or
            cls._is_make(row) or
            cls._is_miss(row) or
            cls._is_shooting_foul(row) or
            cls._is_foul_with_fts(row) or
            cls._is_end_of_period(row)
        )

def clock_to_seconds_remaining(clock_str):
    minutes, seconds = clock_str.split(':')
    return int(minutes) * 60 + int(seconds)
