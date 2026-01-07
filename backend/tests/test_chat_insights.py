"""
Comprehensive test suite for Chat Data Insights feature.

This module tests the chat engine's ability to:
- Detect intents for various query formats
- Retrieve accurate data from the database
- Format responses correctly in markdown
- Handle edge cases gracefully
- Fall back to general chat when appropriate
"""
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from unittest.mock import AsyncMock, MagicMock, patch

from backend.services.chat_engine import ChatEngine
from backend.services.chat_handlers import TopHCOsHandler, GeneralChatHandler
from backend.services.hco_service import HCOService


# Test fixtures
@pytest_asyncio.fixture
async def mock_db():
    """Create a mock database for testing."""
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    return mock_db


@pytest_asyncio.fixture
async def sample_hco_data():
    """Sample HCO data for testing."""
    return [
        {
            "_id": "507f1f77bcf86cd799439011",
            "name": "Memorial Hospital",
            "state": "CA",
            "region": "West",
            "ghost_patients": 1250,
            "treated_patients": 3750,
            "leakage_rate": 25.0
        },
        {
            "_id": "507f1f77bcf86cd799439012",
            "name": "City Medical Center",
            "state": "NY",
            "region": "Northeast",
            "ghost_patients": 980,
            "treated_patients": 4020,
            "leakage_rate": 19.6
        },
        {
            "_id": "507f1f77bcf86cd799439013",
            "name": "Regional Health System",
            "state": "TX",
            "region": "South",
            "ghost_patients": 875,
            "treated_patients": 4125,
            "leakage_rate": 17.5
        },
        {
            "_id": "507f1f77bcf86cd799439014",
            "name": "University Hospital",
            "state": "MA",
            "region": "Northeast",
            "ghost_patients": 720,
            "treated_patients": 3280,
            "leakage_rate": 18.0
        },
        {
            "_id": "507f1f77bcf86cd799439015",
            "name": "Community Care Center",
            "state": "FL",
            "region": "South",
            "ghost_patients": 650,
            "treated_patients": 3350,
            "leakage_rate": 16.25
        }
    ]


# Intent Detection Tests
class TestIntentDetection:
    """Test intent detection for various query formats."""
    
    def test_top_5_hcos_standard_query(self):
        """Test standard 'top 5 HCOs' query detection."""
        message = "show me top 5 HCOs with highest ghost patients"
        params = TopHCOsHandler.matches(message)
        
        assert params is not None
        assert params["limit"] == 5
    
    def test_top_10_hcos_query(self):
        """Test 'top 10 HCOs' query detection."""
        message = "top 10 hcos ghost patients"
        params = TopHCOsHandler.matches(message)
        
        assert params is not None
        assert params["limit"] == 10
    
    def test_top_hcos_default_limit(self):
        """Test 'top HCOs' query defaults to 5."""
        message = "top hcos by ghost patients"
        params = TopHCOsHandler.matches(message)
        
        assert params is not None
        assert params["limit"] == 5
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        messages = [
            "TOP 5 HCOS GHOST PATIENTS",
            "Top 5 HCOs Ghost Patients",
            "top 5 hcos ghost patients"
        ]
        
        for message in messages:
            params = TopHCOsHandler.matches(message)
            assert params is not None
            assert params["limit"] == 5
    
    def test_limit_capping(self):
        """Test that limit is capped at 20."""
        message = "top 100 hcos ghost patients"
        params = TopHCOsHandler.matches(message)
        
        assert params is not None
        assert params["limit"] == 20  # Should be capped
    
    def test_various_query_formats(self):
        """Test various valid query formats."""
        test_cases = [
            ("show me top 3 HCOs with highest ghost patients", 3),
            ("top 7 hco ghost patients", 7),
            ("give me top 15 hcos by ghost patients", 15),
            ("top hcos ghost", 5),  # Default
        ]
        
        for message, expected_limit in test_cases:
            params = TopHCOsHandler.matches(message)
            assert params is not None, f"Failed to match: {message}"
            assert params["limit"] == expected_limit
    
    def test_non_matching_queries(self):
        """Test that non-matching queries return None."""
        non_matching = [
            "hello",
            "help me",
            "what is a ghost patient",
            "show me contracts",
            "dashboard features"
        ]
        
        for message in non_matching:
            params = TopHCOsHandler.matches(message)
            assert params is None, f"Should not match: {message}"


