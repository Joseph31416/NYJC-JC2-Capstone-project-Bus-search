class Config:

    def __init__(self):
        self.GROUP_PAYMENT = {
            ("adult", "cash"): "Adult_cash_fare",
            ("adult", "card"): "Adult_card_fare",
            ("senior", "cash"): "Senior_cash_fare",
            ("senior", "card"): "Senior_card_fare",
            ("student", "cash"): "Student_cash_fare",
            ("student", "card"): "Student_card_fare",
            ("workfare", "cash"): "Workfare_cash_fare",
            ("workfare", "card"): "Workfare_card_fare",
            ("disabilities", "cash"): "Disabilities_cash_fare",
            ("disabilities", "card"): "Disabilities_card_fare"
        }
        self.DB_PATH = "./records.db"
        self.MODE = ["distance", "fare"]
        self.GROUP = ["adult", "student", "senior", "workfare", "disabilities"]
        self.PAYMENT_MODE = ["cash", "card"]
