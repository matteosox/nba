import pandas as pd

from pbpstats.resources.enhanced_pbp import FieldGoal, FreeThrow, Rebound, Turnover


def parse_season(client, league, year, season_type):
    season = client.Season(league, year, season_type)
    return pd.concat(
        [parse_game(client, game_data, league, year, season_type) for game_data in season.games.final_games],
        ignore_index=True,
    )


def parse_game(client, game_data, league, year, season_type):
    game = client.Game(game_data['game_id'])
    possessions_data = pd.DataFrame(parse_possession(possession) for possession in game.possessions.items)
    possessions_data['possession_num'] = possessions_data.index
    possessions_data['game_id'] = game_data['game_id']
    possessions_data['date'] = game_data['date']
    possessions_data['home_team_id'] = game_data['home_team_id']
    possessions_data['visitor_team_id'] = game_data['visitor_team_id']
    possessions_data['status'] = game_data['status']
    possessions_data['league'] = league
    possessions_data['year'] = int(year[:4]) + 1
    possessions_data['season_type'] = season_type
    return possessions_data


def parse_possession(possession):
    off_team_id = possession.offense_team_id
    current_players = possession.events[0].current_players
    def_team_id = [a for a in current_players if a != off_team_id][0]
    row = {
        'off_team_id': off_team_id,
        'def_team_id': def_team_id,
        'period': possession.period,
        'start_time': clock_to_seconds_remaining(possession.start_time),
        'end_time': clock_to_seconds_remaining(possession.end_time),
        'start_score_margin': possession.start_score_margin,
    }
    row['duration'] = row['start_time'] - row['end_time']
    row.update({f'off_player{ind}': player_id for ind, player_id in enumerate(current_players[off_team_id])})
    row.update({f'def_player{ind}': player_id for ind, player_id in enumerate(current_players[def_team_id])})
    row.update(parse_events(possession.events))
    return row


def parse_events(events):
    subrow = {
        'threes_attempted': 0,
        'threes_made': 0,
        'twos_attempted': 0,
        'twos_made': 0,
        'ft_attempted': 0,
        'ft_made': 0,
        'off_rebs': 0,
        'def_rebs': 0,
        'turnovers': 0,
        'points_scored': 0,
    }
    for event in events:
        if isinstance(event, FieldGoal):
            if event.shot_value == 2:
                subrow['twos_attempted'] += 1
                if event.is_made:
                    subrow['twos_made'] += 1
                    subrow['points_scored'] += 2
            else:
                subrow['threes_attempted'] += 1
                if event.is_made:
                    subrow['threes_made'] += 1
                    subrow['points_scored'] += 3
        elif isinstance(event, FreeThrow):
            if not event.is_technical_ft:
                subrow['ft_attempted'] += 1
                if event.is_made:
                    subrow['ft_made'] += 1
                    subrow['points_scored'] += event.shot_value
        elif isinstance(event, Rebound):
            if event.is_real_rebound:
                if event.oreb:
                    subrow['off_rebs'] += 1
                else:
                    subrow['def_rebs'] += 1
        elif isinstance(event, Turnover):
            if not event.is_no_turnover:
                subrow['turnovers'] += 1
    return subrow


def clock_to_seconds_remaining(clock_str):
    minutes, seconds = clock_str.split(':')
    return int(minutes) * 60 + int(seconds)
