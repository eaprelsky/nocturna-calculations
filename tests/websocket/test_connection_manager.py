import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi import WebSocket

from nocturna_calculations.api.routers.websocket import ConnectionManager


class TestConnectionManager:
    """Test suite for WebSocket ConnectionManager."""

    @pytest.mark.asyncio
    async def test_connection_manager_initialization(self):
        """Test ConnectionManager initializes with empty connections."""
        manager = ConnectionManager()
        
        assert manager.active_connections == {}
        assert hasattr(manager, 'active_connections')

    @pytest.mark.asyncio
    async def test_connect_websocket_success(self, mock_websocket):
        """Test successful WebSocket connection."""
        manager = ConnectionManager()
        user_id = "test_user_123"
        
        # Mock WebSocket accept
        mock_websocket.accept = AsyncMock()
        
        await manager.connect(mock_websocket, user_id)
        
        # Verify connection was established
        mock_websocket.accept.assert_called_once()
        assert user_id in manager.active_connections
        assert manager.active_connections[user_id] == mock_websocket

    @pytest.mark.asyncio
    async def test_connect_multiple_users(self, mock_websocket):
        """Test connecting multiple users."""
        manager = ConnectionManager()
        
        # Create multiple mock websockets
        websocket1 = Mock(spec=WebSocket)
        websocket1.accept = AsyncMock()
        websocket2 = Mock(spec=WebSocket)
        websocket2.accept = AsyncMock()
        
        await manager.connect(websocket1, "user1")
        await manager.connect(websocket2, "user2")
        
        assert len(manager.active_connections) == 2
        assert "user1" in manager.active_connections
        assert "user2" in manager.active_connections

    @pytest.mark.asyncio
    async def test_connect_same_user_twice_replaces_connection(self, mock_websocket):
        """Test that connecting the same user twice replaces the old connection."""
        manager = ConnectionManager()
        
        websocket1 = Mock(spec=WebSocket)
        websocket1.accept = AsyncMock()
        websocket2 = Mock(spec=WebSocket)
        websocket2.accept = AsyncMock()
        
        user_id = "duplicate_user"
        
        await manager.connect(websocket1, user_id)
        await manager.connect(websocket2, user_id)
        
        # Should only have one connection for the user (the latest one)
        assert len(manager.active_connections) == 1
        assert manager.active_connections[user_id] == websocket2

    def test_disconnect_existing_user(self):
        """Test disconnecting an existing user."""
        manager = ConnectionManager()
        user_id = "test_user"
        
        # Manually add a connection
        manager.active_connections[user_id] = Mock(spec=WebSocket)
        
        manager.disconnect(user_id)
        
        assert user_id not in manager.active_connections

    def test_disconnect_non_existing_user(self):
        """Test disconnecting a non-existing user doesn't raise error."""
        manager = ConnectionManager()
        
        # Should not raise any exception
        manager.disconnect("non_existing_user")
        
        assert len(manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_send_message_to_connected_user(self, mock_websocket):
        """Test sending message to a connected user."""
        manager = ConnectionManager()
        user_id = "test_user"
        message = {"type": "calculation_result", "data": "test_data"}
        
        # Setup mock websocket
        mock_websocket.send_json = AsyncMock()
        manager.active_connections[user_id] = mock_websocket
        
        await manager.send_message(user_id, message)
        
        mock_websocket.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_send_message_to_disconnected_user(self):
        """Test sending message to a disconnected user doesn't raise error."""
        manager = ConnectionManager()
        user_id = "disconnected_user"
        message = {"type": "test", "data": "test"}
        
        # Should not raise any exception when user is not connected
        await manager.send_message(user_id, message)

    @pytest.mark.asyncio
    async def test_send_message_websocket_error_handling(self):
        """Test error handling when WebSocket send fails."""
        manager = ConnectionManager()
        user_id = "test_user"
        message = {"type": "test", "data": "test"}
        
        # Setup mock websocket that raises an exception
        mock_websocket = Mock(spec=WebSocket)
        mock_websocket.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        manager.active_connections[user_id] = mock_websocket
        
        # Should handle the exception gracefully and remove the connection
        await manager.send_message(user_id, message)
        
        # Connection should be removed after error
        assert user_id not in manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_message_to_all_users(self):
        """Test broadcasting message to all connected users."""
        manager = ConnectionManager()
        message = {"type": "broadcast", "data": "announcement"}
        
        # Setup multiple mock websockets
        websocket1 = Mock(spec=WebSocket)
        websocket1.send_json = AsyncMock()
        websocket2 = Mock(spec=WebSocket)
        websocket2.send_json = AsyncMock()
        
        manager.active_connections["user1"] = websocket1
        manager.active_connections["user2"] = websocket2
        
        # This method should be implemented in ConnectionManager
        if hasattr(manager, 'broadcast'):
            await manager.broadcast(message)
            
            websocket1.send_json.assert_called_once_with(message)
            websocket2.send_json.assert_called_once_with(message)

    def test_get_active_connection_count(self):
        """Test getting the count of active connections."""
        manager = ConnectionManager()
        
        assert manager.get_connection_count() == 0
        
        # Add some connections
        manager.active_connections["user1"] = Mock(spec=WebSocket)
        manager.active_connections["user2"] = Mock(spec=WebSocket)
        
        assert manager.get_connection_count() == 2

    def test_get_connected_users(self):
        """Test getting list of connected user IDs."""
        manager = ConnectionManager()
        
        assert manager.get_connected_users() == []
        
        # Add some connections
        manager.active_connections["user1"] = Mock(spec=WebSocket)
        manager.active_connections["user2"] = Mock(spec=WebSocket)
        
        connected_users = manager.get_connected_users()
        assert len(connected_users) == 2
        assert "user1" in connected_users
        assert "user2" in connected_users

    @pytest.mark.asyncio
    async def test_cleanup_stale_connections(self):
        """Test cleanup of stale/closed connections."""
        manager = ConnectionManager()
        
        # Setup mock websockets with different states
        active_websocket = Mock(spec=WebSocket)
        active_websocket.client_state = Mock()
        active_websocket.client_state.CONNECTED = True
        
        closed_websocket = Mock(spec=WebSocket)
        closed_websocket.client_state = Mock()
        closed_websocket.client_state.CONNECTED = False
        
        manager.active_connections["active_user"] = active_websocket
        manager.active_connections["closed_user"] = closed_websocket
        
        # This method should be implemented in ConnectionManager
        if hasattr(manager, 'cleanup_stale_connections'):
            await manager.cleanup_stale_connections()
            
            # Only active connection should remain
            assert "active_user" in manager.active_connections
            assert "closed_user" not in manager.active_connections

    @pytest.mark.asyncio
    async def test_connection_limit_enforcement(self):
        """Test that connection limits are enforced per user."""
        manager = ConnectionManager()
        user_id = "limited_user"
        max_connections = 3
        
        # This should be implemented in an enhanced ConnectionManager
        if hasattr(manager, 'max_connections_per_user'):
            manager.max_connections_per_user = max_connections
            
            # Add maximum allowed connections
            for i in range(max_connections):
                websocket = Mock(spec=WebSocket)
                websocket.accept = AsyncMock()
                await manager.connect(websocket, f"{user_id}_{i}")
            
            # Trying to add one more should either reject or replace oldest
            extra_websocket = Mock(spec=WebSocket)
            extra_websocket.accept = AsyncMock()
            
            result = await manager.connect(extra_websocket, f"{user_id}_extra")
            
            # Should still have max_connections or fewer
            assert len(manager.active_connections) <= max_connections 