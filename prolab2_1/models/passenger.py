from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any

class PassengerType(Enum):
    GENERAL = "general"  # Genel yolcu
    STUDENT = "student"  # Öğrenci
    TEACHER = "teacher"  # Öğretmen
    ELDERLY = "elderly"  # Yaşlı

class Passenger(ABC):
    def __init__(self, passenger_type: PassengerType):
        self.passenger_type = passenger_type
        self.discount_rate = self.get_discount_rate()
    
    @abstractmethod
    def get_discount_rate(self) -> float:
        """Yolcu tipine göre indirim oranını hesapla"""
        pass
    
    def calculate_cost(self, base_cost: float) -> float:
        """İndirimli ücreti hesapla"""
        return base_cost * self.discount_rate
    
    def calculate_time(self, base_time: float) -> float:
        """Yolcu tipine göre süreyi hesapla (yaşlılar için daha uzun süre)"""
        return base_time * self.get_time_multiplier()
    
    def get_time_multiplier(self) -> float:
        """Yolcu tipine göre süre çarpanını hesapla"""
        return 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Yolcu bilgilerini sözlük olarak döndür"""
        return {
            "type": self.passenger_type.value,
            "discount_rate": self.discount_rate,
            "time_multiplier": self.get_time_multiplier()
        }

class GeneralPassenger(Passenger):
    def __init__(self):
        super().__init__(PassengerType.GENERAL)
    
    def get_discount_rate(self) -> float:
        return 1.0  # İndirim yok

class StudentPassenger(Passenger):
    def __init__(self):
        super().__init__(PassengerType.STUDENT)
    
    def get_discount_rate(self) -> float:
        return 0.5  # %50 indirim

class TeacherPassenger(Passenger):
    def __init__(self):
        super().__init__(PassengerType.TEACHER)
    
    def get_discount_rate(self) -> float:
        return 0.5  # Öğretmenler de öğrenci indirimi alıyor

class ElderlyPassenger(Passenger):
    def __init__(self):
        super().__init__(PassengerType.ELDERLY)
    
    def get_discount_rate(self) -> float:
        return 0.3  # %70 indirim
    
    def get_time_multiplier(self) -> float:
        return 1.5  # Yaşlılar için %50 daha uzun süre 