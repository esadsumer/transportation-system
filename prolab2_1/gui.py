import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from transportation_system import TransportationSystem, Location
from models import GeneralPassenger, StudentPassenger, TeacherPassenger, ElderlyPassenger
from models import CashPayment, CreditCardPayment, KentCardPayment
from tabulate import tabulate
import json
import folium
import webbrowser
import os
import tkintermapview

class TransportationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("İzmit Toplu Taşıma Rota Planlama Sistemi")
        self.root.geometry("1600x900")
        
        # Ana sistem
        self.system = TransportationSystem("Duraklar.json")
        
        # Ana frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Başlık
        ttk.Label(self.main_frame, text="İzmit Toplu Taşıma Rota Planlama Sistemi", 
                 font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
        
        # Sol panel (Giriş alanları)
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Rota Bilgileri", padding="10")
        self.input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Başlangıç noktası seçimi
        ttk.Label(self.input_frame, text="Başlangıç Noktası:").grid(row=1, column=0, pady=5)
        self.start_var = tk.StringVar(value="coordinate")
        ttk.Radiobutton(self.input_frame, text="Koordinat", variable=self.start_var, 
                       value="coordinate").grid(row=2, column=0)
        ttk.Radiobutton(self.input_frame, text="Durak", variable=self.start_var, 
                       value="stop").grid(row=2, column=1)
        
        # Koordinat girişi
        self.start_coord_frame = ttk.Frame(self.input_frame)
        self.start_coord_frame.grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Label(self.start_coord_frame, text="Enlem:").grid(row=0, column=0)
        self.start_lat = ttk.Entry(self.start_coord_frame, width=15)
        self.start_lat.grid(row=0, column=1)
        ttk.Label(self.start_coord_frame, text="Boylam:").grid(row=0, column=2)
        self.start_lon = ttk.Entry(self.start_coord_frame, width=15)
        self.start_lon.grid(row=0, column=3)
        
        # Durak seçimi
        self.start_stop_frame = ttk.Frame(self.input_frame)
        self.start_stop_frame.grid(row=4, column=0, columnspan=2, pady=5)
        self.start_stop_var = tk.StringVar()
        self.start_stop_combo = ttk.Combobox(self.start_stop_frame, 
                                           textvariable=self.start_stop_var,
                                           state="readonly")
        self.start_stop_combo['values'] = [stop.name for stop in self.system.stops.values()]
        self.start_stop_combo.grid(row=0, column=0)
        
        # Bitiş noktası seçimi
        ttk.Label(self.input_frame, text="Bitiş Noktası:").grid(row=5, column=0)
        self.end_var = tk.StringVar(value="coordinate")
        ttk.Radiobutton(self.input_frame, text="Koordinat", variable=self.end_var, 
                       value="coordinate").grid(row=6, column=0)
        ttk.Radiobutton(self.input_frame, text="Durak", variable=self.end_var, 
                       value="stop").grid(row=6, column=1)
        
        # Bitiş koordinat girişi
        self.end_coord_frame = ttk.Frame(self.input_frame)
        self.end_coord_frame.grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Label(self.end_coord_frame, text="Enlem:").grid(row=0, column=0)
        self.end_lat = ttk.Entry(self.end_coord_frame, width=15)
        self.end_lat.grid(row=0, column=1)
        ttk.Label(self.end_coord_frame, text="Boylam:").grid(row=0, column=2)
        self.end_lon = ttk.Entry(self.end_coord_frame, width=15)
        self.end_lon.grid(row=0, column=3)
        
        # Bitiş durak seçimi
        self.end_stop_frame = ttk.Frame(self.input_frame)
        self.end_stop_frame.grid(row=8, column=0, columnspan=2, pady=5)
        self.end_stop_var = tk.StringVar()
        self.end_stop_combo = ttk.Combobox(self.end_stop_frame, 
                                         textvariable=self.end_stop_var,
                                         state="readonly")
        self.end_stop_combo['values'] = [stop.name for stop in self.system.stops.values()]
        self.end_stop_combo.grid(row=0, column=0)
        
        # Yolcu tipi seçimi
        ttk.Label(self.input_frame, text="Yolcu Tipi:").grid(row=9, column=0)
        self.passenger_var = tk.StringVar(value="general")
        ttk.Radiobutton(self.input_frame, text="Genel", variable=self.passenger_var, 
                       value="general").grid(row=10, column=0)
        ttk.Radiobutton(self.input_frame, text="Öğrenci", variable=self.passenger_var, 
                       value="student").grid(row=10, column=1)
        ttk.Radiobutton(self.input_frame, text="Öğretmen", variable=self.passenger_var, 
                       value="teacher").grid(row=11, column=0)
        ttk.Radiobutton(self.input_frame, text="65+ Yaşlı", variable=self.passenger_var, 
                       value="elderly").grid(row=11, column=1)
        
        # Ödeme yöntemi seçimi
        ttk.Label(self.input_frame, text="Ödeme Yöntemi:").grid(row=12, column=0)
        self.payment_var = tk.StringVar(value="cash")
        ttk.Radiobutton(self.input_frame, text="Nakit", variable=self.payment_var, 
                       value="cash").grid(row=13, column=0)
        ttk.Radiobutton(self.input_frame, text="Kredi Kartı", variable=self.payment_var, 
                       value="credit").grid(row=13, column=1)
        ttk.Radiobutton(self.input_frame, text="Kent Kart", variable=self.payment_var, 
                       value="kent").grid(row=14, column=0)
        
        # Ödeme detayları frame
        self.payment_details_frame = ttk.Frame(self.input_frame)
        self.payment_details_frame.grid(row=15, column=0, columnspan=2, pady=10)
        
        # Kredi kartı detayları
        self.card_number = ttk.Entry(self.payment_details_frame, width=20)
        self.card_number.grid(row=0, column=1, pady=2)
        ttk.Label(self.payment_details_frame, text="Kart No:").grid(row=0, column=0)
        
        self.expiry_date = ttk.Entry(self.payment_details_frame, width=10)
        self.expiry_date.grid(row=1, column=1, pady=2)
        ttk.Label(self.payment_details_frame, text="Son Kullanma:").grid(row=1, column=0)
        
        self.cvv = ttk.Entry(self.payment_details_frame, width=5)
        self.cvv.grid(row=2, column=1, pady=2)
        ttk.Label(self.payment_details_frame, text="CVV:").grid(row=2, column=0)
        
        # Kent kart detayları
        self.kent_number = ttk.Entry(self.payment_details_frame, width=20)
        self.kent_number.grid(row=3, column=1, pady=2)
        ttk.Label(self.payment_details_frame, text="Kent Kart No:").grid(row=3, column=0)
        
        # Rota hesaplama butonu
        ttk.Button(self.input_frame, text="Rota Hesapla", 
                  command=self.calculate_route).grid(row=16, column=0, columnspan=2, pady=20)
        
        # Orta panel (Harita)
        self.map_frame = ttk.LabelFrame(self.main_frame, text="Durak Haritası", padding="10")
        self.map_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        # Harita widget'ı
        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, width=600, height=800)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        
        # Haritayı İzmit merkezine konumlandır
        self.map_widget.set_position(40.7654, 29.9408)  # İzmit merkez
        self.map_widget.set_zoom(13)
        
        # Durakları haritaya ekle
        self.markers = {}
        self.paths = []
        for stop in self.system.stops.values():
            # Durak tipine göre renk belirle
            color = "red" if stop.type == "bus" else "blue"
            
            # Durak işaretçisi ekle
            marker = self.map_widget.set_marker(stop.lat, stop.lon, text=stop.name, marker_color_circle=color)
            self.markers[stop.id] = marker
            
            # Durak bağlantılarını çiz
            for next_stop in stop.next_stops:
                next_stop_obj = self.system.stops[next_stop["stopId"]]
                path = self.map_widget.set_path([
                    [stop.lat, stop.lon],
                    [next_stop_obj.lat, next_stop_obj.lon]
                ])
                self.paths.append(path)
        
        # Sağ panel (Sonuçlar)
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Rota Sonuçları", padding="10")
        self.output_frame.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")
        
        # Sonuç gösterme alanı
        self.result_text = scrolledtext.ScrolledText(self.output_frame, width=60, height=40)
        self.result_text.grid(row=0, column=0, padx=5, pady=5)
        
        # Grid yapılandırması
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Harita frame'ini genişletilebilir yap
        self.map_frame.columnconfigure(0, weight=1)
        self.map_frame.rowconfigure(0, weight=1)
    
    def show_map(self):
        # Haritayı zaten gösteriyoruz, bu metodu artık kullanmıyoruz
        pass
    
    def calculate_route(self):
        try:
            # Başlangıç noktası
            if self.start_var.get() == "coordinate":
                # Koordinat alanları boş mu kontrol et
                if not self.start_lat.get() or not self.start_lon.get():
                    raise ValueError("Başlangıç koordinatları boş bırakılamaz!")
                try:
                    start_lat = float(self.start_lat.get())
                    start_lon = float(self.start_lon.get())
                    if not (40.5 <= start_lat <= 41.0) or not (29.5 <= start_lon <= 30.5):
                        raise ValueError("Başlangıç koordinatları İzmit sınırları dışında!")
                    start = Location(start_lat, start_lon)
                except ValueError as e:
                    if "could not convert string to float" in str(e):
                        raise ValueError("Başlangıç koordinatları sayısal değer olmalıdır!")
                    raise e
            else:
                # Durak seçili mi kontrol et
                if not self.start_stop_var.get():
                    raise ValueError("Başlangıç durağı seçilmedi!")
                start_stop_name = self.start_stop_var.get()
                start = next((stop for stop in self.system.stops.values() if stop.name == start_stop_name), None)
                if not start:
                    raise ValueError(f"Başlangıç durağı '{start_stop_name}' bulunamadı!")
            
            # Bitiş noktası
            if self.end_var.get() == "coordinate":
                # Koordinat alanları boş mu kontrol et
                if not self.end_lat.get() or not self.end_lon.get():
                    raise ValueError("Bitiş koordinatları boş bırakılamaz!")
                try:
                    end_lat = float(self.end_lat.get())
                    end_lon = float(self.end_lon.get())
                    if not (40.5 <= end_lat <= 41.0) or not (29.5 <= end_lon <= 30.5):
                        raise ValueError("Bitiş koordinatları İzmit sınırları dışında!")
                    end = Location(end_lat, end_lon)
                except ValueError as e:
                    if "could not convert string to float" in str(e):
                        raise ValueError("Bitiş koordinatları sayısal değer olmalıdır!")
                    raise e
            else:
                # Durak seçili mi kontrol et
                if not self.end_stop_var.get():
                    raise ValueError("Bitiş durağı seçilmedi!")
                end_stop_name = self.end_stop_var.get()
                end = next((stop for stop in self.system.stops.values() if stop.name == end_stop_name), None)
                if not end:
                    raise ValueError(f"Bitiş durağı '{end_stop_name}' bulunamadı!")
            
            # Yolcu tipi
            passenger_type = self.passenger_var.get()
            if passenger_type == "general":
                passenger = GeneralPassenger()
            elif passenger_type == "student":
                passenger = StudentPassenger()
            elif passenger_type == "teacher":
                passenger = TeacherPassenger()
            else:
                passenger = ElderlyPassenger()
            
            # Ödeme yöntemi
            payment_type = self.payment_var.get()
            if payment_type == "cash":
                payment_method = CashPayment()
            elif payment_type == "credit":
                # Kredi kartı bilgilerini kontrol et
                if not self.card_number.get() or not self.expiry_date.get() or not self.cvv.get():
                    raise ValueError("Kredi kartı bilgileri eksik!")
                payment_method = CreditCardPayment(
                    self.card_number.get(),
                    self.expiry_date.get(),
                    self.cvv.get()
                )
            else:
                # Kent kart numarasını kontrol et
                if not self.kent_number.get():
                    raise ValueError("Kent Kart numarası eksik!")
                payment_method = KentCardPayment(self.kent_number.get(), 100.0)  # Varsayılan bakiye
            
            print(f"Başlangıç: {start}")
            print(f"Bitiş: {end}")
            print(f"Yolcu: {passenger}")
            print(f"Ödeme: {payment_method}")
            
            # Rota hesaplama
            route = self.system.find_route(start, end, passenger, payment_method)
            print("Rota:", route)
            print("Rota anahtarları:", route.keys())
            
            # Sonuçları göster
            self.display_results(route, passenger, payment_method)
            
            # Rotayı haritada göster
            self.display_route_on_map(route)
            
        except ValueError as e:
            messagebox.showerror("Hata", str(e))
        except Exception as e:
            import traceback
            error_msg = f"Beklenmeyen bir hata oluştu:\n{str(e)}\n\nHata detayı:\n{traceback.format_exc()}"
            messagebox.showerror("Hata", error_msg)
            print("Hata detayı:", error_msg)
    
    def display_route_on_map(self, route):
        # Önceki rotayı temizle
        for path in self.paths:
            path.delete()
        self.paths = []
        
        # Başlangıç ve bitiş noktalarını işaretle
        if isinstance(route['start_stop'], Location):
            self.map_widget.set_marker(route['start_stop'].lat, route['start_stop'].lon,
                                     text="Başlangıç", marker_color_circle="green")
        if isinstance(route['end_stop'], Location):
            self.map_widget.set_marker(route['end_stop'].lat, route['end_stop'].lon,
                                     text="Bitiş", marker_color_circle="green")
        
        # Rota segmentlerini çiz
        for segment in route['route'].segments:
            # Segment yolunu çiz
            path = self.map_widget.set_path([
                [segment.from_stop.lat, segment.from_stop.lon],
                [segment.to_stop.lat, segment.to_stop.lon]
            ], color="green" if segment.is_transfer else "orange", width=4)
            self.paths.append(path)
    
    def display_results(self, route, passenger, payment_method):
        # Sonuç metnini temizle
        self.result_text.delete(1.0, tk.END)
        
        # Genel Bilgiler
        self.result_text.insert(tk.END, "\n=== GENEL BİLGİLER ===\n")
        general_info = [
            ["Başlangıç Noktası", route['start_stop'].name if hasattr(route['start_stop'], 'name') else f"({route['start_stop'].lat}, {route['start_stop'].lon})"],
            ["Bitiş Noktası", route['end_stop'].name if hasattr(route['end_stop'], 'name') else f"({route['end_stop'].lat}, {route['end_stop'].lon})"],
            ["Yolcu Tipi", passenger.passenger_type.value],
            ["Ödeme Yöntemi", payment_method.__class__.__name__]
        ]
        self.result_text.insert(tk.END, tabulate(general_info, tablefmt="grid"))
        
        # Başlangıç Durağına Erişim
        self.result_text.insert(tk.END, "\n\n=== BAŞLANGIÇ DURAĞINA ERİŞİM ===\n")
        start_access = route['start_access']
        start_access_info = [
            ["Mesafe", f"{start_access['distance']:.2f} km"],
            ["Önerilen Yöntem", start_access['recommended'].upper()],
            ["Sebep", start_access['reason']]
        ]
        self.result_text.insert(tk.END, tabulate(start_access_info, tablefmt="grid"))
        
        # Yürüyüş seçeneği
        if start_access['walking']['available']:
            self.result_text.insert(tk.END, "\nYürüyüş Seçeneği:\n")
            walking_info = [
                ["Süre", f"{start_access['walking']['time']:.1f} dakika"],
                ["Ücret", f"{start_access['walking']['cost']:.2f} TL"],
                ["Durum", "Mevcut"],
                ["Sebep", start_access['walking']['reason']]
            ]
            self.result_text.insert(tk.END, tabulate(walking_info, tablefmt="simple"))
        
        # Taksi seçeneği
        if start_access['taxi']['available']:
            self.result_text.insert(tk.END, "\nTaksi Seçeneği:\n")
            taxi_info = [
                ["Süre", f"{start_access['taxi']['time']:.1f} dakika"],
                ["Ücret", f"{start_access['taxi']['cost']:.2f} TL"],
                ["Durum", "Mevcut"],
                ["Sebep", start_access['taxi']['reason']]
            ]
            self.result_text.insert(tk.END, tabulate(taxi_info, tablefmt="simple"))
        
        # Rota Detayları
        self.result_text.insert(tk.END, "\n\n=== ROTA DETAYLARI ===\n")
        route_details = []
        for segment in route['route'].segments:
            route_details.append([
                segment.from_stop.name,
                segment.to_stop.name,
                segment.vehicle.__class__.__name__,
                f"{segment.distance:.1f} km",
                f"{segment.time:.1f} dk",
                f"{segment.cost:.2f} TL",
                "Aktarma" if segment.is_transfer else "Normal"
            ])
        
        headers = ["Başlangıç", "Bitiş", "Araç", "Mesafe", "Süre", "Ücret", "Tip"]
        self.result_text.insert(tk.END, tabulate(route_details, headers=headers, tablefmt="grid"))
        
        # Bitiş Durağından Çıkış
        self.result_text.insert(tk.END, "\n\n=== BİTİŞ DURAĞINDAN ÇIKIŞ ===\n")
        end_access = route['end_access']
        end_access_info = [
            ["Mesafe", f"{end_access['distance']:.2f} km"],
            ["Önerilen Yöntem", end_access['recommended'].upper()],
            ["Sebep", end_access['reason']]
        ]
        self.result_text.insert(tk.END, tabulate(end_access_info, tablefmt="grid"))
        
        # Yürüyüş seçeneği
        if end_access['walking']['available']:
            self.result_text.insert(tk.END, "\nYürüyüş Seçeneği:\n")
            walking_info = [
                ["Süre", f"{end_access['walking']['time']:.1f} dakika"],
                ["Ücret", f"{end_access['walking']['cost']:.2f} TL"],
                ["Durum", "Mevcut"],
                ["Sebep", end_access['walking']['reason']]
            ]
            self.result_text.insert(tk.END, tabulate(walking_info, tablefmt="simple"))
        
        # Taksi seçeneği
        if end_access['taxi']['available']:
            self.result_text.insert(tk.END, "\nTaksi Seçeneği:\n")
            taxi_info = [
                ["Süre", f"{end_access['taxi']['time']:.1f} dakika"],
                ["Ücret", f"{end_access['taxi']['cost']:.2f} TL"],
                ["Durum", "Mevcut"],
                ["Sebep", end_access['taxi']['reason']]
            ]
            self.result_text.insert(tk.END, tabulate(taxi_info, tablefmt="simple"))
        
        # Toplam Bilgiler
        self.result_text.insert(tk.END, "\n\n=== TOPLAM BİLGİLER ===\n")
        total_info = [
            ["Toplam Mesafe", f"{route['route'].total_distance:.2f} km"],
            ["Toplam Süre", f"{route['route'].total_time:.1f} dakika"],
            ["Toplam Ücret", f"{route['route'].total_cost:.2f} TL"],
            ["Aktarma Sayısı", str(route['route'].transfer_count)],
            ["Başlangıçta Taksi", "Evet" if route['route'].requires_initial_taxi else "Hayır"],
            ["Sonda Taksi", "Evet" if route['route'].requires_final_taxi else "Hayır"]
        ]
        self.result_text.insert(tk.END, tabulate(total_info, tablefmt="grid"))

if __name__ == "__main__":
    root = tk.Tk()
    app = TransportationGUI(root)
    root.mainloop() 