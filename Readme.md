## Some Definitions
### Deviation Analysis:
"Detect anomalies based on cost deviations from expected values within the specified analysis period."

### Anomaly Segmentation:
"Segment anomalies based on deviations from expected values within the specified analysis period."

## Package Contents

### 1. main.py
`main.py` contains a Flask API for detecting cost anomalies. To run the Flask API, simply execute `main.py`.

### 2. API Usage
To detect anomalies, send a JSON payload to the Flask API endpoint.

#### Endpoint:
```
POST /detect_anomalies
```

#### Payload Examples:

##### For Deviation Analysis:
```json
{
    "method": "deviation_analysis",
    "anomaly_start_date": "2024-03-22",
    "anomaly_end_date": "2024-04-18",
    "analysis_period": "12"
}
```

##### For Anomaly Segmentation:
```json
{
    "method": "anomaly_segmentation",
    "anomaly_start_date": "2024-03-22",
    "anomaly_end_date": "2024-04-18",
    "analysis_period": "12"
}
```

### 3. config.py
`config.py` defines configuration parameters for connecting to MongoDB and specifies collection names for anomaly detection results.

## Running the Application
1. Ensure you have all the required dependencies installed. You can install them using:
    ```sh
    pip install -r requirements.txt
    ```
2. Make sure your MongoDB instance is running and properly configured in `config.py`.
3. Run the Flask API:
    ```sh
    python main.py
    ```

## Example
Here is how you can use curl to send a request to the API:

```sh
curl -X POST http://localhost:5009/detect_anomalies -H "Content-Type: application/json" -d '{
    "method": "deviation_analysis",
    "anomaly_start_date": "2024-03-22",
    "anomaly_end_date": "2024-04-18",
    "analysis_period": "12"
}'
```

## Configuration
Make sure to set up your `config.py` with the appropriate MongoDB connection string and collection names. Example `config.py`:

```python
class Config:
    CONNECTION_STRING = "your_mongo_connection_string"
    DATABASE_NAME = "your_database_name"
    ITEM_COLLECTION_NAME = "your_item_collection_name"
    DEVIATION_ANALYSIS_COLLECTION_NAME = "deviation_analysis_results"
    ANOMALY_SEGMENTATION_COLLECTION_NAME = "anomaly_segmentation_results"
```

## Notes
- The `analysis_period` should be specified as an integer representing the number of days to analyze.
- Dates should be in the format `YYYY-MM-DD`.
