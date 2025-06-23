class ResourceManager:
    def __init__(self, initial_points=0):
        self.points = initial_points

    def add_points(self, amount):
        self.points += amount

    def deduct_points(self, amount):
        self.points -= amount

    def get_points(self):
        return self.points
