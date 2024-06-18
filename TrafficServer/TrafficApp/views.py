from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
import requests

def fetch_traffic_data(point):
    tomtom_api_key = os.getenv('TOMTOM_API_KEY')
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={point}&key={tomtom_api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Traffic data:", data)  # Debugging print
        return data
    else:
        print(f"Error fetching traffic data: {response.status_code}")
        print(response.text)  # Print the error message for debugging
        return None

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
        
        if not point:
            return JsonResponse({'error': 'Point parameter is required'}, status=400)
        
        traffic_data = fetch_traffic_data(point)
        if traffic_data:
            anomalies = detect_anomalies(traffic_data)
            return JsonResponse({'anomalies': anomalies})
        else:
            return JsonResponse({'error': 'Failed to retrieve traffic data'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
