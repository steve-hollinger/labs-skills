"""Tests for OpenAI Responses API examples."""

import pytest


class TestChatCompletion:
    """Tests for Example 1: Chat Completion."""

    def test_mock_client_creation(self):
        """Test mock client can be created."""
        from openai_responses_api.examples.example_1_chat_completion import get_client

        client = get_client()
        assert client is not None

    def test_mock_completion(self):
        """Test mock completion returns expected structure."""
        from openai_responses_api.examples.example_1_chat_completion import get_client

        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Hello"}
            ]
        )

        assert hasattr(response, 'choices')
        assert len(response.choices) > 0
        assert hasattr(response.choices[0].message, 'content')
        assert hasattr(response, 'usage')


class TestFunctionCalling:
    """Tests for Example 2: Function Calling."""

    def test_calculator_tool(self):
        """Test calculator function."""
        from openai_responses_api.examples.example_2_function_calling import calculate

        result = calculate("2 + 2")
        assert result["result"] == 4

        result = calculate("sqrt(16)")
        assert result["result"] == 4.0

    def test_calculator_error_handling(self):
        """Test calculator handles errors."""
        from openai_responses_api.examples.example_2_function_calling import calculate

        result = calculate("invalid")
        assert "error" in result

    def test_weather_tool(self):
        """Test weather function."""
        from openai_responses_api.examples.example_2_function_calling import get_weather

        result = get_weather("Tokyo", "celsius")
        assert result["location"] == "Tokyo"
        assert result["unit"] == "celsius"
        assert "temperature" in result

    def test_weather_fahrenheit(self):
        """Test weather with fahrenheit."""
        from openai_responses_api.examples.example_2_function_calling import get_weather

        result = get_weather("Tokyo", "fahrenheit")
        assert result["unit"] == "fahrenheit"
        # Tokyo is 22C, should be ~71.6F
        assert result["temperature"] > 70

    def test_time_tool(self):
        """Test time function."""
        from openai_responses_api.examples.example_2_function_calling import get_current_time

        result = get_current_time()
        assert "datetime" in result
        assert "formatted" in result

    def test_search_products(self):
        """Test product search."""
        from openai_responses_api.examples.example_2_function_calling import search_products

        result = search_products("laptop")
        assert "results" in result
        assert len(result["results"]) > 0

    def test_search_products_with_category(self):
        """Test product search with category filter."""
        from openai_responses_api.examples.example_2_function_calling import search_products

        result = search_products("", category="electronics")
        for product in result["results"]:
            assert product["category"] == "electronics"


class TestStructuredOutputs:
    """Tests for Example 3: Structured Outputs."""

    def test_sentiment_analysis_mock(self):
        """Test sentiment analysis returns correct structure."""
        from openai_responses_api.examples.example_3_structured_outputs import (
            analyze_sentiment, Sentiment
        )

        result = analyze_sentiment("I love this product!")
        assert hasattr(result, 'sentiment')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'reasoning')
        assert 0 <= result.confidence <= 1

    def test_text_analysis_mock(self):
        """Test complete text analysis."""
        from openai_responses_api.examples.example_3_structured_outputs import (
            analyze_text_complete
        )

        text = "Apple announced new products in California."
        result = analyze_text_complete(text)

        assert hasattr(result, 'summary')
        assert hasattr(result, 'sentiment')
        assert hasattr(result, 'entities')
        assert hasattr(result, 'keywords')
        assert result.word_count > 0

    def test_product_extraction_mock(self):
        """Test product info extraction."""
        from openai_responses_api.examples.example_3_structured_outputs import (
            extract_product_info
        )

        description = "Laptop Pro for $999"
        result = extract_product_info(description)

        assert hasattr(result, 'name')
        assert hasattr(result, 'category')

    def test_contact_extraction_mock(self):
        """Test contact extraction."""
        from openai_responses_api.examples.example_3_structured_outputs import (
            extract_contacts
        )

        text = "Contact John at john@example.com"
        results = extract_contacts(text)

        assert isinstance(results, list)
        assert len(results) > 0


