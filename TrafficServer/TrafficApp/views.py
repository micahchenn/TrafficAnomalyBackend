import os
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

@csrf_exempt
def fetch_traffic_data(request):
    TOMTOM_API_KEY = os.environ.get('TOMTOM_API_KEY', ' ')  # Replace with your TomTom API key
    data = json.loads(request.body)
    point = data.get('point', '29.72852,-95.4686')
    historical = data.get('historical', False)
    start_time = data.get('start_time', '2023-01-01T00:00:00Z')
    end_time = data.get('end_time', '2023-12-31T23:59:59Z')

    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={TOMTOM_API_KEY}&point={point}"
    response = requests.get(url)
    print(response.json)
    return JsonResponse(response.json())

def plot_traffic_data(data):
    times = [datetime.strptime(item['time'], "%Y-%m-%dT%H:%M:%SZ") for item in data['flowSegmentData']['historicalData']]
    speeds = [item['currentSpeed'] for item in data['flowSegmentData']['historicalData']]

    plt.figure(figsize=(10, 5))
    plt.plot(times, speeds, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Current Speed')
    plt.title('Historical Traffic Speed')
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return graphic


def detect_anomalies(traffic_data):
    if 'flowSegmentData' not in traffic_data:
        print("Invalid traffic data structure:", traffic_data)  # Debugging print
        return []

    flow_segment = traffic_data['flowSegmentData']
    current_speed = flow_segment['currentSpeed']
    free_flow_speed = flow_segment['freeFlowSpeed']
    confidence = flow_segment['confidence']
    road_closure = flow_segment['roadClosure']
    coordinates = flow_segment['coordinates']['coordinate']

    print(f"Analyzing traffic data - Current Speed: {current_speed}, Free Flow Speed: {free_flow_speed}, Confidence: {confidence}, Road Closure: {road_closure}")

    anomalies = []
    # Simplified anomaly threshold for testing
    threshold = 0.9 * free_flow_speed

    if current_speed < threshold or road_closure:
        anomalies.append({
            'location': coordinates,
            'currentSpeed': current_speed,
            'threshold': threshold,
            'confidence': confidence,
            'roadClosure': road_closure
        })

    print(f"Detected anomalies: {anomalies}")  # Debugging print
    return anomalies
    
@csrf_exempt
def anomaly_detection_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        point = data.get('point')
        historical = data.get('historical', False)
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not point:
            return JsonResponse({'error': 'Point parameter is required'}, status=400)
        
        traffic_data = fetch_traffic_data(point, historical, start_time, end_time)
        if traffic_data:
            anomalies = detect_anomalies(traffic_data)
            if historical:
                plot = plot_traffic_data(traffic_data)
                return JsonResponse({'anomalies': anomalies, 'plot': plot})
            return JsonResponse({'anomalies': anomalies})
        else:
            return JsonResponse({'error': 'Failed to retrieve traffic data'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
