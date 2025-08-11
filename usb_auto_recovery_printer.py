#!/usr/bin/env python3
"""
USB Printer with Automatic Error Recovery
==========================================

Enhanced USB printer interface with automatic error recovery mechanisms
for handling errno 5 (input/output errors), errno 16 (resource busy), 
and other USB communication issues.

Otomatik hata kurtarma mekanizmaları:
- I/O Error (errno 5) otomatik düzeltme
- Resource Busy (errno 16) otomatik çözme
- USB cihaz reconnection
- Kernel driver yönetimi
- Process cleanup
"""

import logging
import time
import usb.core
import usb.util
import subprocess
import os
import signal
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from usb_direct_printer import DirectUSBPrinter, USBPrinterType, USBPrinterInfo, KNOWN_USB_PRINTERS

logger = logging.getLogger(__name__)


class USBErrorType(Enum):
    """USB Error types"""
    IO_ERROR = "io_error"  # errno 5
    RESOURCE_BUSY = "resource_busy"  # errno 16
    ACCESS_DENIED = "access_denied"  # errno 13
    DEVICE_NOT_FOUND = "device_not_found"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class USBErrorInfo:
    """USB Error information"""
    error_type: USBErrorType
    errno: Optional[int]
    message: str
    recovery_attempts: int
    last_attempt_time: float


