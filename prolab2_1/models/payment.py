from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class PaymentMethod(ABC):
    def __init__(self):
        self.transaction_history = []
    
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """Ödeme işlemini gerçekleştir"""
        pass
    
    def add_transaction(self, amount: float, success: bool) -> None:
        """İşlem geçmişine yeni ödeme ekle"""
        self.transaction_history.append({
            "amount": amount,
            "success": success,
            "timestamp": datetime.now()
        })
    
    def get_balance(self) -> Optional[float]:
        """Mevcut bakiyeyi döndür (varsa)"""
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Ödeme yöntemi bilgilerini sözlük olarak döndür"""
        return {
            "type": self.__class__.__name__,
            "balance": self.get_balance(),
            "transaction_count": len(self.transaction_history)
        }

class CashPayment(PaymentMethod):
    def __init__(self, initial_amount: float = 0.0):
        super().__init__()
        self.amount = initial_amount
    
    def process_payment(self, amount: float) -> bool:
        if self.amount >= amount:
            self.amount -= amount
            self.add_transaction(amount, True)
            return True
        self.add_transaction(amount, False)
        return False
    
    def get_balance(self) -> float:
        return self.amount

class CreditCardPayment(PaymentMethod):
    def __init__(self, card_number: str, expiry_date: str, cvv: str, limit: float = 1000.0):
        super().__init__()
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv
        self.limit = limit
        self.current_usage = 0.0
    
    def process_payment(self, amount: float) -> bool:
        if self.current_usage + amount <= self.limit:
            self.current_usage += amount
            self.add_transaction(amount, True)
            return True
        self.add_transaction(amount, False)
        return False
    
    def get_balance(self) -> float:
        return self.limit - self.current_usage

class KentCardPayment(PaymentMethod):
    def __init__(self, card_number: str, balance: float):
        super().__init__()
        self.card_number = card_number
        self.balance = balance
    
    def process_payment(self, amount: float) -> bool:
        if self.balance >= amount:
            self.balance -= amount
            self.add_transaction(amount, True)
            return True
        self.add_transaction(amount, False)
        return False
    
    def get_balance(self) -> float:
        return self.balance 