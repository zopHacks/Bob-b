import os
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv
import asyncio

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBearer()

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # print("Token received:", token)
    try:
        user = supabase.auth.get_user(token)
        # print("User:", user)
        if not user:
            return HTTPException(status_code=401, detail="User doesn't exist")
        return user
    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))
    
async def verify_jwt2(credentials):
    print("I'm running")
    print("I'm running")
    # print("Token received:", token)
    try:
        user = supabase.auth.get_user(credentials)
        print("User:", user)
        if not user:
            return HTTPException(status_code=401, detail="User doesn't exist")
        print(user)
        return user
    except Exception as e:
        return HTTPException(status_code=401, detail=str(e))


# user = asyncio.run(verify_jwt2("eyJhbGciOiJIUzI1NiIsImtpZCI6ImhuTk95NnNMZVRFSUY1Y1ciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2ZqcHV1cm92Ym5oeXlrZGJia3BqLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJlY2M2NTc1OC0xYzExLTRlMDQtOGEwNy1hNmVhMzVhZDViMTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzM5MTc3NjE2LCJpYXQiOjE3MzkxNzQwMTYsImVtYWlsIjoiYWxpYW5jZS5yb2JvdGljc0BnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiYWxpYW5jZS5yb2JvdGljc0BnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiJlY2M2NTc1OC0xYzExLTRlMDQtOGEwNy1hNmVhMzVhZDViMTQifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTczODg2MzM4NX1dLCJzZXNzaW9uX2lkIjoiZjRjMmFlOGYtZGNkYS00ZTY0LTgyMjQtNmJiMGMxODQ0ZDBlIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.RU6YYTG9rCgp-t5mGefoZePaNR32iZXqE3zgbAQ1cxM"))
# print(user)