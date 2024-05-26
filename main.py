from flask import Flask, request, jsonify
from anomalies.deviation_analysis import DeviationDetector
from anomalies.anomaly_segmentation import SegmentationDetector
class AnomalyDetectorAPI:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/detect_anomalies', methods=['POST'])
        def detect_cost_anomaly():
            data = request.json
            method = data.get('method')
            analysis_period = int(data.get('analysis_period'))

            if method == 'deviation_analysis':
                anomaly_start_date = data.get('anomaly_start_date')
                anomaly_end_date = data.get('anomaly_end_date')
                detector = DeviationDetector(anomaly_start_date, anomaly_end_date, analysis_period)
                anomalies_detected = detector.detect_anomalies()
            elif method == 'anomaly_segmentation':
                anomaly_start_date = data.get('anomaly_start_date')
                anomaly_end_date = data.get('anomaly_end_date')
                detector = SegmentationDetector(anomaly_start_date, anomaly_end_date, analysis_period)
                anomalies_detected = detector.detect_anomalies()
            else:
                return jsonify({'error': 'Invalid method specified'}), 400

            if not anomalies_detected.empty:
                return jsonify({'message': 'Anomalies detected successfully'}), 200
            else:
                return jsonify({'message': 'No anomalies detected'}), 200


    def run(self):
        self.app.run(debug=True, port=5009)

if __name__ == "__main__":
    api = AnomalyDetectorAPI()
    api.run()
