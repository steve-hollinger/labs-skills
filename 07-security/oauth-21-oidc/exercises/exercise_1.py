"""Exercise 1: Implement State Parameter Validation

Your task: Implement a function to validate the OAuth state parameter
returned in the callback matches the state stored in the session.

Requirements:
1. Compare the returned state with the expected state
2. Return True if they match, False otherwise
3. Handle edge cases (None values, empty strings)
"""


def validate_state(expected_state: str | None, returned_state: str | None) -> bool:
    """Validate OAuth state parameter.

    Args:
        expected_state: State stored in session before authorization
        returned_state: State returned in callback URL

    Returns:
        True if states match, False otherwise

    TODO: Implement this function
    """
    # Your implementation here
    pass


# Test your implementation
if __name__ == "__main__":
    # Should pass
    assert validate_state("abc123", "abc123") == True

    # Should fail - different values
    assert validate_state("abc123", "xyz789") == False

    # Should fail - None values
    assert validate_state(None, "abc123") == False
    assert validate_state("abc123", None) == False

    # Should fail - empty strings
    assert validate_state("", "abc123") == False
    assert validate_state("abc123", "") == False

    print("All tests passed!")