class TestProductionPatterns:
    """Tests for Example 4: Production Patterns."""

    def test_error_handler(self):
        """Test error handler returns correct structure."""
        from openai_responses_api.examples.example_4_production_patterns import (
            APIErrorHandler
        )

        handler = APIErrorHandler()
        result = handler.safe_completion([
            {"role": "user", "content": "Hello"}
        ])

        assert "success" in result
        assert result["success"] is True
        assert "content" in result

    def test_retrying_client(self):
        """Test retrying client works."""
        from openai_responses_api.examples.example_4_production_patterns import (
            RetryingClient
        )

        client = RetryingClient()
        result = client.completion_with_retry([
            {"role": "user", "content": "Hello"}
        ])

        assert result is not None
        assert isinstance(result, str)

    def test_rate_limited_client(self):
        """Test rate limited client."""
        from openai_responses_api.examples.example_4_production_patterns import (
            RateLimitedClient
        )

        client = RateLimitedClient(requests_per_minute=60)
        result = client.completion([
            {"role": "user", "content": "Hello"}
        ])

        assert result is not None

    def test_cost_tracking_client(self):
        """Test cost tracking."""
        from openai_responses_api.examples.example_4_production_patterns import (
            CostTrackingClient
        )

        client = CostTrackingClient()
        client.completion([{"role": "user", "content": "Hello"}])
        client.completion([{"role": "user", "content": "World"}])

        summary = client.get_summary()
        assert summary["total_requests"] == 2

    def test_streaming_client(self):
        """Test streaming client."""
        from openai_responses_api.examples.example_4_production_patterns import (
            StreamingClient
        )

        client = StreamingClient()
        tokens = list(client.stream_completion([
            {"role": "user", "content": "Hello"}
        ]))

        assert len(tokens) > 0

    def test_caching_client(self):
        """Test caching client."""
        from openai_responses_api.examples.example_4_production_patterns import (
            CachingClient
        )

        client = CachingClient()

        # First call - cache miss
        result1 = client.completion([
            {"role": "user", "content": "Test"}
        ], temperature=0)

        # Same call - cache hit
        result2 = client.completion([
            {"role": "user", "content": "Test"}
        ], temperature=0)

        stats = client.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1
        assert result1 == result2


class TestSolutions:
    """Tests for exercise solutions."""

    def test_solution_1_chatbot(self):
        """Test chatbot solution."""
        from openai_responses_api.exercises.solutions.solution_1_chatbot import Chatbot

        bot = Chatbot(system_prompt="You are a test bot.")

        # Test chat
        response = bot.chat("Hello")
        assert response is not None
        assert isinstance(response, str)

        # Test history
        history = bot.get_history()
        assert len(history) == 3  # system + user + assistant

        # Test clear
        bot.clear_history()
        assert len(bot.get_history()) == 1

    def test_solution_2_task_agent(self):
        """Test task agent solution."""
        from openai_responses_api.exercises.solutions.solution_2_tool_agent import (
            create_task, list_tasks, update_task_status, TASKS
        )

        # Clear tasks
        TASKS.clear()

        # Test create
        result = create_task("Test Task", priority="high")
        assert result["success"] is True
        assert result["task"]["title"] == "Test Task"

        task_id = result["task"]["id"]

        # Test list
        result = list_tasks()
        assert result["count"] == 1

        # Test update
        result = update_task_status(task_id, "completed")
        assert result["success"] is True
        assert result["task"]["status"] == "completed"

    def test_solution_3_extractor(self):
        """Test data extractor solution."""
        from openai_responses_api.exercises.solutions.solution_3_data_extractor import (
            DataExtractor, JobType, ExperienceLevel
        )

        extractor = DataExtractor()

        text = """
        Senior Software Engineer at TechCorp
        Location: San Francisco, CA (Remote)
        Salary: $180,000 - $220,000
        Requirements: Python, AWS
        Full-time position
        """

        result = extractor.extract_job_posting(text)

        assert result.title is not None
        assert result.company is not None
        assert result.job_type == JobType.full_time
        assert result.location.is_remote is True
