import csv
import os
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime

def clean_data(file_path):
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as new_file:
        writer = csv.writer(new_file, lineterminator='\n')

        with open(file_path, 'r') as input_file:
            reader = csv.reader(input_file)

            headers = next(reader)
            writer.writerow(headers)

            for row in reader:
                if any(not cell for cell in row) or ('Regular Season' not in row):
                    continue

                writer.writerow(row)
   
    os.remove(file_path)
    os.rename(new_file.name, file_path)


def add_int_date(file_path):
    start_date = datetime(2003, 1, 1)
    temp_fd, temp_path = tempfile.mkstemp()

    with open(file_path, 'r', newline='') as input_file, \
         open(temp_fd, 'w', newline='') as temp_file:
        
        reader = csv.reader(input_file)
        writer = csv.writer(temp_file, lineterminator='\n')

        headers = next(reader)
        # Identify all indexes of 'days_after_start' columns
        das_indexes = [i for i, header in enumerate(headers) if header == 'days_after_start']
        
        # Remove any additional 'days_after_start' columns, keep only the first occurrence
        if das_indexes:
            headers = [header for i, header in enumerate(headers) if i not in das_indexes[1:]]
        
        # Add 'days_after_start' if it's not present
        if das_indexes:
            writer.writerow(headers)  # The header already contains one 'days_after_start'
            for row in reader:
                # Remove additional 'days_after_start' data points from rows
                row = [cell for i, cell in enumerate(row) if i not in das_indexes[1:]]
                writer.writerow(row)
        else:
            headers.insert(2, 'days_after_start')
            writer.writerow(headers)
            for row in reader:
                game_date_str = row[1]
                game_date = datetime.strptime(game_date_str, '%Y-%m-%d')
                days_difference = (game_date - start_date).days
                row.insert(2, days_difference)
                writer.writerow(row)

    os.replace(temp_path, file_path)

def make_chronological_order(file_path):
    df = pd.read_csv(file_path)
    
    # Sort the DataFrame by 'days_after_start' in ascending order
    df_sorted = df.sort_values(by='days_after_start', ascending=True)

    # Save the sorted DataFrame back to the original CSV file
    df_sorted.to_csv(file_path, index=False)



# Load the data from CSV file


def calculate_averages(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create dictionaries to store points and points allowed for the last 10 games
    team_points = {}
    team_points_allowed = {}

    # Define a function to calculate the average of the last 10 elements in a list
    def average_last_10(lst):
        return sum(lst[-10:]) / min(len(lst), 10)

    # Iterate over the DataFrame to populate the dictionaries
    for index, row in df.iterrows():
        team_id = row['team_id']
        opp_id = row['a_team_id']
        points = row['pts']
        opp_points = df.at[index, 'pts' if row['is_home'] == 't' else 'pts']

        # Update points and points allowed for each team
        team_points.setdefault(team_id, []).append(points)
        team_points_allowed.setdefault(team_id, []).append(opp_points)
        team_points.setdefault(opp_id, []).append(opp_points)
        team_points_allowed.setdefault(opp_id, []).append(points)

        # Keep only the last 10 games for each team
        if len(team_points[team_id]) > 10:
            del team_points[team_id][0]
            del team_points_allowed[team_id][0]
        if len(team_points[opp_id]) > 10:
            del team_points[opp_id][0]
            del team_points_allowed[opp_id][0]

    # Calculate the new column values
    for index, row in df.iterrows():
        team_id = row['team_id']
        opp_id = row['a_team_id']

        df.at[index, 'l10_ppg'] = average_last_10(team_points[team_id])
        df.at[index, 'opp_l10_ppg'] = average_last_10(team_points[opp_id])
        df.at[index, 'l10_points_allowed'] = average_last_10(team_points_allowed[team_id])
        df.at[index, 'opp_l10_points_allowed'] = average_last_10(team_points_allowed[opp_id])

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)




def reorder_by_team(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Save the reordered DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)

# Now you can call the function with the paths to your input and output CSV files.
reorder_by_team(r'C:\Users\Joseph\Downloads\archive\nba_games_all.csv', r'C:\Users\Joseph\Downloads\archive\sorted_nba_games_all.csv')

# Now you can call the function with the paths to your input and output CSV files.
calculate_averages('nba_games.csv', 'nba_games_with_new_columns.csv')

import pandas as pd
def reorder_by_team(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Save the reordered DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)





import pandas as pd

