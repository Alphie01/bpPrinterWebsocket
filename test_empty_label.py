#!/usr/bin/env python3
"""
Test script to send empty label data
"""

import socketio
import asyncio
import time

async def test_empty_label_data():
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to server")
        
        # Send a job with empty label_data
        empty_job = {
            'job_id': 'empty_test_001',
            'label_data': {},  # Empty dictionary
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'requested_by': 'empty_test'
        }
        
        print(f"📤 Sending job with empty label_data: {empty_job}")
        await sio.emit('print_job', empty_job)
    
    @sio.event
    async def print_job_result(data):
        print(f"📄 Print job result: {data}")
    
    @sio.event
    async def disconnect():
        print("❌ Disconnected")
    
    try:
        await sio.connect('http://192.168.1.139:25625')
        await asyncio.sleep(5)  # Wait for responses
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    print("🧪 Empty Label Data Test")
    print("=" * 30)
    asyncio.run(test_empty_label_data())
