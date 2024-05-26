import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
from config import Config

class SegmentationDetector:
    def __init__(self, anomaly_start_date, anomaly_end_date, analysis_period):
        self.client = MongoClient(Config.CONNECTION_STRING)
        self.db = self.client[Config.DATABASE_NAME]
        self.collection = self.db[Config.ITEM_COLLECTION_NAME]
        self.anomaly_start_date = pd.to_datetime(anomaly_start_date)
        self.anomaly_end_date = pd.to_datetime(anomaly_end_date)
        self.analysis_period = analysis_period
        self.cost_deviation_limit = 0.01
        self.segmentation_collection = self.db[Config.ANOMALY_SEGMENTATION_COLLECTION_NAME]

    def generate_anomaly_reason(self, row):
        item = row['item']
        date = row['date']
        reason = f"For item '{item}' on {date.strftime('%Y-%m-%d')}, emphasizing the most extreme spending behavior."
        anomaly_reason = f"Anomaly detection prioritizes the top {self.cost_deviation_limit * 100:.0f}% of spending items. {reason}"
        return anomaly_reason

    def detect_anomalies(self):
        past_start_date = self.anomaly_start_date - pd.DateOffset(days=self.analysis_period)
        cursor = self.collection.find({"date": {"$gte": past_start_date, "$lte": self.anomaly_end_date}})
        data = list(cursor)
        # Convert to DataFrame
        df = pd.DataFrame(data, columns=['item', 'date', 'cost'])
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by='date', ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        anomalies = pd.DataFrame(columns=['item', 'date', 'cost', 'anomaly_reason'])

        for item, group in df.groupby('item'):
            segmentation = IsolationForest(contamination=self.cost_deviation_limit)
            group['anomaly_score'] = segmentation.fit_predict(group[['cost']])
            item_anomalies = group[group['anomaly_score'] == -1]
            item_anomalies.loc[:, 'anomaly_reason'] = item_anomalies.apply(self.generate_anomaly_reason, axis=1)
            anomalies = pd.concat([anomalies, item_anomalies[['item', 'date', 'cost', 'anomaly_reason']]])      
        # Insert anomalies into DB
        if not anomalies.empty:
            self.segmentation_collection.insert_many(anomalies.to_dict(orient='records'))
            return anomalies
        else:
            return None
