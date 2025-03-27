from abc import ABC, abstractmethod
import math
from typing import List, Dict, Optional, Tuple, Set
import json
from dataclasses import dataclass
from heapq import heappush, heappop
from enum import Enum
from models import (
    Passenger, PassengerType, GeneralPassenger, StudentPassenger, ElderlyPassenger,
    PaymentMethod, CashPayment, CreditCardPayment, KentCardPayment,
    Vehicle, Bus, Tram, Taxi,
    Location, Stop,
    RouteSegment, RouteOption
)
from tabulate import tabulate

class TransportationSystem:
    # Sabit değerler
    TAXI_THRESHOLD = 3.0  # km cinsinden taksi kullanım eşiği
    WALKING_SPEED = 5.0  # km/saat cinsinden yürüme hızı
    
    def __init__(self, json_file: str):
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        self.stops: Dict[str, Stop] = {}
        # Taksi ücretlendirme modeli: Açılış 10 TL, km başına 4 TL
        self.taxi = Taxi(opening_fee=10.0, cost_per_km=4.0)
        self.bus = Bus()
        self.tram = Tram()
        
        for stop_data in data["duraklar"]:
            stop = Stop(
                stop_data["id"],
                stop_data["name"],
                stop_data["type"],
                stop_data["lat"],
                stop_data["lon"],
                stop_data["sonDurak"],
                stop_data["nextStops"],
                stop_data.get("transfer")
            )
            self.stops[stop.id] = stop
    
    def find_nearest_stop(self, location: Location) -> Tuple[Stop, float]:
        # En yakın durağı bul
        nearest_stop = None
        min_distance = float('inf')
        
        for stop in self.stops.values():
            distance = location.distance_to(stop)
            if distance < min_distance:
                min_distance = distance
                nearest_stop = stop
        
        return nearest_stop, min_distance
    
    def get_next_stops(self, current_stop: Stop) -> List[RouteSegment]:
        segments = []
        
        # Doğrudan sonraki durakları ekle
        for next_stop_data in current_stop.next_stops:
            next_stop = self.stops[next_stop_data["stopId"]]
            distance = next_stop_data["mesafe"]
            vehicle = self.bus if current_stop.type == "bus" else self.tram
            
            segments.append(RouteSegment(
                from_stop=current_stop,
                to_stop=next_stop,
                vehicle=vehicle,
                distance=distance,
                cost=next_stop_data["ucret"],
                time=next_stop_data["sure"]
            ))
        
        # Aktarma varsa ekle
        if current_stop.transfer:
            transfer_stop = self.stops[current_stop.transfer["transferStopId"]]
            segments.append(RouteSegment(
                from_stop=current_stop,
                to_stop=transfer_stop,
                vehicle=self.bus if current_stop.type == "tram" else self.tram,
                distance=0,  # Aktarma mesafesi önemsiz
                cost=current_stop.transfer["transferUcret"],
                time=current_stop.transfer["transferSure"],
                is_transfer=True
            ))
        
        return segments
    
    def evaluate_stop_access(self, location: Location, stop: Stop, passenger: Passenger) -> Dict:
        """Durağa ulaşım seçeneklerini değerlendir"""
        distance = location.distance_to(stop)
        
        # 3 km'den uzak mesafelerde zorunlu taksi kullanımı
        if distance > self.TAXI_THRESHOLD:
            taxi_cost = self.taxi.calculate_cost(distance) * passenger.get_discount_rate()
            taxi_time = self.taxi.calculate_time(distance)
            
            return {
                "distance": distance,
                "walking": {
                    "time": 0.0,
                    "cost": 0.0,
                    "available": False,
                    "reason": f"Mesafe ({distance:.2f} km) taksi kullanım eşiğinden ({self.TAXI_THRESHOLD} km) uzak"
                },
                "taxi": {
                    "time": taxi_time,
                    "cost": taxi_cost,
                    "available": True,
                    "reason": "Zorunlu taksi kullanımı"
                },
                "recommended": "taxi",
                "reason": "Mesafe taksi kullanım eşiğini aşıyor"
            }
        
        # 3 km'den kısa mesafelerde yürüyüş ve taksi seçenekleri
        walking_time = (distance / self.WALKING_SPEED) * 60  # dakika
        walking_cost = 0  # Yürüyüş ücretsiz
        
        taxi_cost = self.taxi.calculate_cost(distance) * passenger.get_discount_rate()
        taxi_time = self.taxi.calculate_time(distance)
        
        # Yürüyüş süresi taksi süresinden çok uzunsa taksi öner
        if walking_time > taxi_time * 2:
            recommended = "taxi"
            reason = "Yürüyüş süresi taksi süresinin 2 katından fazla"
        else:
            recommended = "walking"
            reason = "Mesafe yürüyüş için uygun"
        
        return {
            "distance": distance,
            "walking": {
                "time": walking_time,
                "cost": walking_cost,
                "available": True,
                "reason": "Mesafe yürüyüş için uygun"
            },
            "taxi": {
                "time": taxi_time,
                "cost": taxi_cost,
                "available": True,
                "reason": "Alternatif ulaşım seçeneği"
            },
            "recommended": recommended,
            "reason": reason
        }
    
    def find_route(self, start_location: Location, end_location: Location, 
                  passenger: Passenger, payment_method: PaymentMethod) -> Dict:
        # Başlangıç ve bitiş noktalarına en yakın durakları bul
        start_stop, start_distance = self.find_nearest_stop(start_location)
        end_stop, end_distance = self.find_nearest_stop(end_location)
        
        print(f"En yakın başlangıç durağı: {start_stop.name}, mesafe: {start_distance:.2f} km")
        print(f"En yakın bitiş durağı: {end_stop.name}, mesafe: {end_distance:.2f} km")
        
        # Duraklara ulaşım seçeneklerini değerlendir
        start_access = self.evaluate_stop_access(start_location, start_stop, passenger)
        end_access = self.evaluate_stop_access(end_location, end_stop, passenger)
        
        # Başlangıç veya bitiş için taksi gerekip gerekmediğini kontrol et
        requires_initial_taxi = start_access["recommended"] == "taxi"
        requires_final_taxi = end_access["recommended"] == "taxi"
        
        # Eğer başlangıç ve bitiş noktaları arasındaki mesafe 3 km'den azsa ve
        # aynı durak tipindeyse (ikisi de otobüs veya ikisi de tramvay), direkt bağlantı kur
        direct_distance = start_stop.distance_to(end_stop)
        print(f"Duraklar arası direkt mesafe: {direct_distance:.2f} km")
        
        if start_stop.type == end_stop.type and direct_distance <= 3.0:
            print("Direkt bağlantı kuruldu")
            # Araç tipine göre maliyet ve süre hesapla
            vehicle = self.bus if start_stop.type == "bus" else self.tram
            base_cost = direct_distance * (2.0 if start_stop.type == "bus" else 3.0)  # km başına maliyet
            base_time = direct_distance * (3.0 if start_stop.type == "bus" else 2.0)  # km başına süre
            
            # Yolcu indirimi ve süre çarpanını uygula
            total_cost = base_cost * passenger.get_discount_rate()
            total_time = base_time * passenger.get_time_multiplier()
            
            direct_segment = RouteSegment(
                from_stop=start_stop,
                to_stop=end_stop,
                vehicle=vehicle,
                distance=direct_distance,
                cost=base_cost,  # Ham maliyet
                time=base_time,  # Ham süre
                is_transfer=False
            )
            route = [direct_segment]
            total_distance = direct_distance
        else:
            print("Dijkstra algoritması ile rota hesaplanıyor")
            # Dijkstra algoritması için veri yapılarını başlat
            distances = {stop_id: float('inf') for stop_id in self.stops}
            previous = {stop_id: None for stop_id in self.stops}
            costs = {stop_id: float('inf') for stop_id in self.stops}
            times = {stop_id: float('inf') for stop_id in self.stops}
            visited = set()
            
            # Dijkstra algoritması için öncelikli kuyruk
            pq = [(0, 0, start_stop.id, None)]
            
            # Başlangıç değerlerini ayarla
            distances[start_stop.id] = 0
            costs[start_stop.id] = 0
            times[start_stop.id] = 0
            
            # Dijkstra algoritması
            while pq:
                current_cost, current_time, current_id, previous_segment = heappop(pq)
                
                if current_id == end_stop.id:
                    break
                    
                if current_id in visited:
                    continue
                    
                visited.add(current_id)
                current_stop = self.stops[current_id]
                
                # Tüm olası sonraki durakları al
                for segment in self.get_next_stops(current_stop):
                    next_stop = segment.to_stop
                    next_id = next_stop.id
                    
                    if next_id in visited:
                        continue
                    
                    # Yeni mesafe, maliyet ve süreleri hesapla
                    new_distance = distances[current_id] + segment.distance
                    new_cost = costs[current_id] + segment.cost
                    new_time = times[current_id] + segment.time
                    
                    # Daha iyi yol bulunduysa güncelle
                    if new_cost < costs[next_id]:
                        distances[next_id] = new_distance
                        costs[next_id] = new_cost
                        times[next_id] = new_time
                        previous[next_id] = (current_id, segment)
                        heappush(pq, (new_cost, new_time, next_id, segment))
            
            # Rotayı yeniden oluştur
            route = []
            current_id = end_stop.id
            while current_id is not None:
                if previous[current_id] is not None:
                    prev_id, segment = previous[current_id]
                    route.append(segment)
                current_id = previous[current_id][0] if previous[current_id] is not None else None
            route.reverse()
            
            print(f"Bulunan rota segment sayısı: {len(route)}")
            
            # Ham toplam değerleri hesapla (indirimler uygulanmadan)
            total_distance = sum(segment.distance for segment in route)
            total_cost = sum(segment.cost for segment in route)
            total_time = sum(segment.time for segment in route)
            
            # Yolcu indirimi ve süre çarpanını uygula
            total_cost = total_cost * passenger.get_discount_rate()
            total_time = total_time * passenger.get_time_multiplier()
            
            print(f"Rota mesafesi: {total_distance:.2f} km")
            print(f"Rota maliyeti: {total_cost:.2f} TL")
            print(f"Rota süresi: {total_time:.1f} dk")
        
        # Başlangıç ve bitiş erişim maliyetlerini ekle
        if requires_initial_taxi:
            total_cost += start_access["taxi"]["cost"]
            total_time += start_access["taxi"]["time"]
            total_distance += start_access["distance"]
            print("Başlangıç için taksi eklendi")
        else:
            total_time += start_access["walking"]["time"]
            total_distance += start_access["distance"]
            print("Başlangıç için yürüyüş eklendi")
        
        if requires_final_taxi:
            total_cost += end_access["taxi"]["cost"]
            total_time += end_access["taxi"]["time"]
            total_distance += end_access["distance"]
            print("Bitiş için taksi eklendi")
        else:
            total_time += end_access["walking"]["time"]
            total_distance += end_access["distance"]
            print("Bitiş için yürüyüş eklendi")
        
        print(f"Toplam mesafe: {total_distance:.2f} km")
        print(f"Toplam maliyet: {total_cost:.2f} TL")
        print(f"Toplam süre: {total_time:.1f} dk")
        
        # Aktarma sayısını say
        transfer_count = sum(1 for segment in route if segment.is_transfer)
        print(f"Aktarma sayısı: {transfer_count}")
        
        # Rota seçeneğini oluştur
        route_option = RouteOption(
            segments=route,
            total_cost=total_cost,
            total_time=total_time,
            total_distance=total_distance,
            requires_initial_taxi=requires_initial_taxi,
            requires_final_taxi=requires_final_taxi,
            start_distance=start_distance,
            end_distance=end_distance,
            transfer_count=transfer_count
        )
        
        # Ödeme işlemini gerçekleştir
        payment_successful = payment_method.process_payment(total_cost)
        
        return {
            "start_stop": start_stop,  # Başlangıç durağı
            "end_stop": end_stop,      # Bitiş durağı
            "start_access": start_access,  # Başlangıç durağına erişim bilgileri
            "end_access": end_access,      # Bitiş durağından çıkış bilgileri
            "route": route_option          # Rota bilgileri
        }

# Örnek kullanım
if __name__ == "__main__":
    import tkinter as tk
    from gui import TransportationGUI
    
    # Ana pencereyi oluştur
    root = tk.Tk()
    
    # GUI uygulamasını başlat
    app = TransportationGUI(root)
    
    # Ana döngüyü başlat
    root.mainloop() 