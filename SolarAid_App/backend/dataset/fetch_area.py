from backend.database.supabase import supabase

def get_area_data():
    try:
        result = supabase.table("area").select("*").execute()

        if not result.data:
            return []

        return result.data

    except Exception as e:
        print("❌ Error fetching area data:", e)
        return []
