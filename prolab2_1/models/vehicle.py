from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class VehicleStats:
    total_distance: float = 0.0
    total_passengers: int = 0
    total_revenue: float = 0.0
    total_trips: int = 0

class Vehicle(ABC):
    def __init__(self, capacity: int, speed: float, base_fare: float):
        self.capacity = capacity  # Yolcu kapasitesi
        self.speed = speed  # Hız (km/saat)
        self.base_fare = base_fare  # Temel ücret
        self.current_passengers = 0  # Mevcut yolcu sayısı
        self.stats = VehicleStats()  # İstatistikler
    
    @abstractmethod
    def calculate_cost(self, distance: float) -> float:
        """Mesafeye göre ücreti hesapla"""
        pass
    
    def calculate_time(self, distance: float) -> float:
        """Mesafeye göre süreyi hesapla (dakika)"""
        return (distance / self.speed) * 60
    
    def can_accept_passengers(self, count: int = 1) -> bool:
        """Yeni yolcu alabilir mi kontrol et"""
        return self.current_passengers + count <= self.capacity
    
    def add_passengers(self, count: int = 1) -> bool:
        """Yolcu ekle"""
        if self.can_accept_passengers(count):
            self.current_passengers += count
            self.stats.total_passengers += count
            return True
        return False
    
    def remove_passengers(self, count: int = 1) -> bool:
        """Yolcu çıkar"""
        if self.current_passengers >= count:
            self.current_passengers -= count
            return True
        return False
    
    def update_stats(self, distance: float, revenue: float) -> None:
        """İstatistikleri güncelle"""
        self.stats.total_distance += distance
        self.stats.total_revenue += revenue
        self.stats.total_trips += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            "type": self.__class__.__name__,
            "capacity": self.capacity,
            "speed": self.speed,
            "base_fare": self.base_fare,
            "current_passengers": self.current_passengers,
            "total_distance": self.stats.total_distance,
            "total_passengers": self.stats.total_passengers,
            "total_revenue": self.stats.total_revenue,
            "total_trips": self.stats.total_trips
        }

class Bus(Vehicle):
    def __init__(self, base_fare: float = 3.0):
        super().__init__(capacity=50, speed=30, base_fare=base_fare)
    
    def calculate_cost(self, distance: float) -> float:
        return self.base_fare

class Tram(Vehicle):
    def __init__(self, base_fare: float = 2.5):
        super().__init__(capacity=100, speed=20, base_fare=base_fare)
    
    def calculate_cost(self, distance: float) -> float:
        return self.base_fare

class Taxi(Vehicle):
    def __init__(self, opening_fee: float = 10.0, cost_per_km: float = 4.0):
        super().__init__(capacity=4, speed=40, base_fare=opening_fee)
        self.cost_per_km = cost_per_km
    
    def calculate_cost(self, distance: float) -> float:
        return self.base_fare + (distance * self.cost_per_km) 