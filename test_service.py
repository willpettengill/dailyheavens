import json
import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"

# Test data
TEST_DATA = {
    "email": "wwpettengill@gmail.com",
    "birth_date": "6/20/1988",
    "birth_time": "04:25",
    "birth_place_zip": "01776"
}

def test_chart_endpoint():
    """Test the chart generation endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/chart", json=TEST_DATA)
        if response.status_code == 200:
            print("✅ Chart generation successful!")
            chart_data = response.json()
            print(f"Sun Sign: {chart_data['sun_sign']}")
            print(f"Moon Sign: {chart_data['moon_sign']}")
            print(f"Ascendant: {chart_data['ascendant']}")
            print("\nInterpretation:")
            print(chart_data['interpretation'])
            return True
        else:
            print(f"❌ Chart generation failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing chart endpoint: {str(e)}")
        return False

def test_webhook_endpoint():
    """Test the webhook endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=TEST_DATA)
        if response.status_code == 200:
            print("✅ Webhook test successful!")
            data = response.json()
            print(f"Sun Sign: {data['chart']['sun_sign']}")
            print(f"Moon Sign: {data['chart']['moon_sign']}")
            print(f"Ascendant: {data['chart']['ascendant']}")
            return True
        else:
            print(f"❌ Webhook test failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {str(e)}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing health endpoint: {str(e)}")
        return False

def main():
    print("Testing Astrological Service with dummy data:")
    print(json.dumps(TEST_DATA, indent=2))
    print()
    
    # First check if the server is running
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=2)
        if health_check.status_code != 200:
            print("⚠️ Server may not be running properly. Health check failed.")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the server with 'uvicorn app.main:app --reload'")
        sys.exit(1)
    
    # Run tests
    print("1. Testing health check endpoint...")
    test_health_endpoint()
    print()
    
    print("2. Testing chart generation endpoint...")
    test_chart_endpoint()
    print()
    
    print("3. Testing webhook endpoint...")
    test_webhook_endpoint()

if __name__ == "__main__":
    main()
