"""Solution 1: State Parameter Validation"""


def validate_state(expected_state: str | None, returned_state: str | None) -> bool:
    """Validate OAuth state parameter.

    Args:
        expected_state: State stored in session before authorization
        returned_state: State returned in callback URL

    Returns:
        True if states match, False otherwise
    """
    # Both must be non-None and non-empty
    if not expected_state or not returned_state:
        return False

    # Use constant-time comparison to prevent timing attacks
    # (though less critical for state than for tokens)
    return expected_state == returned_state


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
