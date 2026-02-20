"""Travel agent tools - three simple tools for Greece trip planning."""

from strands import tool


@tool
def get_travel_preferences():
    """Get user's travel preferences."""
    return {
        "hotel_type": "mid-range",
        "food_preference": "vegetarian",
        "budget_range": "moderate",
    }


@tool
def calculate_budget(total_budget: int, days: int):
    """Calculate daily budget allocation for a trip.

    Args:
        total_budget: Total trip budget in USD
        days: Number of days for the trip
    """
    daily_budget = total_budget / days
    return {
        "daily_budget": round(daily_budget, 2),
        "allocation": {
            "flights": round(total_budget * 0.24, 2),
            "hotels": round(total_budget * 0.36, 2),
            "food": round(total_budget * 0.20, 2),
            "activities": round(total_budget * 0.16, 2),
            "buffer": round(total_budget * 0.04, 2),
        },
    }


@tool
def get_destination_info(destination: str):
    """Get information about a Greek travel destination.

    Args:
        destination: Name of the destination (e.g. 'athens', 'santorini', 'mykonos')
    """
    destinations = {
        "athens": {
            "country": "Greece",
            "currency": "EUR",
            "language": "Greek",
            "best_for": "History, culture, food",
            "attractions": [
                "Acropolis & Parthenon",
                "Ancient Agora",
                "Plaka neighborhood (old town)",
            ],
        },
        "santorini": {
            "country": "Greece",
            "currency": "EUR",
            "language": "Greek",
            "best_for": "Romance, sunsets, volcanic scenery",
            "attractions": [
                "Oia sunset views",
                "Red Beach & Black Sand beaches",
                "Boat tour to volcanic islands",
            ],
        },
        "mykonos": {
            "country": "Greece",
            "currency": "EUR",
            "language": "Greek",
            "best_for": "Nightlife, beaches, cosmopolitan vibe",
            "attractions": [
                "Windmills & Little Venice",
                "Delos island (ancient ruins)",
                "Beach clubs",
            ],
        },
    }
    key = destination.lower()
    if key not in destinations:
        return {
            "error": f"Destination '{destination}' not found.",
            "available": list(destinations.keys()),
        }
    return destinations[key]
