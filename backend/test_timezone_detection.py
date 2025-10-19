import asyncio
from app.utils.timezone import TimezoneHandler
from datetime import datetime

def test_timezone_detection():
    print("🧭 TESTING TIMEZONE AUTO-DETECTION")
    
    # Mock request class for testing
    class MockRequest:
        def __init__(self, headers):
            self.headers = headers
    
    # Test 1: Valid timezone header
    request1 = MockRequest({"X-Timezone": "America/New_York"})
    tz1 = TimezoneHandler.detect_timezone_from_request(request1)
    print(f"✅ Explicit timezone header: {tz1}")
    
    # Test 2: UTC offset header
    request2 = MockRequest({"X-Timezone-Offset": "3"})  # +3 hours from UTC
    tz2 = TimezoneHandler.detect_timezone_from_request(request2)
    print(f"✅ Offset-based detection: {tz2}")
    
    # Test 3: No headers (fallback to UTC)
    request3 = MockRequest({})
    tz3 = TimezoneHandler.detect_timezone_from_request(request3)
    print(f"✅ Fallback to UTC: {tz3}")
    
    # Test 4: Formatting for display
    test_time = datetime(2025, 10, 18, 10, 30, 0)
    formatted = TimezoneHandler.format_for_display(test_time, "America/New_York")
    print(f"✅ Smart formatting: {formatted}")
    
    # Test 5: Relative time
    recent_time = datetime.now()
    relative = TimezoneHandler.format_relative_time(recent_time)
    print(f"✅ Relative time: {relative}")

if __name__ == "__main__":
    test_timezone_detection()