def add_l10_ppg_column(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['l10_ppg'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['pts'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'l10_ppg'] = rolling_points

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)


import pandas as pd

def add_opp_pts_column(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_pts = pd.Series(df.pts.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp_pts(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp_pts = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['pts'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp_pts[0] if len(opp_pts) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp_pts_series = df.apply(get_opp_pts, axis=1)

    # Find the index of the 'pts' column
    pts_idx = df.columns.get_loc('pts')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(pts_idx + 1, 'opp_pts', opp_pts_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)





def add_l10_opp_ppg(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['game_date'] = pd.to_datetime(df['game_date'])

    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    df_sorted['opp_l10_ppg'] = float('nan')

    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        rolling_points = team_games['opp_pts'].shift(1).rolling(window=10, min_periods=1).mean()
        
        df_sorted.loc[team_games.index, 'opp_l10_ppg'] = rolling_points

    df_sorted.to_csv(output_csv, index=False)



import pandas as pd

def add_l10_fg_pct(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['l10_fg_pct'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['fg_pct'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'l10_fg_pct'] = rolling_points.round(3)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

# Function to round l10_ppg and opp_l10_ppg to the nearest tenth
def round_ppg_columns(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Round the 'l10_ppg' and 'opp_l10_ppg' columns to one decimal place
    df['l10_ppg'] = df['l10_ppg'].round(1)
    df['opp_l10_ppg'] = df['opp_l10_ppg'].round(1)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)



import pandas as pd


def add_l10_fg3_pct(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['l10_fg3_pct'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['fg3_pct'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'l10_fg3_pct'] = rolling_points.round(3)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)


import pandas as pd


def add_opp_fg_pct(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_pts = pd.Series(df.fg_pct.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp_fg_pct(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp_fg_pct = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['fg_pct'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp_fg_pct[0] if len(opp_fg_pct) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp_fg_pct_series = df.apply(get_opp_fg_pct, axis=1)

    # Find the index of the 'pts' column
    fg_pct_idx = df.columns.get_loc('fg_pct')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(fg_pct_idx + 1, 'opp_gf_pct', opp_fg_pct_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)


import pandas as pd


def add_opp_fg3_pct(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_pts = pd.Series(df.fg3_pct.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp_fg3_pct(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp_fg3_pct = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['fg3_pct'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp_fg3_pct[0] if len(opp_fg3_pct) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp_fg3_pct_series = df.apply(get_opp_fg3_pct, axis=1)

    # Find the index of the 'pts' column
    fg3_pct_idx = df.columns.get_loc('fg3_pct')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(fg3_pct_idx + 1, 'opp_fg3_pct', opp_fg3_pct_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)




import pandas as pd


def add_opp_l10_fg_pct(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['opp_l10_fg_pct'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['opp_fg_pct'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'opp_l10_fg_pct'] = rolling_points.round(3)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd


def add_opp_l10_fg3_pct(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['opp_l10_fg3_pct'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['opp_fg3_pct'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'opp_l10_fg3_pct'] = rolling_points.round(3)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

def add_opp_tov(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_pts = pd.Series(df.tov.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp_tov(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp_tov = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['tov'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp_tov[0] if len(opp_tov) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp_tov_series = df.apply(get_opp_tov, axis=1)

    # Find the index of the 'pts' column
    tov_idx = df.columns.get_loc('tov')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(tov_idx + 1, 'opp_tov', opp_tov_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)



import pandas as pd

def add_l10_tov(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['l10_tov'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_points = team_games['tov'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'l10_tov'] = rolling_points.round(1)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

def add_opp_l10_tov(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['opp_l10_tov'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_tov = team_games['opp_tov'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'opp_l10_tov'] = rolling_tov.round(1)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

def add_net_wins(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['net_wins'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        net_wins = team_games['w']-team_games['l']

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'net_wins'] = net_wins

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

def add_opp_net_wins(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_net_wins = pd.Series(df.tov.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp_net_wins(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp_net_wins = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['net_wins'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp_net_wins[0] if len(opp_net_wins) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp_net_wins_series = df.apply(get_opp_net_wins, axis=1)

    # Find the index of the 'pts' column
    net_wins_idx = df.columns.get_loc('net_wins')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(net_wins_idx + 1, 'opp_net_wins', opp_net_wins_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)




import pandas as pd

def add_l10_opp_net_wins(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['l10_opp_net_wins'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        rolling_opp_net_wins = team_games['opp_net_wins'].shift(1).rolling(window=10, min_periods=1).mean()

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'l10_opp_net_wins'] = rolling_opp_net_wins.round(1)

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



#Desired parameters include: is_home,l10_ppg,opp_l10_ppg,l10_fg_pct,l10_fg3_pct,opp_l10_fg_pct,opp_l10_fg3_pct,l10_tov,opp_l10_tov,net_wins,l10_opp_net_wins,win_differential,opp1_l10_ppg, opp1_l10_fg_pct, opp1_l10fg3_pct, opp2_l10_ppg, opp2_l10_fg_pct, opp2_l10fg3_pct, opp1_l10_tov, opp2_l10_tov, opp_l10_opp_net_wins




import pandas as pd

def add_win_differential(input_csv_path, output_csv_path):
    
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Convert 'game_date' to datetime for proper chronological sorting
    df['game_date'] = pd.to_datetime(df['game_date'])

    # Sort the DataFrame by 'team_id' and within each team by 'game_date'
    df_sorted = df.sort_values(by=['team_id', 'game_date'])

    # Initialize a new column for l10_ppg with default NaN values
    df_sorted['win_differential'] = float('nan')

    # Calculate the rolling average for the last 10 games for each team excluding the current game
    for team_id in df_sorted['team_id'].unique():
        team_games = df_sorted[df_sorted['team_id'] == team_id]

        # Calculate the rolling average of points scored, using min_periods=1 to include all available games
        # We shift the rolling window by 1 to exclude the current game
        win_differential = team_games['net_wins']-team_games['opp_net_wins']

        # Assign the computed values to the appropriate locations in the DataFrame
        df_sorted.loc[team_games.index, 'win_differential'] = win_differential

    # Save the updated DataFrame to a new CSV file
    df_sorted.to_csv(output_csv_path, index=False)



import pandas as pd

def add_opp_pts_column(input_csv_path, output_csv_path):
    # Load the data from CSV file
    df = pd.read_csv(input_csv_path)

    # Create a dictionary to map game_id to pts for quick lookup
    game_id_to_pts = pd.Series(df.l10_opp_net_wins.values, index=df.game_id).to_dict()

    # Function to get the opponent's pts
    def get_opp1_l10_ppg(row):
        # Find the game_id and the opponent's team_id
        game_id = row['game_id']
        opp_team_id = row['a_team_id']
        
        # Find the row for the opponent team using the game_id and opponent team_id
        opp1_l10_ppg = df[(df['game_id'] == game_id) & (df['team_id'] == opp_team_id)]['l10_opp_net_wins'].values
        
        # Return the opponent's points if it's found, otherwise return NaN
        return opp1_l10_ppg[0] if len(opp1_l10_ppg) > 0 else float('nan')

    # Apply the function to each row of the DataFrame and store the result in a new 'opp_pts' series
    opp1_l10_ppg_series = df.apply(get_opp1_l10_ppg, axis=1)

    # Find the index of the 'pts' column
    end_idx = df.columns.get_loc('win_differential')

    # Insert the new 'opp_pts' series into the DataFrame right after 'pts'
    df.insert(end_idx + 1, 'opp_l10_opp_net_wins', opp1_l10_ppg_series)

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_csv_path, index=False)

import pandas as pd

def remove_features_and_save_new_file(original_csv_path, features_to_remove, new_csv_path):
    """
    Removes specified features from a CSV file and saves the result to a new file.

    Parameters:
    original_csv_path (str): The file path for the original CSV file.
    features_to_remove (list): A list of strings representing the feature names to remove.
    new_csv_path (str): The file path to save the new CSV file with irrelevant features removed.
    """

    # Load the original data
    df = pd.read_csv(original_csv_path)

    # Check if the features to remove are in the DataFrame
    for feature in features_to_remove:
        if feature not in df.columns:
            raise ValueError(f"Feature '{feature}' not found in the DataFrame.")

    # Drop the irrelevant features
    df = df.drop(features_to_remove, axis=1)

    # Save the new DataFrame without the irrelevant features to a new CSV file
    df.to_csv(new_csv_path, index=False)

    print(f"File saved successfully to {new_csv_path}")

# Example usage:

import pandas as pd

def shift_team_stats(csv_path, output_path):
    # Load CSV data into a DataFrame
    df = pd.read_csv(csv_path)

    # Sort the DataFrame by team and date to ensure the shift operation is applied correctly
    df.sort_values(by=['team_id', 'game_date'], inplace=True)

    # Shift the 'w', 'l', and 'w_pct' columns for each team and overwrite the original columns
    df['w'] = df.groupby('team_id')['w'].shift(1)
    df['l'] = df.groupby('team_id')['l'].shift(1)
    df['w_pct'] = df.groupby('team_id')['w_pct'].shift(1)

    # Save the updated DataFrame to a CSV file
    df.to_csv(output_path, index=False)



# Example usage:

import csv

def merge_csv_columns(first_csv_path, second_csv_path, output_csv_path):
    # Read data from the first CSV and store the required fields in a dictionary
    first_csv_data = {}
    with open(first_csv_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            game_id = row['game_id']
            first_csv_data[game_id] = {
                'net_wins': row['net_wins'],
                'opp_net_wins': row['opp_net_wins'],
                'l10_opp_net_wins': row['l10_opp_net_wins'],
                'win_differential': row['win_differential'],
                'opp_l10_opp_net_wins': row['opp_l10_opp_net_wins']
            }

    # Now read the second CSV, update the data, and write to the output CSV
    with open(second_csv_path, mode='r', newline='', encoding='utf-8') as csvfile, \
         open(output_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            game_id = row['game_id']
            if game_id in first_csv_data:
                # Update the row with the data from the first CSV
                row.update(first_csv_data[game_id])
            writer.writerow(row)

    print(f'Merged CSV has been created as {output_csv_path}')

# Example usage:
first_csv_file = r'C:\Users\Joseph\Downloads\archive\sorted_l10ah.csv'
second_csv_file = r'C:\Users\Joseph\Downloads\archive\sorted_l10ai.csv'
output_csv_file = r'C:\Users\Joseph\Downloads\archive\FINALLY.csv'




import csv

def remove_second_instance(input_filename, output_filename):
    with open(input_filename, 'r', newline='', encoding='utf-8') as infile, \
         open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        
        writer.writeheader()
        seen_game_ids = set()
        
        for row in reader:
            game_id = row['game_id']
            
            if game_id not in seen_game_ids:
                # Write the row if the game_id has not been seen yet
                writer.writerow(row)
                # Add the current game_id to the set of seen ids
                seen_game_ids.add(game_id)

# Use the function with your file names




remove_second_instance(r'C:\Users\Joseph\Downloads\archive\FINALLY.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10am.csv')

merge_csv_columns(first_csv_file, second_csv_file, output_csv_file)

shift_team_stats(r'C:\Users\Joseph\Downloads\archive\sorted_l10l.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10ac.csv')

remove_features_and_save_new_file(r'C:\Users\Joseph\Downloads\archive\sorted_l10aa.csv', ['game_id','game_date','days_after_start','matchup','team_id','w','l','w_pct','min','fgm','fga','fg_pct','opp_fg_pct','fg3m','fg3a','fg3_pct','opp_fg3_pct','ftm','fta','ft_pct','oreb','dreb','reb','ast','stl','blk','tov','opp_tov','pf','pts','opp_pts','a_team_id','season_year','season_type','season','net_wins','opp_net_wins'], r'C:\Users\Joseph\Downloads\archive\sorted_l10ab.csv')

add_opp_pts_column(r'C:\Users\Joseph\Downloads\archive\sorted_l10x.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10y.csv')

add_win_differential(r'C:\Users\Joseph\Downloads\archive\sorted_l10o.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10p.csv')

add_l10_opp_net_wins(r'C:\Users\Joseph\Downloads\archive\sorted_l10n.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10o.csv')

add_opp_net_wins(r'C:\Users\Joseph\Downloads\archive\sorted_l10m.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10n.csv')

add_net_wins(r'C:\Users\Joseph\Downloads\archive\sorted_l10l.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10m.csv')

add_opp_l10_tov(r'C:\Users\Joseph\Downloads\archive\sorted_l10k.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10l.csv')

add_l10_tov(r'C:\Users\Joseph\Downloads\archive\sorted_l10j.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10k.csv')

add_opp_tov(r'C:\Users\Joseph\Downloads\archive\sorted_l10i.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10j.csv')

add_opp_l10_fg3_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10h.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10i.csv')

add_opp_l10_fg_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10g.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10h.csv')

add_opp_fg3_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10f.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10g.csv')

add_opp_fg_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10e.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10f.csv')

add_l10_fg3_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10d.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10e.csv')

round_ppg_columns(r'C:\Users\Joseph\Downloads\archive\sorted_l10c.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10d.csv')

add_l10_fg_pct(r'C:\Users\Joseph\Downloads\archive\sorted_l10b.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10c.csv')

# Now you can call the function with the paths to your input and output CSV files.
add_l10_opp_ppg(r'C:\Users\Joseph\Downloads\archive\sorted_l10a.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10b.csv')

# Now you can call the function with the paths to your input and output CSV files.
add_opp_pts_column(r'C:\Users\Joseph\Downloads\archive\sorted_l10_ppg.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10a.csv')

# Now you can call the function with the paths to your input and output CSV files.
add_l10_ppg_column(r'C:\Users\Joseph\Downloads\archive\sorted_nba_games_all.csv', r'C:\Users\Joseph\Downloads\archive\sorted_l10_ppg.csv')

# Now you can call the function with the paths to your input and output CSV files.
reorder_by_team(r'C:\Users\Joseph\Downloads\archive\nba_games_all.csv', r'C:\Users\Joseph\Downloads\archive\sorted_nba_games_all.csv')   

make_chronological_order(r'C:\Users\Joseph\Downloads\archive\nba_games_all.csv')
clean_data(r'C:\Users\Joseph\Downloads\archive\nba_games_all.csv')
add_int_date(r'C:\Users\Joseph\Downloads\archive\nba_games_all.csv')
