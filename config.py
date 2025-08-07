"""
Configuration module for the WebSocket Printer Client
"""

import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PrinterType(Enum):
    """Supported printer types"""
    LABEL = "label"
    THERMAL = "thermal"
    LASER = "laser"


@dataclass
class PrinterConfig:
    """Printer configuration data class"""
    printer_id: str
    printer_name: str
    printer_type: PrinterType
    location: str
    serial_port: str
    baud_rate: int = 9600
    timeout: float = 1.0
    
    @classmethod
    def from_env(cls) -> 'PrinterConfig':
        """Create configuration from environment variables"""
        return cls(
            printer_id=os.getenv('PRINTER_ID', 'PRINTER_001'),
            printer_name=os.getenv('PRINTER_NAME', 'Default Printer'),
            printer_type=PrinterType(os.getenv('PRINTER_TYPE', 'thermal')),
            location=os.getenv('PRINTER_LOCATION', 'Warehouse A'),
            serial_port=os.getenv('SERIAL_PORT', 'COM1'),
            baud_rate=int(os.getenv('BAUD_RATE', '9600')),
            timeout=float(os.getenv('SERIAL_TIMEOUT', '1.0'))
        )


@dataclass
class ServerConfig:
    """WebSocket server configuration"""
    url: str = "http://localhost:25625"
    reconnect_delay: float = 5.0
    max_reconnect_attempts: int = 10
    ping_interval: float = 30.0
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Create server configuration from environment variables"""
        return cls(
            url=os.getenv('SERVER_URL', 'http://localhost:25625'),
            reconnect_delay=float(os.getenv('RECONNECT_DELAY', '5.0')),
            max_reconnect_attempts=int(os.getenv('MAX_RECONNECT_ATTEMPTS', '10')),
            ping_interval=float(os.getenv('PING_INTERVAL', '30.0'))
        )


@dataclass
class AppConfig:
    """Application configuration"""
    printer: PrinterConfig
    server: ServerConfig
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create application configuration from environment variables"""
        return cls(
            printer=PrinterConfig.from_env(),
            server=ServerConfig.from_env(),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE')
        )


# Default configurations for different printer models
PRINTER_PRESETS = {
    'zebra_zd410': {
        'baud_rate': 9600,
        'timeout': 2.0,
        'printer_type': PrinterType.THERMAL
    },
    'epson_tm_t20': {
        'baud_rate': 38400,
        'timeout': 1.0,
        'printer_type': PrinterType.THERMAL
    },
    'brother_ql': {
        'baud_rate': 9600,
        'timeout': 1.5,
        'printer_type': PrinterType.LABEL
    }
}