# Data Retrieval Tests
class TestDataRetrieval:
    """Test data retrieval accuracy."""
    
    @pytest.mark.asyncio
    async def test_top_5_hcos_retrieval(self, mock_db, sample_hco_data):
        """Test retrieving top 5 HCOs."""
        # Mock the database query
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients', 
                         return_value=sample_hco_data[:5]) as mock_get:
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 5})
            
            # Verify the service was called correctly
            mock_get.assert_called_once_with(mock_db, limit=5)
            
            # Verify response contains expected data
            assert "Memorial Hospital" in response
            assert "1250 ghost patients" in response
            assert "25.0% leakage rate" in response
    
    @pytest.mark.asyncio
    async def test_top_3_hcos_retrieval(self, mock_db, sample_hco_data):
        """Test retrieving top 3 HCOs."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:3]) as mock_get:
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 3})
            
            mock_get.assert_called_once_with(mock_db, limit=3)
            
            # Should contain first 3 HCOs
            assert "Memorial Hospital" in response
            assert "City Medical Center" in response
            assert "Regional Health System" in response
            
            # Should NOT contain 4th and 5th
            assert "University Hospital" not in response
            assert "Community Care Center" not in response
    
    @pytest.mark.asyncio
    async def test_empty_database(self, mock_db):
        """Test handling of empty database."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=[]):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 5})
            
            assert response == "No HCO data found."
    
    @pytest.mark.asyncio
    async def test_less_than_requested_hcos(self, mock_db, sample_hco_data):
        """Test when database has fewer HCOs than requested."""
        # Only 2 HCOs available, but requesting 5
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:2]):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 5})
            
            # Should return what's available
            assert "top 2 HCOs" in response
            assert "Memorial Hospital" in response
            assert "City Medical Center" in response


