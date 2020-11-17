class Receipt:
    total = None
    store = None
    date = None
    items = []

    def __init__(self, total : float, store : str, date : str, items : list):
        self.total = total
        self.store = store
        self.date = date
        self.items = items

    def __str__(self):
        res = ""
        res += str(self.total) + "\n"
        res += str(self.store) + "\n"
        res += str(self.date) + "\n"
        for item in self.items:
            res += str(item[0]) + ": " + str(item[1])
        return res
    
    def print(self):
        print(str(self))

    def isSound(self):
        return round(sum([y[1] for y in self.items]), 2) == self.total