class USBAutoRecoveryPrinter(DirectUSBPrinter):
    """
    Enhanced USB printer with automatic error recovery capabilities
    """
    
    def __init__(self, vendor_id: Optional[int] = None, product_id: Optional[int] = None, 
                 auto_detect: bool = True, max_recovery_attempts: int = 3, 
                 recovery_delay: float = 2.0, auto_recovery_enabled: bool = True):
        """
        Initialize USB printer with auto-recovery
        
        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID  
            auto_detect: Auto-detect printer if not specified
            max_recovery_attempts: Maximum recovery attempts per error
            recovery_delay: Delay between recovery attempts (seconds)
            auto_recovery_enabled: Enable automatic error recovery
        """
        super().__init__(vendor_id, product_id, auto_detect)
        
        self.max_recovery_attempts = max_recovery_attempts
        self.recovery_delay = recovery_delay
        self.auto_recovery_enabled = auto_recovery_enabled
        
        # Error tracking
        self.error_history: List[USBErrorInfo] = []
        self.current_error: Optional[USBErrorInfo] = None
        self.last_successful_operation = time.time()
        
        # Recovery state
        self.recovery_in_progress = False
        self.total_recovery_attempts = 0
        
        logger.info(f"USBAutoRecoveryPrinter initialized (auto_recovery: {auto_recovery_enabled})")
    
    def _classify_usb_error(self, error: Exception) -> USBErrorType:
        """Classify USB error type"""
        error_str = str(error).lower()
        
        if hasattr(error, 'errno'):
            if error.errno == 5:
                return USBErrorType.IO_ERROR
            elif error.errno == 16:
                return USBErrorType.RESOURCE_BUSY
            elif error.errno == 13:
                return USBErrorType.ACCESS_DENIED
        
        if "input/output error" in error_str or "i/o error" in error_str:
            return USBErrorType.IO_ERROR
        elif "resource busy" in error_str or "busy" in error_str:
            return USBErrorType.RESOURCE_BUSY
        elif "access denied" in error_str or "permission denied" in error_str:
            return USBErrorType.ACCESS_DENIED
        elif "no such device" in error_str or "device not found" in error_str:
            return USBErrorType.DEVICE_NOT_FOUND
        elif "timeout" in error_str:
            return USBErrorType.TIMEOUT
        else:
            return USBErrorType.UNKNOWN
    
    def _log_error(self, error: Exception, operation: str = "USB operation"):
        """Log and track USB error"""
        error_type = self._classify_usb_error(error)
        errno = getattr(error, 'errno', None)
        
        error_info = USBErrorInfo(
            error_type=error_type,
            errno=errno,
            message=str(error),
            recovery_attempts=0,
            last_attempt_time=time.time()
        )
        
        self.error_history.append(error_info)
        self.current_error = error_info
        
        logger.error(f"USB Error in {operation}: {error_type.value} (errno: {errno}) - {error}")
    
    def _find_usb_processes(self) -> List[Dict[str, Any]]:
        """Find processes using USB devices"""
        processes = []
        
        try:
            # Zebra yazıcıları bul
            zebra_devices = list(usb.core.find(find_all=True, idVendor=0x0a5f))
            
            for device in zebra_devices:
                usb_path = f"/dev/bus/usb/{device.bus:03d}/{device.address:03d}"
                
                try:
                    result = subprocess.run(
                        ['lsof', usb_path], 
                        capture_output=True, 
                        text=True, 
                        timeout=5
                    )
                    
                    if result.returncode == 0 and result.stdout.strip():
                        lines = result.stdout.strip().split('\n')[1:]  # Header'ı atla
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 2:
                                processes.append({
                                    'name': parts[0],
                                    'pid': parts[1],
                                    'device_path': usb_path,
                                    'bus': device.bus,
                                    'address': device.address
                                })
                                
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    pass
        
        except Exception as e:
            logger.debug(f"Error finding USB processes: {e}")
        
        return processes
    
    def _kill_usb_processes(self, processes: List[Dict[str, Any]]) -> bool:
        """Kill processes using USB devices"""
        if not processes:
            return True
        
        logger.info(f"🔥 Killing {len(processes)} USB processes...")
        
        success = True
        for proc in processes:
            try:
                pid = int(proc['pid'])
                
                # Önce SIGTERM
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                
                # Hala çalışıyor mu kontrol et
                try:
                    os.kill(pid, 0)
                    # Hala çalışıyor, SIGKILL gönder
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(0.2)
                except ProcessLookupError:
                    pass  # Process sonlandırıldı
                    
            except (ProcessLookupError, PermissionError, Exception) as e:
                logger.warning(f"Process kill error: {e}")
                success = False
        
        return success
    
    def _reset_usb_device(self, vendor_id: int = 0x0a5f) -> bool:
        """Reset USB device"""
        try:
            devices = list(usb.core.find(find_all=True, idVendor=vendor_id))
            
            for device in devices:
                try:
                    device.reset()
                    time.sleep(1)
                    logger.info(f"USB device reset: Bus {device.bus:03d} Device {device.address:03d}")
                except Exception as e:
                    logger.warning(f"USB reset error: {e}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"USB reset failed: {e}")
            return False
    
    def _unbind_kernel_driver(self) -> bool:
        """Unbind kernel driver from USB device"""
        try:
            if not self.device:
                return False
            
            config = self.device.get_active_configuration()
            
            for interface in config:
                interface_num = interface.bInterfaceNumber
                
                try:
                    if self.device.is_kernel_driver_active(interface_num):
                        self.device.detach_kernel_driver(interface_num)
                        logger.info(f"Kernel driver detached: Interface {interface_num}")
                        time.sleep(0.2)
                except Exception as e:
                    logger.debug(f"Kernel driver detach error: {e}")
            
            return True
        except Exception as e:
            logger.warning(f"Kernel driver unbind failed: {e}")
            return False
    
    def _recover_from_io_error(self) -> bool:
        """Recover from I/O error (errno 5)"""
        logger.info("🔧 Recovering from I/O error...")
        
        try:
            # 1. Disconnect mevcut bağlantı
            self.disconnect()
            time.sleep(self.recovery_delay)
            
            # 2. USB cihazını reset et
            if not self._reset_usb_device(self.vendor_id or 0x0a5f):
                logger.warning("USB reset failed")
            
            time.sleep(self.recovery_delay)
            
            # 3. Yeniden bağlan
            if self.connect():
                logger.info("✅ I/O error recovery successful")
                return True
            else:
                logger.error("❌ I/O error recovery failed - reconnection failed")
                return False
        
        except Exception as e:
            logger.error(f"I/O error recovery failed: {e}")
            return False
    
    def _recover_from_resource_busy(self) -> bool:
        """Recover from resource busy error (errno 16)"""
        logger.info("🔧 Recovering from resource busy error...")
        
        try:
            # 1. Disconnect
            self.disconnect()
            time.sleep(1)
            
            # 2. USB process'leri bul ve sonlandır
            processes = self._find_usb_processes()
            if processes:
                logger.info(f"Found {len(processes)} USB processes")
                if not self._kill_usb_processes(processes):
                    logger.warning("Some USB processes could not be killed")
            
            time.sleep(1)
            
            # 3. Kernel driver'ı unbind et
            self._unbind_kernel_driver()
            time.sleep(1)
            
            # 4. USB reset
            if not self._reset_usb_device(self.vendor_id or 0x0a5f):
                logger.warning("USB reset failed")
            
            time.sleep(self.recovery_delay)
            
            # 5. Yeniden bağlan
            if self.connect():
                logger.info("✅ Resource busy recovery successful")
                return True
            else:
                logger.error("❌ Resource busy recovery failed")
                return False
        
        except Exception as e:
            logger.error(f"Resource busy recovery failed: {e}")
            return False
    
    def _recover_from_error(self, error_type: USBErrorType) -> bool:
        """Recover from specific error type"""
        if self.recovery_in_progress:
            logger.warning("Recovery already in progress, skipping...")
            return False
        
        self.recovery_in_progress = True
        self.total_recovery_attempts += 1
        
        try:
            logger.info(f"🚑 Starting recovery for {error_type.value} (attempt {self.total_recovery_attempts})")
            
            if error_type == USBErrorType.IO_ERROR:
                success = self._recover_from_io_error()
            elif error_type == USBErrorType.RESOURCE_BUSY:
                success = self._recover_from_resource_busy()
            elif error_type == USBErrorType.DEVICE_NOT_FOUND:
                # Cihaz bulunamadı - yeniden detect et
                time.sleep(self.recovery_delay)
                success = self.connect()
            else:
                # Genel recovery - disconnect/reconnect
                self.disconnect()
                time.sleep(self.recovery_delay)
                success = self.connect()
            
            if success:
                logger.info(f"✅ Recovery successful for {error_type.value}")
                self.current_error = None
                self.last_successful_operation = time.time()
            else:
                logger.error(f"❌ Recovery failed for {error_type.value}")
            
            return success
        
        finally:
            self.recovery_in_progress = False
    
    def _should_attempt_recovery(self) -> bool:
        """Check if recovery should be attempted"""
        if not self.auto_recovery_enabled:
            return False
        
        if not self.current_error:
            return False
        
        if self.current_error.recovery_attempts >= self.max_recovery_attempts:
            logger.warning(f"Max recovery attempts ({self.max_recovery_attempts}) reached")
            return False
        
        # Çok sık recovery denemesini önle
        time_since_last = time.time() - self.current_error.last_attempt_time
        if time_since_last < self.recovery_delay:
            return False
        
        return True
    
    def send_zpl_command(self, zpl_command: str) -> bool:
        """
        Send ZPL command with automatic error recovery
        """
        max_attempts = self.max_recovery_attempts + 1  # Initial attempt + recovery attempts
        
        for attempt in range(max_attempts):
            try:
                # Temel gönderme işlemi
                result = super().send_zpl_command(zpl_command)
                
                if result:
                    self.last_successful_operation = time.time()
                    self.current_error = None
                    logger.info(f"ZPL command sent successfully (attempt {attempt + 1})")
                    return True
                else:
                    raise Exception("ZPL command send failed")
            
            except Exception as e:
                self._log_error(e, "send_zpl_command")
                
                # İlk deneme mi ve auto recovery açık mı?
                if attempt < max_attempts - 1 and self._should_attempt_recovery():
                    error_type = self._classify_usb_error(e)
                    logger.warning(f"Attempting recovery for {error_type.value} (attempt {attempt + 1}/{max_attempts})")
                    
                    if self.current_error:
                        self.current_error.recovery_attempts += 1
                        self.current_error.last_attempt_time = time.time()
                    
                    # Recovery dene
                    if self._recover_from_error(error_type):
                        time.sleep(0.5)  # Kısa bekleme sonrası tekrar dene
                        continue
                    else:
                        logger.error(f"Recovery failed for {error_type.value}")
                        break
                else:
                    logger.error(f"ZPL command failed after {attempt + 1} attempts: {e}")
                    break
        
        return False
    
    def connect(self) -> bool:
        """Connect with automatic recovery"""
        try:
            result = super().connect()
            if result:
                self.last_successful_operation = time.time()
                self.current_error = None
            return result
        except Exception as e:
            self._log_error(e, "connect")
            
            if self.auto_recovery_enabled and self._should_attempt_recovery():
                error_type = self._classify_usb_error(e)
                logger.info("Attempting connection recovery...")
                return self._recover_from_error(error_type)
            
            return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        error_counts = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.error_history),
            'error_counts': error_counts,
            'total_recovery_attempts': self.total_recovery_attempts,
            'current_error': self.current_error.error_type.value if self.current_error else None,
            'last_successful_operation': self.last_successful_operation,
            'auto_recovery_enabled': self.auto_recovery_enabled
        }
    
    def reset_error_history(self):
        """Reset error history and stats"""
        self.error_history.clear()
        self.current_error = None
        self.total_recovery_attempts = 0
        logger.info("Error history reset")


