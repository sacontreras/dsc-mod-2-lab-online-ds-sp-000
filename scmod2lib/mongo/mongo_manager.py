import pymongo
import matplotlib.image as mpimg
import os
from bson.binary import Binary
import pickle
import matplotlib.pyplot as plt
from ..utils import *
from ..web import dark_sky as ds

class Team:
    def __init__(self, name, season=None, games_played=0, wins=0, goals_for=0, goals_against=0):
        self.name = name
        self.season = season
        self.games_played = games_played
        self.wins = wins
        self.goals_for = goals_for
        self.goals_against = goals_against

    def to_dict(self):
        return {
            'name': self.name
            , 'season': self.season
            , 'games_played': self.games_played
            , 'wins': self.wins
            , 'goals_for': self.goals_for
            , 'goals_against': self.goals_against
        }

class MongoDBManager:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        self.db = self.client['mod2_summative_lab_db']
        self.team_collection = self.db['team_collection']
        self.image_collection = self.db['image_collection']
        self.weather_collection = self.db['weather_collection']

    # since this falls outside of standard read/write mongodb ops, 
    #   since it involves encoding, we place the code here in this
    #   helper function, since the code is not so straightforwardd
    #   at first sight
    def save_or_update_img(self, fig, fn_img):
        fig.savefig(fn_img)
        img_raw = mpimg.imread(fn_img)
        os.remove(fn_img)
        img_record = {
            'img': fn_img
            , 'bin': Binary(pickle.dumps(img_raw, protocol=2), subtype=128)
        }
        insertion_result = self.image_collection.insert_one(img_record)
        print(f"inserted {fn_img} record into MongoDB image_collection with id: {insertion_result.inserted_id}")

    def load_img(self, fn_img):
        d_find_img_record = {'img': fn_img}
        q_find_img = self.image_collection.find(d_find_img_record)
        for img_record in q_find_img:
            print(f"image {d_find_img_record} found")
            img_raw = pickle.loads(img_record['bin'])
            return plt.imshow(img_raw)

    def update_weather_via_dsapi(self, dates_df):
        keys = get_keys("/Users/stevencontreras/.secret/dark_sky_api.json") # REMEBER TO DELETE THIS LINE BEFORE CHECK-IN!
        api_key = keys['api_key']
        dsapi = ds.DSAPI(api_key)

        #coords for Berlin, Germany: 52.520008, 13.404954 (lat, lon)
        loc_berlin = (52.520008, 13.404954)

        dates_df['weather_complete_json'] = None
        dates_df['weather_simple'] = None

        for idx, distinct_date in dates_df.iterrows():
            date = distinct_date[0].split('-')
            response = dsapi.get_weather(
                loc_berlin[0]
                , loc_berlin[1]
                , date[0]
                , date[1]
                , date[2]
            )
            response_json = response.json()
            daily_data_json = response_json['daily']['data'][0]
            record_to_update = {'date':  date}
            d_update = {
                'response': response.text
                , 'simple': daily_data_json['icon'] if 'icon' in daily_data_json else None
            }
            update = {'$set': d_update}
            self.weather_collection.update_one(record_to_update, update)

            dates_df.loc[idx, 'weather_complete_json'] = d_update['response']
            dates_df.loc[idx, 'weather_simple'] = d_update['simple']
        
        return dates_df