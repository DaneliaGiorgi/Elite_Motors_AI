from logger import ShowroomLogger

class Showroom:
    """Manages showroom statistics and reporting logic."""
    
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.inventory = [] # This will be populated from the Database by the Agent

    def get_financials_report(self, inventory_data):
        """Calculates total value and unit counts from provided database records."""
        if not inventory_data:
            ShowroomLogger.log_error("Attempted to generate report for empty inventory.")
            return "Inventory is empty."
        
        # inventory_data schema: (car_id, brand, year, price, quantity)
        # Price is at index 3, Quantity is at index 4
        total_value = sum(row[3] * row[4] for row in inventory_data)
        total_units = sum(row[4] for row in inventory_data)
        avg_price = total_value / total_units if total_units > 0 else 0
        
        ShowroomLogger.log(f"Financial report generated for {self.name}.")
        
        return {
            "total_value": float(total_value),
            "total_units": total_units,
            "average_price": round(float(avg_price), 2)
        }