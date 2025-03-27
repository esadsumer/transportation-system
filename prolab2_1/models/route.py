from dataclasses import dataclass
from typing import List
from .location import Stop
from .vehicle import Vehicle

@dataclass
class RouteSegment:
    from_stop: Stop  # Başlangıç durağı
    to_stop: Stop  # Bitiş durağı
    vehicle: Vehicle  # Taşıt
    distance: float  # Mesafe
    cost: float  # Ücret
    time: float  # Süre
    is_transfer: bool = False  # Aktarma mı?

@dataclass
class RouteOption:
    segments: List[RouteSegment]  # Rota parçaları
    total_cost: float  # Toplam ücret
    total_time: float  # Toplam süre
    total_distance: float  # Toplam mesafe
    requires_initial_taxi: bool  # Başlangıçta taksi gerekiyor mu?
    requires_final_taxi: bool  # Sonda taksi gerekiyor mu?
    start_distance: float  # Başlangıç mesafesi
    end_distance: float  # Bitiş mesafesi
    transfer_count: int = 0  # Aktarma sayısı 