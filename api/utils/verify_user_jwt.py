import os
from fastapi import HTTPException
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def verify_user(token):
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return HTTPException(status_code=401, detail="User doesn't exist")
        return user
    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))