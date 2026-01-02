import os
import json
from models import ElectroCar, GasolineCar, Truck
from logger import ShowroomLogger

# The main management class for the dealership showroom
class Showroom:
    def __init__(self, name, addres):
        # Storing dealership info in a tuple
        self.info = (name, addres)
        # Main list to store all vehicle objects in memory
        self.inventory = [] 
        
    # Method to register a new vehicle object in the showroom
    def add_vehicle(self, car):
        self.inventory.append(car)
        # Log the addition of a new vehicle
        ShowroomLogger.log(f"Vehicle added: {car.brand} ({car.year})")
        
    # Converts in-memory objects into a JSON format for persistence
    def save_to_db(self, filename):
        list_to_save = []
        for item in self.inventory:
            # Map object attributes to a dictionary format
            car_data = {
                "brand": item.brand,
                "year": item.year,
                "mileage": item.mileage,
                "price": item.price,
                "quantity": item.quantity,
                "warranty_period": item.warranty_period,
                "warranty_type": item.warranty_type,
                "e_sign_eligible": item.e_sign_eligible,
                
                # Determine type label and capture class-specific info
                "type": "Electric" if isinstance(item, ElectroCar) else ("Gasoline" if isinstance(item, GasolineCar) else "Truck")
            }
            
            # Map the specific technical attribute
            if isinstance(item, ElectroCar):
                car_data["extra_info"] = item.battery_capacity
            elif isinstance(item, GasolineCar):
                car_data["extra_info"] = item.engine_volume
            elif isinstance(item, Truck):
                car_data["extra_info"] = item.max_load
            else:
                continue
            list_to_save.append(car_data)
        try:
            # Save the dictionary list to a physical JSON file
            with open(filename, 'w', encoding="utf-8") as file:
                json.dump(list_to_save, file, indent=4, ensure_ascii=False)
            print(f"✅ Full inventory sync complete: {filename}")
        except Exception as e:
            print(f"❌ Critical Sync Error: {e}")
            
    # Reads the JSON file and reconstructs Python objects (ElectroCar or Truck)
    def load_from_db(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 1. Clear current memory to avoid duplicates (Count: 10 issue)
                self.inventory = [] 
                
                for item in data:
                    # 2. Extract data with defaults
                    brand = item.get('brand', 'Unknown')
                    year = item.get('year', 0)
                    mileage = item.get('mileage', 0)
                    price = item.get('price', 0)
                    qty = item.get('quantity', 0)
                    w_period = item.get('warranty_period', 0)
                    w_type = item.get('warranty_type', 'None')
                    e_sign = item.get('e_sign_eligible', False)
                    extra = item.get('extra_info', 0)
                    car_type = item.get('type')

                    # 3. Create REAL objects, not just strings!
                    if car_type == 'Electric':
                        new_car = ElectroCar(brand, year, extra, mileage, price, qty, w_period, w_type, e_sign)
                    elif car_type == 'Gasoline':
                        new_car = GasolineCar(brand, year, extra, mileage, price, qty, w_period, w_type, e_sign)
                    elif car_type == 'Truck':
                        new_car = Truck(brand, year, mileage, price, qty, w_period, w_type, e_sign, extra)
                    else:
                        continue # Skip unknown types

                    # 4. Add the actual OBJECT to inventory
                    self.inventory.append(new_car)
                    
            print(f"✅ [DEBUG] Inventory synced. Count: {len(self.inventory)}")
            
        except FileNotFoundError:
            self.inventory = []
            print("⚠️ [DEBUG] File not found. Starting fresh.")
        except Exception as e:
            print(f"❌ [DEBUG] Load error: {e}")
        
    # Demonstrates Polymorphism: calls drive() on every vehicle regardless of its class
    def start_all_engines(self):
        for car in self.inventory:
            try:
                print(car.drive()) 
            except AttributeError:
                # Fallback if an object doesn't have a drive method
                print(f"Error: Object {car.brand} has't drive method!")
            except Exception as e:
                print(f"Error: {e}")
                
    # Helper method to get the count of each vehicle type
    def get_stats(self):
        stats = {"Electric": 0, "Gasoline": 0, "Truck": 0}
        for item in self.inventory:
            if isinstance(item, ElectroCar):
                stats["Electric"]+=1
            elif isinstance(item, GasolineCar):
                stats["Gasoline"]+=1
            elif isinstance(item, Truck):
                stats["Truck"]+=1
        return stats
    
    #remove car 
    def remove_car(self, brand, year):
        original_count = len(self.inventory)
        # Filter out the vehicle matching the specified brand and year
        self.inventory = [car for car in self.inventory if not (car.brand.lower() == brand.lower() and int(car.year) == int(year))]
        
        if len(self.inventory) < original_count:
            ShowroomLogger.log(f"Vehicle removed: {brand} ({year})")
            return True
        
        # Log failed attempt if vehicle was not found
        ShowroomLogger.log_error(f"Failed to remove: {brand} ({year}) not found.")
        return False
        

    # 2. update vehicle details
    def update_vehicle(self, brand, year, field, new_value):
        # Normalize the field name to match object attributes
        field = field.lower().strip()
        field_map = {
            "ფასი": "price", "გარბენი": "mileage", 
            "რაოდენობა": "quantity", "წელი": "year"
        }
        field = field_map.get(field, field)
        
        for item in self.inventory:
            if brand.lower().strip() in item.brand.lower() and int(item.year) == int(year):
                if hasattr(item, field):
                    # Convert numeric values correctly
                    try:
                        # Convert numeric values correctly
                        if field in ["price", "mileage", "quantity", "year"]:
                            clean_val = str(new_value).replace('$', '').replace(',', '').strip()
                            new_value = int(float(clean_val))
                        
                        # Apply the new value to the vehicle object
                        setattr(item, field, new_value)
                        
                        # LOGGING SUCCESS: Record the successful update
                        ShowroomLogger.log(f"SUCCESS: Updated {item.brand} ({item.year}) - {field} is now {new_value}")
                        return True
                    except (ValueError, TypeError):
                        # LOGGING ERROR: Record conversion failure
                        ShowroomLogger.log_error(f"CONVERSION ERROR: Failed to update {field} for {brand}: {e}")
        
        # LOGGING ERROR: Record if the vehicle wasn't found in inventory
        ShowroomLogger.log_error(f"NOT FOUND: Could not find {brand} ({year}) for update.")
        return False 
    
    # 3. financial report logic
    def get_financials_report(self):
        if not self.inventory:
            return "Inventory is empty."
        
        total_value = sum(car.price * car.quantity for car in self.inventory)
        total_units = sum(car.quantity for car in self.inventory)
        avg_price = total_value / total_units if total_units > 0 else 0
        
        return {
            "total_value": total_value,
            "total_units": total_units,
            "average_price": round(avg_price, 2)
        }