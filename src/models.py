# Base class for all vehicles in the system
# Defines common properties like brand and fuel level
class Vehicle:
    def __init__(self, brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):          
        self.brand = brand
        self.year = int(year) # Force integer
        self.mileage = int(mileage) # Force integer
        self.price = int(price) # Force integer
        self.quantity = int(quantity) # Force integer
        self.warranty_period = warranty_period
        self.warranty_type = warranty_type
        self.e_sign_eligible = e_sign_eligible

    # Abstract method to be implemented by child classes
    def drive(self):
        raise NotImplementedError("driver method must be implemented by subclasses.")

# Specialized class for Electric Cars, inheriting from Vehicle
class ElectroCar(Vehicle):
    def __init__(self, brand, year, battery_capacity, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):
       # Calling the base class constructor
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.battery_capacity = battery_capacity
    
    # Implementing the specific released year logic for electric cars
    def drive(self):
        return f"{self.brand} released in {self.year} year"

# Specialized class for Trucks, inheriting from Vehicle
class Truck(Vehicle):
    def __init__(self, brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible, max_load):
        # Calling the base class constructor
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.max_load = max_load

     # Implementing the powerful movement logic for trucks
    def drive(self):
        return f"{self.brand} has {self.max_load} power"
    
# Specialized class for gasoline Cars, inheriting from Vehicle
class GasolineCar(Vehicle):
    def __init__(self, brand, year, engine_volume, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):
       # Calling the base class constructor
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.engine_volume = engine_volume
    
    # Implementing the specific released year logic for gasoline cars
    def drive(self):
        return f"{self.brand} released in {self.year} year"


