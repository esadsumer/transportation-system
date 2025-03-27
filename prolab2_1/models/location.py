import math
from typing import List, Dict, Optional
from .vehicle import Vehicle

class Location:
    def __init__(self, lat: float, lon: float):
        self.lat = lat  # Enlem
        self.lon = lon  # Boylam
    
    def distance_to(self, other: 'Location') -> float:
        # İki nokta arasındaki mesafeyi hesaplamak için Haversine formülü
        R = 6371  # Dünya'nın yarıçapı (kilometre)
        
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(other.lat), math.radians(other.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

class Stop(Location):
    def __init__(self, id: str, name: str, type: str, lat: float, lon: float, 
                 son_durak: bool, next_stops: List[Dict], transfer: Optional[Dict]):
        super().__init__(lat, lon)
        self.id = id
        self.name = name
        self.type = type
        self.son_durak = son_durak  # Son durak mı?
        self.next_stops = next_stops  # Sonraki duraklar
        self.transfer = transfer  # Aktarma bilgisi 