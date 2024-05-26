import pandas as pd
from pymongo import MongoClient
from config import Config

class DeviationDetector:
    def __init__(self, anomaly_start_date, anomaly_end_date, analyze_period):
        self.client = MongoClient(Config.CONNECTION_STRING)
        self.db = self.client[Config.DATABASE_NAME]
        self.collection = self.db[Config.ITEM_COLLECTION_NAME]
        self.anomaly_collection = self.db[Config.DEVIATION_ANANLYSIS_COLLECTION_NAME]
        self.anomaly_start_date = pd.to_datetime(anomaly_start_date)
        self.anomaly_end_date = pd.to_datetime(anomaly_end_date)
        self.analyze_period = analyze_period
        self.threshold = 3
        

    def generate_anomaly_reason(self,row):
        item = row['item']
        cost_deviation = row['cost_deviation']
        date = row['date']

        if cost_deviation >= 3:
            return f"For Item '{item}' on {date.strftime('%Y-%m-%d')}, the cost indicates more than usual spending."
        elif cost_deviation <= -3:
            return f"For Item '{item}' on {date.strftime('%Y-%m-%d')}, the cost indicates less than usual spending."
        else:
            return f"For Item '{item}' on {date.strftime('%Y-%m-%d')}, the cost is at the average level."


    def detect_anomalies(self):
        past_start_date = self.anomaly_start_date - pd.DateOffset(days=self.analyze_period)
        cursor = self.collection.find({"date": {"$gte": past_start_date, "$lte": self.anomaly_end_date}})
        data = list(cursor)
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['item', 'date', 'cost'])
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by=['date'],ascending=False,inplace=True)
        df.reset_index(drop=True,inplace=True)
        group = df.groupby('item').agg(['mean', 'std'])['cost'].reset_index()
        costs = df.merge(group, on=['item'],suffixes=('','_grouped'))
        costs['cost_deviation'] = (costs['cost'] - costs['mean']) / costs['std']
        item_anomalies = costs[
            (costs['cost_deviation'].abs() > self.threshold)&
            (costs['date'] >= self.anomaly_start_date) & 
            (costs['date'] <= self.anomaly_end_date)]
        item_anomalies['anomaly_reason'] = item_anomalies.apply(self.generate_anomaly_reason, axis=1).reset_index()
        anomalies = item_anomalies[['item', 'date','cost','anomaly_reason']]
        # Insert cost anomalies into DB
        if not anomalies.empty:
            self.anomaly_collection.insert_many(anomalies.to_dict(orient='records'))
            return anomalies
        else:
            return None
        
        



