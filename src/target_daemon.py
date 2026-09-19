import argparse
import pyautogui
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import Response
from pydantic import BaseModel

from actions import capture_screen, execute_tool

app = FastAPI(title="Cognita Remote Target Daemon")
AUTH_TOKEN = ""


class ToolRequest(BaseModel):
    name: str
    args: dict


def verify_token(authorization: str = Header(None)):
    if AUTH_TOKEN and authorization != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/info", dependencies=[Depends(verify_token)])
def get_info():
    w, h = pyautogui.size()
    return {"width": w, "height": h}


@app.get("/screen", dependencies=[Depends(verify_token)])
def get_screen():
    try:
        jpeg_bytes = capture_screen()
        return Response(content=jpeg_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute", dependencies=[Depends(verify_token)])
def execute_tool_endpoint(req: ToolRequest):
    w, h = pyautogui.size()
    try:
        result = execute_tool(req.name, req.args, w, h)
        return {"result": result}
    except pyautogui.FailSafeException:
        raise HTTPException(
            status_code=400, detail="PyAutoGUI fail-safe triggered on target.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Target execution error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cognita Remote Target Daemon")
    parser.add_argument("--host", default="0.0.0.0", help="Binding host")
    parser.add_argument("--port", type=int, default=8765, help="Binding port")
    parser.add_argument("--token", default="", help="Secret security token")
    args = parser.parse_args()

    AUTH_TOKEN = args.token
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.3

    import uvicorn
    print(f"Cognita Daemon running on {args.host}:{args.port}")
    if AUTH_TOKEN:
        print("Security token is enabled.")
    uvicorn.run(app, host=args.host, port=args.port)
