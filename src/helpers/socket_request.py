import json
from typing import Dict, List, Optional
import websockets


class WebSocketClient:
    """Client for connecting to external WebSocket services."""
    
    @staticmethod
    async def connect_and_listen(ws_url: str, data: Dict, headers: Optional[Dict] = None) -> List[Dict]:
        """
        Connect to a WebSocket and listen for all messages until connection closes.
        
        Args:
            ws_url: URL of the WebSocket to connect to
            headers: Optional headers for the WebSocket connection
            
        Returns:
            List of received messages
        """
        messages = []
        try:
            async with websockets.connect(ws_url, additional_headers=headers) as websocket:
                print(f"Connected to WebSocket at {ws_url}")
                
                while True:
                    try:
                        await websocket.send(json.dumps(data), text=True)  # Send initial data
                        message = await websocket.recv()
                        print(f"Received message: {message[:100]}...")
                        
                        # Try to parse JSON, but store raw message if not JSON
                        try:
                            parsed_message = json.loads(message)
                            messages.append(parsed_message)
                        except json.JSONDecodeError:
                            messages.append({"raw_message": message})
                            
                    except websockets.ConnectionClosed:
                        print("WebSocket connection closed by server")
                        break
                        
        except Exception as e:
            print(f"Error in WebSocket connection: {str(e)}")
            messages.append({"error": str(e)})
            
        return messages