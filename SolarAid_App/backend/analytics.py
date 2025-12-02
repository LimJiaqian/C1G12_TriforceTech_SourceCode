import pandas as pd
import math

class DonationAnalytics:

    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.monthly = None
        self.latest_year = None
        self.df_year = None
        self.donors = None

    # -------------------------------
    # 1. Load donations and aggregate monthly totals
    # -------------------------------
    def load_data(self):
        df = pd.read_csv(self.csv_path)
        df['Transaction_Time'] = pd.to_datetime(df['Transaction_Time'])
        df['year_month'] = df['Transaction_Time'].dt.to_period('M')
        # Ensure Donor_ID is integer
        df['Donor_ID'] = df['Donor_ID'].astype(int)
        self.df = df

        # Load full donor info
        self.donors = pd.read_csv("backend/dataset/donors.csv")
        # Ensure User_ID is integer
        self.donors['User_ID'] = self.donors['User_ID'].astype(int)

        # Make lookup fast
        self.donors.set_index("User_ID", inplace=True)

        # find the latest year in the data
        self.latest_year = self.df['Transaction_Time'].dt.year.max()

        # filter data for the latest year
        self.df_year = self.df[self.df['Transaction_Time'].dt.year == self.latest_year]

        # monthly totals per donor
        self.monthly = (
            self.df.groupby(['Donor_ID', 'year_month'])['Donation_Amount_kWh']
              .sum()
              .reset_index()
        )

    def get_donor_info(self, user_id):
        try:
            info = self.donors.loc[user_id]
            return {
                'user_id': user_id,
                "User_Name": info["User_Name"],
                "User_Img": info["User_Img"],
                "Area": info["Area"],
                "District": info["District"],
                "State": info["State"],
                "Postcode": int(info["Postcode"]),
                "Region": info["Region"]
            }
        except KeyError:
            return {
                'user_id': user_id,
                "User_Name": "Unknown",
                "User_Img": "",
                "Area": None,
                "District": None,
                "State": None,
                "Postcode": None,
                "Region": None
            }

    # -------------------------------
    # 2. Get latest leaderboard
    # -------------------------------
    def get_latest_leaderboard(self):
        if self.df.empty:
            return pd.DataFrame()  
        
        # sum donations per donor for the year
        leaderboard = self.df_year.groupby('Donor_ID')['Donation_Amount_kWh'] \
                    .sum() \
                    .reset_index() \
                    .sort_values('Donation_Amount_kWh', ascending=False)
        
        # Add ranking column (1-based)
        leaderboard['Rank'] = range(1, len(leaderboard) + 1)
    
    
         # Merge donor info (User_Name and User_Img)
        donor_info_df = self.donors[['User_Name', 'User_Img']].copy()
        donor_info_df.index.name = 'Donor_ID'  
        donor_info_df.reset_index(inplace=True)
        # Ensure Donor_ID is integer type for merge
        donor_info_df['Donor_ID'] = donor_info_df['Donor_ID'].astype(int)
        leaderboard['Donor_ID'] = leaderboard['Donor_ID'].astype(int)

        leaderboard = leaderboard.merge(donor_info_df, on='Donor_ID', how='left')

        # Reorder and rename columns for API output
        leaderboard = leaderboard[['Rank', 'Donor_ID', 'User_Name', 'User_Img', 'Donation_Amount_kWh']]
        leaderboard.rename(columns={
            'Donation_Amount_kWh': 'total_Donation_Amount_kWh' 
        }, inplace=True)

        print(f"Leaderboard for latest year ({self.latest_year}):")
        print(leaderboard)
        return leaderboard
    
    # -------------------------------
    # 3. Get user ranking
    # -------------------------------
    def get_user_position(self, user_id):
        user_id = int(user_id)
        leaderboard = self.get_latest_leaderboard().reset_index(drop=True)

        if leaderboard.empty:
            return None

        total_donors = len(leaderboard)

        # ----------------------------
        # 1. Find 5th place threshold
        # ----------------------------
        kWh_5th_place = float(leaderboard.iloc[4]['total_Donation_Amount_kWh']) if total_donors >= 5 else 0 

        # ----------------------------
        # 2. Find the user row
        # ----------------------------
        user_row = leaderboard[leaderboard['Donor_ID'] == user_id]

        if user_row.empty:
            # User has no donations
            return {
                'user_id': user_id,
                'User_Name': None,
                'User_Img': "",
                'Rank': None,
                'total_Donation_Amount_kWh': 0,
                'total_donors': total_donors,
                'kWh_needed_for_top_5': math.ceil(max(kWh_5th_place + 0.1, 0)),
                'message': 'No donations in current year'
            }

        user_rank = int(user_row['Rank'].values[0]) 
        user_total = float(user_row['total_Donation_Amount_kWh'].values[0])  

        # ----------------------------
        # 3. Calculate needed for top 5
        # ----------------------------
        if user_rank <= 5:
            kWh_needed = 0  # Already top 5
        else:
            kWh_needed = max(kWh_5th_place - user_total + 0.1, 0)

        # ----------------------------
        # 4. Build output
        # ----------------------------
        position_info = {
            'user_id': user_id,
            'User_Name': user_row['User_Name'].values[0],
            'User_Img': user_row['User_Img'].values[0],
            'Rank': user_rank,
            'total_Donation_Amount_kWh': user_total,
            'total_donors': total_donors,
            'kWh_needed_for_top_5': math.ceil(kWh_needed),
            'message': None
        }

        print(f"User {user_id} rank {user_rank}/{total_donors}, needs {kWh_needed} kWh to enter top 5")
        return position_info


    # -------------------------------
    # 4. Get previous ranker in the latest leaderboard
    # -------------------------------
    def get_previous_ranker(self, user_id):
        leaderboard = self.get_latest_leaderboard().reset_index(drop=True)
        if leaderboard.empty:
            return None
        user_id = int(user_id)
        user_row = leaderboard[leaderboard['Donor_ID'] == user_id]
        
        if user_row.empty:
           # User not ranked -> return top donor
            top_row = leaderboard.iloc[0]
            return {
                'user_id': int(top_row['Donor_ID']),
                'User_Name': top_row['User_Name'],
                'User_Img': top_row['User_Img'],
                'total_Donation_Amount_kWh': float(top_row['total_Donation_Amount_kWh'])  
            }

        user_rank = user_row.index[0]
        
        if user_rank == 0:
            # User is already rank 1 - no one to beat!
            return None

        prev_row = leaderboard.iloc[user_rank - 1]

        return {
            'user_id': int(prev_row['Donor_ID']),
            'User_Name': prev_row['User_Name'],
            'User_Img': prev_row['User_Img'],
            'total_Donation_Amount_kWh': float(prev_row['total_Donation_Amount_kWh'])  
        }

    # -------------------------------
    # 5. Get yearly patterns to beat previous ranker
    # -------------------------------
    def get_yearly_patterns(self, user_id, previous_ranker_id):
    
        user_id = int(user_id)

        leaderboard = self.get_latest_leaderboard().reset_index(drop=True)

        if leaderboard.empty:
            return None

        # Get user total 
        user_row = leaderboard[leaderboard['Donor_ID'] == user_id]
        user_total = float(user_row['total_Donation_Amount_kWh'].values[0]) if not user_row.empty else 0

        # User pattern 
        user_df = self.monthly[self.monthly['Donor_ID'] == user_id].copy()
        user_pattern = [
            {"year_month": str(row["year_month"]), "Donation_Amount_kWh": float(row["Donation_Amount_kWh"])}
            for _, row in user_df.sort_values("year_month").iterrows()
        ]

        # User info
        user_info = self.get_donor_info(user_id)

        # Handle rank 1 user 
        if previous_ranker_id is None:
            return {
                "user_info": user_info,
                "user_yearly_pattern": user_pattern,
                "user_total_Donation_Amount_kWh": user_total,
                "previous_ranker_info": None,
                "previous_ranker_yearly_pattern": [],
                "previous_ranker_total_Donation_Amount_kWh": 0,
                "latest_year": int(self.latest_year),
                "message": "You're already rank 1! No one to beat."
            }

        # Previous ranker pattern
        previous_ranker_id = int(previous_ranker_id)
        prev_df = self.monthly[self.monthly['Donor_ID'] == previous_ranker_id].copy()
        
        # Get prev total 
        prev_row = leaderboard[leaderboard['Donor_ID'] == previous_ranker_id]
        prev_total = float(prev_row['total_Donation_Amount_kWh'].values[0]) if not prev_row.empty else 0

        prev_pattern = [
            {"year_month": str(row["year_month"]), "Donation_Amount_kWh": float(row["Donation_Amount_kWh"])}
            for _, row in prev_df.sort_values("year_month").iterrows()
        ]
        # Previous ranker info
        previous_ranker_info = self.get_donor_info(previous_ranker_id)

        return {
            "user_info": user_info,
            "user_yearly_pattern": user_pattern,
            "user_total_Donation_Amount_kWh": user_total,
            "previous_ranker_info": previous_ranker_info,
            "previous_ranker_yearly_pattern": prev_pattern,
            "previous_ranker_total_Donation_Amount_kWh": prev_total,
            "latest_year": int(self.latest_year),
            "message": None
        }
