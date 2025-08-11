#!/usr/bin/env python3
"""
Test script for new pallet label design
"""

import socketio
import asyncio
import time

async def test_pallet_label():
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        print("✅ Connected to server")
        
        # Send a pallet label test job
        pallet_job = {
            'job_id': 'pallet_test_001',
            'label_data': {
                'type': 'pallet',
                'product_code': 'BP-PE-001',
                'product_name': 'Polietilen Granül Doğal',
                'hammadde': 'PE Hammadde',
                'palet_id': 'PLT2025001',
                'lot_no': 'LOT001',
                'production_date': '2025-08-11',
                'expiry_date': '2026-08-11',
                'quantity': '250',
                'gross_weight': '25.5',
                'package_type': '25 KG Poşet',
                'net_weight': '25.0',
                'receiving_company': 'ABC Plastik Ltd Şti',
                'department': 'Ana Depo - A1',
                'responsible_person': 'Ahmet Yılmaz',
                'order_no': 'SIP2025001',
                'order_date': '2025-08-10',
                'status': 'HAZIR',
                'notes': 'Sevkiyat hazır'
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'requested_by': 'pallet_test'
        }
        
        print(f"📤 Sending pallet label test: {pallet_job}")
        await sio.emit('print_job', pallet_job)
    
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
    print("🏷️ Pallet Label Test")
    print("=" * 30)
    asyncio.run(test_pallet_label())