def send_zpl_with_auto_recovery(zpl_command: str, vendor_id: int = 0x0A5F, 
                               product_id: int = 0x0164, max_attempts: int = 3) -> bool:
    """
    Convenience function to send ZPL with automatic recovery
    
    Args:
        zpl_command: ZPL command to send
        vendor_id: USB Vendor ID
        product_id: USB Product ID  
        max_attempts: Maximum recovery attempts
        
    Returns:
        True if successful, False otherwise
    """
    printer = USBAutoRecoveryPrinter(
        vendor_id=vendor_id, 
        product_id=product_id, 
        auto_detect=False,
        max_recovery_attempts=max_attempts,
        auto_recovery_enabled=True
    )
    
    try:
        if printer.connect():
            result = printer.send_zpl_command(zpl_command)
            stats = printer.get_error_stats()
            if stats['total_errors'] > 0:
                logger.info(f"Operation completed with {stats['total_errors']} errors and {stats['total_recovery_attempts']} recovery attempts")
            printer.disconnect()
            return result
        else:
            logger.error("Could not connect to printer")
            return False
    except Exception as e:
        logger.error(f"Error in send_zpl_with_auto_recovery: {e}")
        return False


if __name__ == "__main__":
    # Test the auto-recovery printer
    logging.basicConfig(level=logging.INFO)
    
    printer = USBAutoRecoveryPrinter(auto_detect=True, max_recovery_attempts=3)
    
    if printer.connect():
        info = printer.get_printer_info()
        print(f"Connected to: {info}")
        
        # Test ZPL command
        test_zpl = "^XA^FO50,50^A0N,50,50^FDAuto Recovery Test^FS^XZ"
        
        for i in range(5):
            print(f"\nTest {i+1}/5:")
            if printer.send_zpl_command(test_zpl):
                print("✅ Test print sent successfully")
            else:
                print("❌ Test print failed")
            
            # Stats göster
            stats = printer.get_error_stats()
            print(f"Stats: {stats}")
            
            time.sleep(2)
        
        printer.disconnect()
    else:
        print("Failed to connect to printer")
