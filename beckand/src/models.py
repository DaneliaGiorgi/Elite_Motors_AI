#Base class for all vehicles in the system
#Defines common properties like brand, year, and pricing
class Vehicle:
    def __init__(self, brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):          
        self.brand = brand
        self.year = int(year) 
        self.mileage = int(mileage) 
        self.price = int(price) 
        self.quantity = int(quantity) 
        self.warranty_period = warranty_period
        self.warranty_type = warranty_type
        self.e_sign_eligible = e_sign_eligible

    #Abstract method to be implemented by child classes
    def drive(self):
        raise NotImplementedError("drive method must be implemented by subclasses.")

#Specialized class for Electric Cars, inheriting from Vehicle
class ElectroCar(Vehicle):
    def __init__(self, brand, year, battery_capacity, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):
        # Calling the base class constructor
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.battery_capacity = battery_capacity
    
    #Specific logic for electric cars
    def drive(self):
        return f"Electric {self.brand} ({self.year}) with {self.battery_capacity} kWh battery."

#Specialized class for Trucks, inheriting from Vehicle
class Truck(Vehicle):
    def __init__(self, brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible, max_load):
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.max_load = max_load

    # Specific logic for trucks
    def drive(self):
        return f"{self.brand} truck with max load capacity of {self.max_load}."
    
#Specialized class for Gasoline Cars, inheriting from Vehicle
class GasolineCar(Vehicle):
    def __init__(self, brand, year, engine_volume, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible):
        super().__init__(brand, year, mileage, price, quantity, warranty_period, warranty_type, e_sign_eligible)
        self.engine_volume = engine_volume
    
    #Specific logic for gasoline cars
    def drive(self):
        return f"Gasoline {self.brand} ({self.year}) with {self.engine_volume}L engine."