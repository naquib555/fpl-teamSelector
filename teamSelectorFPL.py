#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 18:22:41 2021

@author: ahmad
"""

import requests
import json
import pandas as pd

##################################
#FPL data URL and storing them to json
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
response_json = r.json()
################################


teams = response_json['teams']
element_types = response_json['element_types']
player_data = response_json['elements']

test_df = pd.DataFrame(player_data)


##################################
#mapping team

team_list = []
team_limit_list = []
for team in teams:
    team_id = {team['code'] : team['name']}
    team_limit_id = {team['name'] : 3}
    
    team_list.append(team_id)
    team_limit_list.append(team_limit_id)

team_dictionary = {}
for team in team_list:
    team_dictionary.update(team)

team_limit_dictionary = {}
for team_limit in team_limit_list:
    team_limit_dictionary.update(team_limit)

#mapping position
position_list = []
for element_type in element_types:
    position_id = {element_type['id'] : element_type['plural_name_short']}
    position_list.append(position_id)

position_dictionary = {}
for position in position_list:
    position_dictionary.update(position)


##################################



##################################
#Filter data and preparing dataframe
wanted_features = ['first_name', 'second_name', 'team_code','element_type','news','now_cost', 'total_points', 'minutes',
                   'form',  'value_season', 'points_per_game', 'value_form',
                    'goals_scored', 'assists', 'dreamteam_count','clean_sheets', 
                   'goals_conceded', 'own_goals','penalties_saved', 'penalties_missed',
                   'yellow_cards', 'red_cards', 'saves', 'bonus',
                   'influence', 'creativity', 'threat', 'ict_index', 'selected_by_percent'
                  ]

# Converting the list of players to a DataFrame
players_df = pd.DataFrame(player_data)
# Choosing only the columns that we want
players_df = players_df[wanted_features]

players_df = players_df.replace({'team_code' : team_dictionary})
players_df = players_df.replace({'element_type' : position_dictionary})

players_df = players_df.rename(columns={'team_code' : 'team', 'element_type' : 'position'})

players_df['player_name'] = players_df['first_name'].str.cat(players_df['second_name'], sep=' ')
players_df = players_df.drop(['first_name', 'second_name'], axis=1)



def unavialable(row):
    if row['news'] != '': 
        return True 
    else:
        return False

players_df['unavailable'] = players_df.apply(lambda row: unavialable(row), axis=1)


players_df = players_df[['player_name', 'team','position','unavailable','now_cost', 'total_points', 'minutes',
                   'form',  'value_season', 'points_per_game', 'value_form',
                    'goals_scored', 'assists', 'dreamteam_count','clean_sheets', 
                   'goals_conceded', 'own_goals','penalties_saved', 'penalties_missed',
                   'yellow_cards', 'red_cards', 'saves', 'bonus',
                   'influence', 'creativity', 'threat', 'ict_index', 'selected_by_percent'
                  ]]

##################################

players_wanted_features = ['player_name', 'team', 'position', 'total_points', 'now_cost', 'unavailable']
most_points = players_df[players_wanted_features]
most_points = most_points.sort_values(by='total_points', ascending=False)

roi_players = players_df[players_wanted_features]
roi_players['roi'] = roi_players.apply(lambda row: row.total_points / row.now_cost, axis=1)
roi_players = roi_players.sort_values(by='roi', ascending=False)

##################################

def choose_team():
    roi_team = []
    squad = []
    
    gkp_squad = []
    def_squad = []
    mid_squad = []
    fwd_squad = []
    
    total_points = 0
    budget = 1000
    top_performer_limit = 3
    position_limit_dictionary = {"GKP": 2, "DEF": 5, "MID": 5, "FWD": 3}
    
    for idx, row in most_points.iterrows():
        if budget >= row.now_cost and len(roi_team) < top_performer_limit and row.unavailable == False and position_limit_dictionary[row.position] != 0 and team_limit_dictionary[row.team] != 0:
            roi_team.append(row.player_name)
            budget -= row.now_cost
            position_limit_dictionary[row.position] -= 1
            team_limit_dictionary[row.team] -= 1
            total_points += row.total_points
            squad.append(row)
            print('Chosen from Top players: ' + str(row.player_name))
        else:
            for idx, row in roi_players.iterrows():
                if row.player_name not in roi_team and budget >= row.now_cost and row.unavailable == False and position_limit_dictionary[row.position] != 0 and team_limit_dictionary[row.team] != 0:
                    roi_team.append(row.player_name)
                    budget -= row.now_cost
                    position_limit_dictionary[row.position] -= 1
                    team_limit_dictionary[row.team] -= 1
                    total_points += row.total_points
                    squad.append(row)

    for row in squad:
        if row.position == 'GKP':
            gkp_squad.append(row.player_name)
        elif row.position == 'DEF':
            def_squad.append(row.player_name)
        elif row.position == 'MID':
            mid_squad.append(row.player_name)
        elif row.position == 'FWD':
            fwd_squad.append(row.player_name)
        
    print("\nTeam chosen: " + str(roi_team))
    print("Remaining Budget: " + str((budget/10)) + "M")
    print("Total points from choosen team: " + str(total_points) + ".")
    print(position_limit_dictionary)
    
    print('GKP: ' + str(gkp_squad))
    print('DEF: ' + str(def_squad))
    print('MID: ' + str(mid_squad))
    print('FWD: ' + str(fwd_squad))


choose_team()
    







