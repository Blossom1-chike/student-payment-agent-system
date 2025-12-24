from datetime import datetime, timedelta
def get_date_cheat_sheet():
    """Generates a text list of the next 14 days for the LLM"""
    now = datetime.now()
    cheat_sheet = "**CALENDAR REFERENCE (Use this to find dates):**\n"
    for i in range(15):
        day = now + timedelta(days=i)
        # Format: "Wednesday, Dec 17"
        cheat_sheet += f"- +{i} days ({day.strftime('%A')}): {day.strftime('%Y-%m-%d')}\n"
    return cheat_sheet