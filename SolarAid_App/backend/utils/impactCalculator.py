"""
Impact Calculator for Sadaqah Jariah Certificate
Calculates environmental and human impact metrics from kWh donation
"""

def calculate_impact(kwh_input):
    """
    Calculate impact metrics from kWh input
    
    Args:
        kwh_input (float): Amount of kWh donated
        
    Returns:
        dict: Impact metrics including CO2, and human stories
    """
    
    # --- SECTION 1: ENVIRONMENTAL IMPACT ---
    # Source: Energy Commission Malaysia Grid Emission Factor
    # Formula: 0.76 kg of CO2 per kWh
    co2_saved = round(kwh_input * 0.76, 2)
    
    # --- SECTION 3: HUMAN IMPACT STORIES ---
    
    # Story A: Rural Clinic (Vaccine Fridge)
    # Formula: (Input / 0.6) * 24 hours
    vaccine_fridge_hours = int((kwh_input / 0.6) * 24)
    
    # Story B: Education (Classroom LEDs)
    # Formula: Input / 0.18 (180W load)
    study_hours = int(kwh_input / 0.18)
    
    # Story C: Disaster Relief (Phone Charging)
    # Formula: Input / 0.015 (15Wh battery)
    phones_charged = int(kwh_input / 0.015)
    
    # Story D: Basic Comfort (Ceiling Fan)
    # Formula: Input / 0.06 (60W Fan)
    fan_hours = int(kwh_input / 0.06)
    
    return {
        "kwh": kwh_input,
        "co2_kg": co2_saved,
        "stories": {
            "clinic": {
                "val": vaccine_fridge_hours,
                "unit": "Hours of Vaccine Protection"
            },
            "school": {
                "val": study_hours,
                "unit": "Hours of Study Light"
            },
            "disaster": {
                "val": phones_charged,
                "unit": "Phones Charged for Families"
            },
            "home": {
                "val": fan_hours,
                "unit": "Hours of Cooling Comfort"
            }
        }
    }
