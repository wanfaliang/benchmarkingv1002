"""WebSocket endpoints for real-time updates"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.websocket_manager import manager
from ..core.security import decode_access_token
from ..services.analysis_service import get_analysis_by_id
from ..models.user import User
import asyncio

router = APIRouter(prefix="/api/ws", tags=["websocket"])

# Allowed origins for WebSocket connections
ALLOWED_ORIGINS = [
    "https://finexus.net",
    "https://www.finexus.net", 
    "https://api.finexus.net",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


@router.websocket("/analysis/{analysis_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    analysis_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time analysis updates.
    
    CRITICAL: Must accept() connection FIRST, then validate
    """
    
    # ============================================
    # STEP 1: ACCEPT CONNECTION IMMEDIATELY
    # ============================================
    await websocket.accept()
    print(f"🔌 WebSocket accepted for analysis: {analysis_id}")
    
    # ============================================
    # STEP 2: VALIDATE TOKEN
    # ============================================
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            print(f"❌ Invalid token - no user_id")
            await websocket.close(code=1008, reason="Invalid token")
            return
        print(f"✅ Token valid for user: {user_id}")
    except Exception as e:
        print(f"❌ Token validation failed: {str(e)}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # ============================================
    # STEP 3: VERIFY USER EXISTS
    # ============================================
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            print(f"❌ User not found: {user_id}")
            await websocket.close(code=1008, reason="User not found")
            return
        print(f"✅ User found: {user.email}")
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        await websocket.close(code=1008, reason="Database error")
        return
    
    # ============================================
    # STEP 4: VERIFY ANALYSIS ACCESS
    # ============================================
    try:
        analysis = get_analysis_by_id(db, analysis_id, user)
        if not analysis:
            print(f"❌ Analysis not found or unauthorized: {analysis_id}")
            await websocket.close(code=1008, reason="Analysis not found")
            return
        print(f"✅ Analysis access granted: {analysis.name}")
    except Exception as e:
        print(f"❌ Authorization failed: {str(e)}")
        await websocket.close(code=1008, reason=f"Authorization failed")
        return
    
    # ============================================
    # STEP 5: REGISTER WITH CONNECTION MANAGER
    # ============================================
    await manager.connect(websocket, analysis_id, user_id)
    
    # ============================================
    # STEP 6: SEND INITIAL CONFIRMATION
    # ============================================
    await websocket.send_json({
        'type': 'connected',
        'analysis_id': analysis_id,
        'analysis_name': analysis.name,
        'message': 'WebSocket connection established'
    })
    
    print(f"✅ WebSocket fully connected - User: {user.email}, Analysis: {analysis.name}")
    
    # ============================================
    # STEP 7: KEEP CONNECTION ALIVE
    # ============================================
    try:
        while True:
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_json({'type': 'pong'})
                print("💓 Pong sent")
    
    except WebSocketDisconnect:
        print(f"🔌 Client disconnected - User: {user.email}")
        manager.disconnect(websocket, analysis_id, user_id)
    
    except Exception as e:
        print(f"❌ WebSocket error: {type(e).__name__}: {str(e)}")
        manager.disconnect(websocket, analysis_id, user_id)

@router.websocket("/test")
async def test_websocket(websocket: WebSocket):
    """Dead simple WebSocket for testing - NO AUTO PING"""
    print("=" * 50)
    print("🧪 TEST WEBSOCKET - Connection attempt")
    
    await websocket.accept()
    print("✅ Connection accepted!")
    
    # Send ONE greeting message
    await websocket.send_json({
        "message": "Hello! WebSocket is working!",
        "timestamp": "now"
    })
    print("📨 Sent greeting message")
    
    # Just wait for client messages (no auto-ping)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📨 Received from client: {data}")
            
            # Echo it back
            await websocket.send_json({
                "echo": data,
                "message": "You said: " + data
            })
            
    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {e}")
