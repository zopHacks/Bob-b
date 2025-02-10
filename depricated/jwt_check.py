from fastapi import HTTPException
from supabase import Client, create_client
import os

def verify_jwtv002(token: str):
    try: 
        print(token)
        SUPABASE_URL = os.environ["SUPABASE_URL"]
        SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        user = supabase.auth.get_user(token)
        return user
    except:
        raise HTTPException(500, detail={"error": "supabase cannot authenticate user"})