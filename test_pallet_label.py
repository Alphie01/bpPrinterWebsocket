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
                'firma_adi': 'Bil Plastik Ambalaj',
                'depo_adi': 'Ana Fabrika',
                'sevkiyat_bilgisi': 'Sevkiyat Ürün Deposu',
                'hammadde_ismi': 'PE Granül Doğal',
                'urun_adi': 'Polietilen Hammadde',
                'teslim_firma': 'ABC Plastik Ltd Şti',
                'siparis_tarihi': '2025-08-10',
                'palet_id': 'PLT2025001',
                'lot_no': 'LOT001',
                'durum': 'HAZIR',
                'brut_kg': '25.5',
                'net_kg': '25.0'
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
