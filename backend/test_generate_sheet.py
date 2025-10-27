#!/usr/bin/env python3
"""
Test script for the generate_sheet Lambda function
"""

import json
import sys
import os

# Add the lambda directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda'))

from handlers.generate_sheet import handler

def test_generate_sheet():
    """Test the generate_sheet handler"""
    
    # Mock event
    event = {
        'body': json.dumps({
            'song_name': 'Twinkle Twinkle Little Star',
            'instrument': 'C'
        })
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = 'test'
            self.function_version = '1'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test'
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = 30000
    
    context = MockContext()
    
    print("Testing generate_sheet handler...")
    print(f"Event: {event}")
    
    try:
        result = handler(event, context)
        print(f"Result: {result}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Success! ABC notation: {body.get('abc_notation', 'None')[:100]}...")
        else:
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_sheet()
