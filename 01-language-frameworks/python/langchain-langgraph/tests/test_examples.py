"""Tests for LangChain and LangGraph examples."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage


class TestSimpleChain:
    """Tests for Example 1: Simple Chain."""

    def test_create_mock_chain(self):
        """Test that mock chain can be created and invoked."""
        from langchain_langgraph.examples.example_1_simple_chain import create_mock_chain

        chain = create_mock_chain()
        result = chain.invoke({"question": "What is Python?"})

        assert result is not None
        assert isinstance(result, str)
        assert "What is Python?" in result

    def test_create_simple_chain_without_api_key(self):
        """Test that simple chain falls back to mock without API key."""
        from langchain_langgraph.examples.example_1_simple_chain import create_simple_chain

        chain = create_simple_chain()
        result = chain.invoke({"question": "Test question"})

        assert result is not None
        assert isinstance(result, str)


class TestToolAgent:
    """Tests for Example 2: Tool-Using Agent."""

    def test_calculator_tool(self):
        """Test the calculator tool."""
        from langchain_langgraph.examples.example_2_tool_agent import calculator

        result = calculator.invoke({"expression": "2 + 2"})
        assert "4" in result

        result = calculator.invoke({"expression": "sqrt(16)"})
        assert "4" in result

    def test_calculator_tool_error_handling(self):
        """Test calculator handles invalid expressions."""
        from langchain_langgraph.examples.example_2_tool_agent import calculator

        result = calculator.invoke({"expression": "invalid_expression"})
        assert "Error" in result

    def test_get_current_time(self):
        """Test the time tool."""
        from langchain_langgraph.examples.example_2_tool_agent import get_current_time

        result = get_current_time.invoke({})
        assert "Current time" in result
        assert ":" in result  # Should have time format

    def test_get_weather(self):
        """Test the weather tool."""
        from langchain_langgraph.examples.example_2_tool_agent import get_weather

        result = get_weather.invoke({"city": "Tokyo", "unit": "celsius"})
        assert "Tokyo" in result
        assert "C" in result

        result = get_weather.invoke({"city": "New York", "unit": "fahrenheit"})
        assert "New York" in result
        assert "F" in result

    def test_get_weather_unknown_city(self):
        """Test weather tool with unknown city."""
        from langchain_langgraph.examples.example_2_tool_agent import get_weather

        result = get_weather.invoke({"city": "UnknownCity"})
        assert "not available" in result.lower()

    def test_search_knowledge_base(self):
        """Test the knowledge base search tool."""
        from langchain_langgraph.examples.example_2_tool_agent import search_knowledge_base

        result = search_knowledge_base.invoke({"query": "What is LangChain?"})
        assert "langchain" in result.lower()

    def test_create_mock_agent(self):
        """Test mock agent creation and invocation."""
        from langchain_langgraph.examples.example_2_tool_agent import create_tool_agent

        agent = create_tool_agent()
        result = agent.invoke({"messages": [("user", "What time is it?")]})

        assert "messages" in result
        assert len(result["messages"]) > 0


class TestLangGraphWorkflow:
    """Tests for Example 3: LangGraph Workflow."""

    def test_validate_document_valid(self, sample_documents):
        """Test document validation with valid input."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import validate_document

        state = {"document": sample_documents["technical"]}
        result = validate_document(state)

        assert result["is_valid"] is True
        assert result["word_count"] > 0
        assert "Validation passed" in result["processing_log"][0]

    def test_validate_document_too_short(self, sample_documents):
        """Test document validation with short input."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import validate_document

        state = {"document": sample_documents["short"]}
        result = validate_document(state)

        assert result["is_valid"] is False
        assert "Validation failed" in result["processing_log"][0]

    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis with positive text."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import analyze_sentiment

        state = {"document": "This is great and excellent! I love it!"}
        result = analyze_sentiment(state)

        assert result["sentiment"] == "positive"

    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis with negative text."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import analyze_sentiment

        state = {"document": "This is terrible and awful. I hate it."}
        result = analyze_sentiment(state)

        assert result["sentiment"] == "negative"

    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis with neutral text."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import analyze_sentiment

        state = {"document": "The document contains information about various topics."}
        result = analyze_sentiment(state)

        assert result["sentiment"] == "neutral"

    def test_extract_topics_technology(self, sample_documents):
        """Test topic extraction for technical content."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import extract_topics

        state = {"document": sample_documents["technical"]}
        result = extract_topics(state)

        assert "technology" in result["key_topics"]

    def test_extract_topics_business(self, sample_documents):
        """Test topic extraction for business content."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import extract_topics

        state = {"document": sample_documents["business"]}
        result = extract_topics(state)

        assert "business" in result["key_topics"]

    def test_create_workflow(self, sample_documents):
        """Test complete workflow execution."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import create_document_workflow

        workflow = create_document_workflow(use_llm=False)

        initial_state = {
            "document": sample_documents["technical"],
            "is_valid": False,
            "validation_message": "",
            "word_count": 0,
            "sentiment": "",
            "key_topics": [],
            "summary": "",
            "processing_log": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        assert result["is_valid"] is True
        assert result["sentiment"] in ["positive", "negative", "neutral"]
        assert len(result["key_topics"]) > 0
        assert result["summary"] != ""

    def test_workflow_with_invalid_document(self, sample_documents):
        """Test workflow handles invalid documents."""
        from langchain_langgraph.examples.example_3_langgraph_workflow import create_document_workflow

        workflow = create_document_workflow(use_llm=False)

        initial_state = {
            "document": sample_documents["short"],
            "is_valid": False,
            "validation_message": "",
            "word_count": 0,
            "sentiment": "",
            "key_topics": [],
            "summary": "",
            "processing_log": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        assert result["is_valid"] is False
        assert "Could not process" in result["summary"]


class TestMemoryAgent:
    """Tests for Example 4: Conversational Agent with Memory."""

    def test_extract_user_info_name(self):
        """Test user name extraction."""
        from langchain_langgraph.examples.example_4_memory_agent import extract_user_info

        messages = [HumanMessage(content="My name is Alice")]
        info = extract_user_info(messages)

        assert info["name"] == "Alice"

    def test_extract_user_info_preferences(self):
        """Test user preference extraction."""
        from langchain_langgraph.examples.example_4_memory_agent import extract_user_info

        messages = [HumanMessage(content="I like programming")]
        info = extract_user_info(messages)

        assert "likes" in info["preferences"]
        assert "programming" in info["preferences"]["likes"]

    def test_extract_user_info_multiple(self):
        """Test extraction of multiple pieces of info."""
        from langchain_langgraph.examples.example_4_memory_agent import extract_user_info

        messages = [
            HumanMessage(content="My name is Bob"),
            HumanMessage(content="I prefer Python over JavaScript"),
        ]
        info = extract_user_info(messages)

        assert info["name"] == "Bob"
        assert "prefers" in info["preferences"]

    def test_create_memory_agent(self):
        """Test memory agent creation."""
        from langchain_langgraph.examples.example_4_memory_agent import create_memory_agent

        agent = create_memory_agent()
        assert agent is not None

    def test_memory_agent_conversation(self):
        """Test memory agent maintains state across turns."""
        from langchain_langgraph.examples.example_4_memory_agent import create_memory_agent, chat

        agent = create_memory_agent()
        thread_id = "test-thread"

        # First message
        response1 = chat(agent, "My name is Test User", thread_id)
        assert response1 is not None

        # Second message - should remember
        response2 = chat(agent, "What is my name?", thread_id)
        # The mock should recall the name
        assert "Test" in response2 or "name" in response2.lower()

    def test_memory_agent_separate_threads(self):
        """Test that separate threads have separate state."""
        from langchain_langgraph.examples.example_4_memory_agent import create_memory_agent, chat

        agent = create_memory_agent()

        # Thread 1
        chat(agent, "My name is Alice", "thread-1")

        # Thread 2 - different conversation
        chat(agent, "My name is Bob", "thread-2")

        # Check thread 1 state
        config1 = {"configurable": {"thread_id": "thread-1"}}
        state1 = agent.get_state(config1)

        # Check thread 2 state
        config2 = {"configurable": {"thread_id": "thread-2"}}
        state2 = agent.get_state(config2)

        # States should be different
        assert state1.values.get("user_name") != state2.values.get("user_name")


class TestSolutionIntegration:
    """Integration tests for exercise solutions."""

    def test_solution_1_summarization(self):
        """Test summarization solution."""
        from langchain_langgraph.exercises.solutions.solution_1_summarization_chain import (
            summarize_text
        )

        text = """
        Machine learning is a subset of artificial intelligence that enables systems
        to learn and improve from experience without being explicitly programmed.
        It focuses on developing computer programs that can access data and use it
        to learn for themselves. The process involves looking for patterns in data.
        Machine learning algorithms are categorized as supervised or unsupervised.
        """ * 2  # Make it long enough

        result = summarize_text(text)

        assert result is not None
        assert "main_topic" in result
        assert "bullet_points" in result
        assert len(result["bullet_points"]) == 3
        assert "word_count" in result

    def test_solution_1_short_text_rejection(self):
        """Test that short text is rejected."""
        from langchain_langgraph.exercises.solutions.solution_1_summarization_chain import (
            summarize_text
        )

        result = summarize_text("Too short")
        assert result is None

    def test_solution_2_tools(self):
        """Test customer support tools."""
        from langchain_langgraph.exercises.solutions.solution_2_custom_tool_agent import (
            lookup_order_status,
            check_product_availability,
            get_return_policy,
        )

        # Test order lookup
        result = lookup_order_status.invoke({"order_id": "12345"})
        assert "shipped" in result.lower()
        assert "12345" in result

        # Test product availability
        result = check_product_availability.invoke({"product_name": "wireless mouse"})
        assert "stock" in result.lower()

        # Test return policy
        result = get_return_policy.invoke({})
        assert "30 days" in result

    def test_solution_3_pipeline(self, sample_documents):
        """Test document pipeline solution."""
        from langchain_langgraph.exercises.solutions.solution_3_document_pipeline import (
            process_document
        )

        result = process_document(sample_documents["technical"])

        assert "final_report" in result
        assert "PASSED" in result["final_report"]
        assert "TECHNICAL" in result["final_report"]

    def test_solution_3_pipeline_invalid(self, sample_documents):
        """Test pipeline with invalid document."""
        from langchain_langgraph.exercises.solutions.solution_3_document_pipeline import (
            process_document
        )

        result = process_document(sample_documents["short"])

        assert "final_report" in result
        assert "FAILED" in result["final_report"]