# Response Formatting Tests
class TestResponseFormatting:
    """Test response formatting and markdown structure."""
    
    @pytest.mark.asyncio
    async def test_markdown_structure(self, mock_db, sample_hco_data):
        """Test that response uses proper markdown formatting."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 5})
            
            # Check for markdown bold formatting
            assert "**Memorial Hospital**" in response
            assert "**City Medical Center**" in response
            
            # Check for numbered list
            assert "1. **" in response
            assert "2. **" in response
            assert "3. **" in response
            assert "4. **" in response
            assert "5. **" in response
    
    @pytest.mark.asyncio
    async def test_response_includes_all_fields(self, mock_db, sample_hco_data):
        """Test that response includes all required fields."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:1]):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 1})
            
            # Should include: name, state, ghost patients count, leakage rate
            assert "Memorial Hospital" in response
            assert "(CA)" in response
            assert "1250 ghost patients" in response
            assert "25.0% leakage rate" in response
    
    @pytest.mark.asyncio
    async def test_response_header(self, mock_db, sample_hco_data):
        """Test that response has appropriate header."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:3]):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 3})
            
            assert "Here are the top 3 HCOs" in response


# General Chat Tests
class TestGeneralChat:
    """Test general chat fallback functionality."""
    
    @pytest.mark.asyncio
    async def test_hello_greeting(self, mock_db):
        """Test greeting response."""
        handler = GeneralChatHandler(mock_db)
        response = await handler.handle({"message": "hello"})
        
        assert "Hello" in response
    
    @pytest.mark.asyncio
    async def test_help_request(self, mock_db):
        """Test help response."""
        handler = GeneralChatHandler(mock_db)
        response = await handler.handle({"message": "help"})
        
        assert "help" in response.lower()
        assert "HCOs" in response
    
    @pytest.mark.asyncio
    async def test_dashboard_query(self, mock_db):
        """Test dashboard-related query."""
        handler = GeneralChatHandler(mock_db)
        response = await handler.handle({"message": "tell me about the dashboard"})
        
        assert "dashboard" in response.lower()
        assert "analytics" in response.lower()
    
    @pytest.mark.asyncio
    async def test_thank_you_response(self, mock_db):
        """Test thank you response."""
        handler = GeneralChatHandler(mock_db)
        response = await handler.handle({"message": "thank you"})
        
        assert "welcome" in response.lower()
    
    @pytest.mark.asyncio
    async def test_default_fallback(self, mock_db):
        """Test default fallback response."""
        handler = GeneralChatHandler(mock_db)
        response = await handler.handle({"message": "random unrecognized query"})
        
        assert "understand" in response.lower()
        assert "HCOs" in response  # Should mention data insights capability


# Chat Engine Integration Tests
class TestChatEngineIntegration:
    """Test the full chat engine integration."""
    
    @pytest.mark.asyncio
    async def test_data_query_routing(self, mock_db, sample_hco_data):
        """Test that data queries are routed to correct handler."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            engine = ChatEngine(mock_db)
            response = await engine.process_message("show me top 5 HCOs with highest ghost patients")
            
            # Should be a data response, not general chat
            assert "Memorial Hospital" in response
            assert "ghost patients" in response
    
    @pytest.mark.asyncio
    async def test_general_chat_routing(self, mock_db):
        """Test that general queries are routed to general handler."""
        engine = ChatEngine(mock_db)
        response = await engine.process_message("hello")
        
        # Should be a greeting, not data
        assert "Hello" in response
        assert "Memorial Hospital" not in response
    
    @pytest.mark.asyncio
    async def test_handler_priority(self, mock_db, sample_hco_data):
        """Test that handlers are checked in priority order."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            engine = ChatEngine(mock_db)
            
            # This should match TopHCOsHandler, not general chat
            response = await engine.process_message("top 5 hcos ghost patients")
            
            assert "Memorial Hospital" in response
            assert "Hello" not in response


# Edge Case Tests
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_message_handling(self, mock_db):
        """Test handling of empty or whitespace-only messages."""
        engine = ChatEngine(mock_db)
        
        # Empty string should still get a response
        response = await engine.process_message("")
        assert response is not None
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_very_long_message(self, mock_db, sample_hco_data):
        """Test handling of very long messages."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            engine = ChatEngine(mock_db)
            long_message = "show me " + "top " * 100 + "hcos ghost patients"
            
            response = await engine.process_message(long_message)
            assert response is not None
    
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self, mock_db, sample_hco_data):
        """Test handling of special characters."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            engine = ChatEngine(mock_db)
            response = await engine.process_message("top 5 HCOs!!! ghost patients???")
            
            # Should still work despite special characters
            assert "Memorial Hospital" in response
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, mock_db):
        """Test handling of database errors."""
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         side_effect=Exception("Database connection error")):
            
            handler = TopHCOsHandler(mock_db)
            
            # Should raise the exception (to be caught by router)
            with pytest.raises(Exception):
                await handler.handle({"limit": 5})
    
    @pytest.mark.asyncio
    async def test_missing_hco_fields(self, mock_db):
        """Test handling of HCOs with missing fields."""
        incomplete_hco = [{
            "_id": "507f1f77bcf86cd799439011",
            "name": "Test Hospital",
            # Missing state, ghost_patients, etc.
        }]
        
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=incomplete_hco):
            
            handler = TopHCOsHandler(mock_db)
            response = await handler.handle({"limit": 1})
            
            # Should handle gracefully with defaults
            assert "Test Hospital" in response
            assert "Unknown" in response or "??" in response


# Performance Tests
class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_response_time_data_query(self, mock_db, sample_hco_data):
        """Test that data queries respond quickly."""
        import time
        
        with patch.object(HCOService, 'get_top_hcos_by_ghost_patients',
                         return_value=sample_hco_data[:5]):
            
            engine = ChatEngine(mock_db)
            
            start_time = time.time()
            response = await engine.process_message("top 5 hcos ghost patients")
            end_time = time.time()
            
            # Should respond in less than 1 second (mocked, so should be very fast)
            assert (end_time - start_time) < 1.0
            assert response is not None
    
    @pytest.mark.asyncio
    async def test_response_time_general_chat(self, mock_db):
        """Test that general chat responds quickly."""
        import time
        
        engine = ChatEngine(mock_db)
        
        start_time = time.time()
        response = await engine.process_message("hello")
        end_time = time.time()
        
        # Should respond very quickly
        assert (end_time - start_time) < 0.1
        assert response is not None


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])