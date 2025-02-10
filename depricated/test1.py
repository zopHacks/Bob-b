from fastapi import APIRouter, Depends
from utils.auth_user_jwt import verify_jwt
import json
router = APIRouter()

@router.get("/test")
def test1(user=Depends(verify_jwt)):
    return "hey1"


# // export const getThreadID = async () => {
# //   const token = await getJWTtoken();
# //   if (!token) return { error: "Unauthorized" };

# //   try {
# //     const response = await fetch("http://127.0.0.1:8000/llms/threadid", {
# //       method: "GET",
# //       headers: {
# //         "Authorization": `Bearer ${token}`
# //       },
# //     });
# //     return response.json();
# //   } catch {
# //     throw new Error("API error");
# //   }
# // };
#