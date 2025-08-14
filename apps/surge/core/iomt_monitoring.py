"""
Internet of Medical Things (IoMT) & Real-Time Patient Monitoring
State-of-the-art wearable sensors and device integration for surgical patients
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
import pandas as pd
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DeviceType(str, Enum):
    """Types of IoMT devices"""
    PULSE_OXIMETER = "pulse_oximeter"
    ECG_MONITOR = "ecg_monitor"
    BLOOD_PRESSURE = "blood_pressure"
    TEMPERATURE_SENSOR = "temperature_sensor"
    RESPIRATORY_MONITOR = "respiratory_monitor"
    GLUCOSE_MONITOR = "glucose_monitor"
    ACTIVITY_TRACKER = "activity_tracker"
    SMART_BED = "smart_bed"
    IV_PUMP = "iv_pump"
    VENTILATOR = "ventilator"

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class VitalSigns:
    """Standardized vital signs data structure"""
    patient_id: str
    timestamp: datetime
    heart_rate: Optional[float] = None
    blood_pressure_systolic: Optional[float] = None
    blood_pressure_diastolic: Optional[float] = None
    oxygen_saturation: Optional[float] = None
    respiratory_rate: Optional[float] = None
    temperature: Optional[float] = None
    glucose_level: Optional[float] = None
    device_id: Optional[str] = None
    device_type: Optional[DeviceType] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class DeviceAlert:
    """IoMT device alert structure"""
    alert_id: str
    patient_id: str
    device_id: str
    device_type: DeviceType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    vital_signs: Optional[VitalSigns] = None
    acknowledged: bool = False
    resolved: bool = False

class IoMTDevice:
    """Base class for IoMT device simulation"""
    
    def __init__(self, device_id: str, device_type: DeviceType, patient_id: str):
        self.device_id = device_id
        self.device_type = device_type
        self.patient_id = patient_id
        self.is_active = False
        self.last_reading = None
        self.battery_level = 100.0
        self.connection_status = "connected"
        
    async def start_monitoring(self):
        """Start continuous monitoring"""
        self.is_active = True
        logger.info(f"Started monitoring for device {self.device_id} ({self.device_type})")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.is_active = False
        logger.info(f"Stopped monitoring for device {self.device_id}")
    
    async def get_reading(self) -> Optional[VitalSigns]:
        """Get current vital signs reading - to be implemented by specific devices"""
        raise NotImplementedError
    
    async def calibrate(self):
        """Calibrate device"""
        logger.info(f"Calibrating device {self.device_id}")
        await asyncio.sleep(2)  # Simulate calibration time
        return True

class PulseOximeterDevice(IoMTDevice):
    """Pulse oximeter IoMT device simulation"""
    
    def __init__(self, device_id: str, patient_id: str):
        super().__init__(device_id, DeviceType.PULSE_OXIMETER, patient_id)
        self.baseline_spo2 = 98.0
        self.baseline_hr = 72.0
    
    async def get_reading(self) -> VitalSigns:
        """Simulate pulse oximeter reading with realistic variations"""
        if not self.is_active:
            return None
        
        # Simulate realistic variations
        spo2_noise = np.random.normal(0, 0.5)
        hr_noise = np.random.normal(0, 3)
        
        # Add some trends for surgical patients
        time_factor = (datetime.utcnow().hour % 24) / 24
        stress_factor = 1 + 0.1 * np.sin(time_factor * 2 * np.pi)
        
        spo2 = max(85, min(100, self.baseline_spo2 + spo2_noise))
        heart_rate = max(50, min(150, self.baseline_hr * stress_factor + hr_noise))
        
        reading = VitalSigns(
            patient_id=self.patient_id,
            timestamp=datetime.utcnow(),
            oxygen_saturation=round(spo2, 1),
            heart_rate=round(heart_rate, 0),
            device_id=self.device_id,
            device_type=self.device_type
        )
        
        self.last_reading = reading
        return reading

class BloodPressureDevice(IoMTDevice):
    """Blood pressure monitor IoMT device"""
    
    def __init__(self, device_id: str, patient_id: str):
        super().__init__(device_id, DeviceType.BLOOD_PRESSURE, patient_id)
        self.baseline_systolic = 120.0
        self.baseline_diastolic = 80.0
    
    async def get_reading(self) -> VitalSigns:
        """Simulate blood pressure reading"""
        if not self.is_active:
            return None
        
        # Realistic BP variations
        systolic_noise = np.random.normal(0, 8)
        diastolic_noise = np.random.normal(0, 5)
        
        # Postoperative trends
        stress_factor = 1.1  # Slightly elevated post-surgery
        
        systolic = max(80, min(200, self.baseline_systolic * stress_factor + systolic_noise))
        diastolic = max(50, min(120, self.baseline_diastolic * stress_factor + diastolic_noise))
        
        reading = VitalSigns(
            patient_id=self.patient_id,
            timestamp=datetime.utcnow(),
            blood_pressure_systolic=round(systolic, 0),
            blood_pressure_diastolic=round(diastolic, 0),
            device_id=self.device_id,
            device_type=self.device_type
        )
        
        self.last_reading = reading
        return reading

class TemperatureDevice(IoMTDevice):
    """Temperature sensor IoMT device"""
    
    def __init__(self, device_id: str, patient_id: str):
        super().__init__(device_id, DeviceType.TEMPERATURE_SENSOR, patient_id)
        self.baseline_temp = 98.6  # Fahrenheit
    
    async def get_reading(self) -> VitalSigns:
        """Simulate temperature reading"""
        if not self.is_active:
            return None
        
        temp_noise = np.random.normal(0, 0.3)
        temp = max(95, min(105, self.baseline_temp + temp_noise))
        
        reading = VitalSigns(
            patient_id=self.patient_id,
            timestamp=datetime.utcnow(),
            temperature=round(temp, 1),
            device_id=self.device_id,
            device_type=self.device_type
        )
        
        self.last_reading = reading
        return reading

class RealTimeMonitoringSystem:
    """Central IoMT monitoring and alert system"""
    
    def __init__(self):
        self.devices: Dict[str, IoMTDevice] = {}
        self.active_patients: Dict[str, List[str]] = {}  # patient_id -> device_ids
        self.alerts: List[DeviceAlert] = []
        self.vital_signs_history: Dict[str, List[VitalSigns]] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.start_time = datetime.utcnow()  # Track system start time
        
        # Alert thresholds
        self.alert_thresholds = {
            'heart_rate_low': 50,
            'heart_rate_high': 120,
            'spo2_low': 88,
            'systolic_high': 180,
            'systolic_low': 90,
            'diastolic_high': 110,
            'temp_high': 101.5,
            'temp_low': 96.0
        }
        
        # System statistics
        self.start_time = datetime.utcnow()

    async def register_device(self, device: IoMTDevice) -> bool:
        """Register a new IoMT device"""
        try:
            self.devices[device.device_id] = device
            
            # Add to patient's device list
            if device.patient_id not in self.active_patients:
                self.active_patients[device.patient_id] = []
            
            if device.device_id not in self.active_patients[device.patient_id]:
                self.active_patients[device.patient_id].append(device.device_id)
            
            # Initialize vital signs history
            if device.patient_id not in self.vital_signs_history:
                self.vital_signs_history[device.patient_id] = []
            
            logger.info(f"✅ Registered device {device.device_id} for patient {device.patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering device {device.device_id}: {str(e)}")
            return False
    
    async def start_patient_monitoring(self, patient_id: str) -> bool:
        """Start monitoring all devices for a patient"""
        try:
            if patient_id not in self.active_patients:
                logger.warning(f"No devices registered for patient {patient_id}")
                return False
            
            # Start monitoring tasks for all patient devices
            for device_id in self.active_patients[patient_id]:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    await device.start_monitoring()
                    
                    # Create monitoring task
                    task = asyncio.create_task(
                        self._continuous_monitoring(device)
                    )
                    self.monitoring_tasks[device_id] = task
            
            logger.info(f"✅ Started monitoring for patient {patient_id} with {len(self.active_patients[patient_id])} devices")
            return True
            
        except Exception as e:
            logger.error(f"Error starting patient monitoring: {str(e)}")
            return False
    
    async def stop_patient_monitoring(self, patient_id: str) -> bool:
        """Stop monitoring all devices for a patient"""
        try:
            if patient_id not in self.active_patients:
                return True
            
            # Stop monitoring tasks
            for device_id in self.active_patients[patient_id]:
                if device_id in self.devices:
                    await self.devices[device_id].stop_monitoring()
                
                if device_id in self.monitoring_tasks:
                    self.monitoring_tasks[device_id].cancel()
                    del self.monitoring_tasks[device_id]
            
            logger.info(f"✅ Stopped monitoring for patient {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping patient monitoring: {str(e)}")
            return False
    
    async def _continuous_monitoring(self, device: IoMTDevice):
        """Continuous monitoring loop for a device"""
        while device.is_active:
            try:
                # Get reading from device
                reading = await device.get_reading()
                
                if reading:
                    # Store reading
                    self.vital_signs_history[device.patient_id].append(reading)
                    
                    # Keep only last 1000 readings per patient
                    if len(self.vital_signs_history[device.patient_id]) > 1000:
                        self.vital_signs_history[device.patient_id] = \
                            self.vital_signs_history[device.patient_id][-1000:]
                    
                    # Check for alerts
                    await self._check_alerts(reading)
                
                # Wait before next reading (varies by device type)
                if device.device_type == DeviceType.PULSE_OXIMETER:
                    await asyncio.sleep(2)  # Every 2 seconds
                elif device.device_type == DeviceType.BLOOD_PRESSURE:
                    await asyncio.sleep(300)  # Every 5 minutes
                elif device.device_type == DeviceType.TEMPERATURE_SENSOR:
                    await asyncio.sleep(60)  # Every minute
                else:
                    await asyncio.sleep(30)  # Default 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring for device {device.device_id}: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _check_alerts(self, vital_signs: VitalSigns):
        """Check vital signs against alert thresholds"""
        alerts_generated = []
        
        # Heart rate alerts
        if vital_signs.heart_rate is not None:
            if vital_signs.heart_rate < self.alert_thresholds['heart_rate_low']:
                alert = DeviceAlert(
                    alert_id=f"hr_low_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.HIGH,
                    message=f"Bradycardia detected: HR {vital_signs.heart_rate} bpm",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
                
            elif vital_signs.heart_rate > self.alert_thresholds['heart_rate_high']:
                alert = DeviceAlert(
                    alert_id=f"hr_high_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.HIGH,
                    message=f"Tachycardia detected: HR {vital_signs.heart_rate} bpm",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
        
        # Oxygen saturation alerts
        if vital_signs.oxygen_saturation is not None:
            if vital_signs.oxygen_saturation < self.alert_thresholds['spo2_low']:
                severity = AlertSeverity.CRITICAL if vital_signs.oxygen_saturation < 85 else AlertSeverity.HIGH
                alert = DeviceAlert(
                    alert_id=f"spo2_low_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=severity,
                    message=f"Hypoxemia detected: SpO2 {vital_signs.oxygen_saturation}%",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
        
        # Blood pressure alerts
        if vital_signs.blood_pressure_systolic is not None:
            if vital_signs.blood_pressure_systolic > self.alert_thresholds['systolic_high']:
                alert = DeviceAlert(
                    alert_id=f"bp_high_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.HIGH,
                    message=f"Hypertension detected: BP {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic} mmHg",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
            
            elif vital_signs.blood_pressure_systolic < self.alert_thresholds['systolic_low']:
                alert = DeviceAlert(
                    alert_id=f"bp_low_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.HIGH,
                    message=f"Hypotension detected: BP {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic} mmHg",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
        
        # Temperature alerts
        if vital_signs.temperature is not None:
            if vital_signs.temperature > self.alert_thresholds['temp_high']:
                alert = DeviceAlert(
                    alert_id=f"temp_high_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.MEDIUM,
                    message=f"Fever detected: Temperature {vital_signs.temperature}°F",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
            
            elif vital_signs.temperature < self.alert_thresholds['temp_low']:
                alert = DeviceAlert(
                    alert_id=f"temp_low_{datetime.utcnow().timestamp()}",
                    patient_id=vital_signs.patient_id,
                    device_id=vital_signs.device_id,
                    device_type=vital_signs.device_type,
                    severity=AlertSeverity.MEDIUM,
                    message=f"Hypothermia detected: Temperature {vital_signs.temperature}°F",
                    timestamp=vital_signs.timestamp,
                    vital_signs=vital_signs
                )
                alerts_generated.append(alert)
        
        # Add alerts to system
        self.alerts.extend(alerts_generated)
        
        # Keep only last 500 alerts
        if len(self.alerts) > 500:
            self.alerts = self.alerts[-500:]
        
        # Log critical alerts
        for alert in alerts_generated:
            if alert.severity == AlertSeverity.CRITICAL:
                logger.critical(f"🚨 CRITICAL ALERT: {alert.message} for patient {alert.patient_id}")
            elif alert.severity == AlertSeverity.HIGH:
                logger.warning(f"⚠️ HIGH ALERT: {alert.message} for patient {alert.patient_id}")
    
    async def get_patient_status(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive real-time status for a patient"""
        try:
            if patient_id not in self.active_patients:
                return {'error': f'Patient {patient_id} not found'}
            
            # Get latest readings from all devices
            latest_readings = {}
            device_statuses = {}
            
            for device_id in self.active_patients[patient_id]:
                if device_id in self.devices:
                    device = self.devices[device_id]
                    device_statuses[device_id] = {
                        'type': device.device_type.value,
                        'active': device.is_active,
                        'battery': device.battery_level,
                        'connection': device.connection_status,
                        'last_reading': device.last_reading.timestamp.isoformat() if device.last_reading else None
                    }
                    
                    if device.last_reading:
                        latest_readings[device.device_type.value] = device.last_reading.to_dict()
            
            # Get recent alerts
            patient_alerts = [
                alert for alert in self.alerts 
                if alert.patient_id == patient_id and not alert.resolved
            ]
            
            # Get vital signs trend
            recent_vitals = []
            if patient_id in self.vital_signs_history:
                # Get last 20 readings
                recent_vitals = [
                    vs.to_dict() for vs in self.vital_signs_history[patient_id][-20:]
                ]
            
            return {
                'patient_id': patient_id,
                'timestamp': datetime.utcnow().isoformat(),
                'device_count': len(self.active_patients[patient_id]),
                'devices': device_statuses,
                'latest_readings': latest_readings,
                'active_alerts': len(patient_alerts),
                'recent_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'severity': alert.severity.value,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat(),
                        'acknowledged': alert.acknowledged
                    }
                    for alert in patient_alerts[-5:]  # Last 5 alerts
                ],
                'vital_signs_trend': recent_vitals
            }
            
        except Exception as e:
            logger.error(f"Error getting patient status: {str(e)}")
            return {'error': str(e)}
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged by {user_id}")
                return True
        return False
    
    async def get_system_statistics(self) -> Dict:
        """Get IoMT system statistics"""
        return {
            'connected_devices': len(self.devices),
            'patients_monitored': len(set(d.patient_id for d in self.devices.values())),
            'active_alerts': len([a for a in self.alerts if not a.acknowledged]),
            'total_readings': sum(d.total_readings for d in self.devices.values()),
            'uptime': (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    async def health_check(self) -> Dict:
        """Health check for IoMT monitoring system"""
        return {
            'status': 'healthy',
            'device_manager_active': self.device_manager is not None,
            'alert_processing': True,
            'data_storage': True,
            'timestamp': datetime.utcnow().isoformat()
        }


# Alias for backward compatibility
RealTimeMonitoringEngine = RealTimeMonitoringSystem

# Global IoMT monitoring system
iomt_system = RealTimeMonitoringSystem()
