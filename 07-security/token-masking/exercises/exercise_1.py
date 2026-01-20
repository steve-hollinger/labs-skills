"""Exercise 1: Credit Card Number Masker.

Create a credit card masker that:
1. Validates credit card numbers using the Luhn algorithm
2. Masks all but the last 4 digits
3. Preserves the card format (with dashes or spaces)
4. Identifies card type (Visa, Mastercard, Amex)

Expected usage:
    masker = CreditCardMasker()
    masked = masker.mask("4111-1111-1111-1111")
    # Returns: "****-****-****-1111"

    info = masker.get_card_info("4111111111111111")
    # Returns: CardInfo(type="Visa", valid=True, masked="************1111")

Hints:
- Luhn algorithm: double every second digit from right, sum all
- Visa starts with 4, Mastercard 51-55, Amex 34/37
- Handle both formatted and unformatted numbers
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CardType(Enum):
    """Credit card types."""
    VISA = "Visa"
    MASTERCARD = "Mastercard"
    AMEX = "American Express"
    DISCOVER = "Discover"
    UNKNOWN = "Unknown"


@dataclass
class CardInfo:
    """Information about a credit card."""
    card_type: CardType
    valid: bool
    masked: str
    last_four: str


def luhn_checksum(card_number: str) -> bool:
    """Validate a credit card number using the Luhn algorithm.

    Args:
        card_number: The card number (digits only)

    Returns:
        True if valid according to Luhn

    TODO: Implement the Luhn algorithm
    1. Starting from the right, double every second digit
    2. If doubling results in > 9, subtract 9
    3. Sum all digits
    4. Valid if sum % 10 == 0
    """
    # TODO: Implement this function
    raise NotImplementedError("Implement luhn_checksum")


def identify_card_type(card_number: str) -> CardType:
    """Identify the card type from the number.

    Args:
        card_number: The card number (digits only)

    Returns:
        The identified CardType

    TODO: Implement card type detection
    - Visa: starts with 4, 13 or 16 digits
    - Mastercard: starts with 51-55, 16 digits
    - Amex: starts with 34 or 37, 15 digits
    - Discover: starts with 6011, 16 digits
    """
    # TODO: Implement this function
    raise NotImplementedError("Implement identify_card_type")


class CreditCardMasker:
    """Masks credit card numbers while preserving format.

    TODO: Implement this class with:
    - mask(card_number: str) -> str
    - get_card_info(card_number: str) -> CardInfo
    - detect_and_mask(text: str) -> str
    """

    def __init__(self, mask_char: str = "*"):
        """Initialize the masker.

        Args:
            mask_char: Character to use for masking
        """
        # TODO: Store configuration
        pass

    def _extract_digits(self, card_number: str) -> str:
        """Extract only digits from a card number.

        Args:
            card_number: The formatted card number

        Returns:
            Digits only
        """
        # TODO: Implement digit extraction
        raise NotImplementedError("Implement _extract_digits")

    def mask(self, card_number: str) -> str:
        """Mask a credit card number, preserving format.

        Args:
            card_number: The card number (may include dashes/spaces)

        Returns:
            Masked card number with format preserved

        Example:
            mask("4111-1111-1111-1111") -> "****-****-****-1111"
            mask("4111 1111 1111 1111") -> "**** **** **** 1111"
            mask("4111111111111111") -> "************1111"
        """
        # TODO: Implement masking with format preservation
        raise NotImplementedError("Implement mask")

    def get_card_info(self, card_number: str) -> CardInfo:
        """Get information about a credit card.

        Args:
            card_number: The card number

        Returns:
            CardInfo with type, validity, and masked number
        """
        # TODO: Implement card info extraction
        raise NotImplementedError("Implement get_card_info")

    def detect_and_mask(self, text: str) -> str:
        """Detect and mask credit card numbers in text.

        Args:
            text: Text that may contain credit card numbers

        Returns:
            Text with card numbers masked
        """
        # TODO: Implement detection and masking
        # Hint: Use regex to find potential card numbers
        raise NotImplementedError("Implement detect_and_mask")


def main() -> None:
    """Test your implementation."""
    print("Exercise 1: Credit Card Masker")
    print("See the solution in solutions/solution_1.py")

    # Uncomment to test your implementation:
    #
    # masker = CreditCardMasker()
    #
    # # Test masking
    # print("\nMasking tests:")
    # print(masker.mask("4111-1111-1111-1111"))  # ****-****-****-1111
    # print(masker.mask("5500 0000 0000 0004"))  # **** **** **** 0004
    # print(masker.mask("378282246310005"))      # ***********0005
    #
    # # Test card info
    # print("\nCard info tests:")
    # info = masker.get_card_info("4111111111111111")
    # print(f"Type: {info.card_type.value}, Valid: {info.valid}")
    #
    # # Test detection
    # print("\nDetection tests:")
    # text = "Card: 4111-1111-1111-1111, backup: 5500000000000004"
    # print(masker.detect_and_mask(text))


if __name__ == "__main__":
    main()
