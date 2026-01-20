"""Solution 1: Credit Card Number Masker.

This solution demonstrates credit card masking with:
- Luhn algorithm validation
- Card type detection
- Format-preserving masking
- Pattern-based detection in text
"""

from __future__ import annotations

import re
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

    The Luhn algorithm:
    1. From the rightmost digit, double every second digit
    2. If doubling results in > 9, subtract 9
    3. Sum all digits
    4. Valid if sum % 10 == 0
    """
    # Remove any non-digit characters
    digits = [int(d) for d in card_number if d.isdigit()]

    if len(digits) < 13:
        return False

    # Reverse for processing
    digits = digits[::-1]

    total = 0
    for i, digit in enumerate(digits):
        if i % 2 == 1:  # Every second digit (0-indexed, so odd positions)
            doubled = digit * 2
            if doubled > 9:
                doubled -= 9
            total += doubled
        else:
            total += digit

    return total % 10 == 0


def identify_card_type(card_number: str) -> CardType:
    """Identify the card type from the number.

    Card type rules:
    - Visa: starts with 4, 13 or 16 digits
    - Mastercard: starts with 51-55 or 2221-2720, 16 digits
    - Amex: starts with 34 or 37, 15 digits
    - Discover: starts with 6011, 622126-622925, 644-649, 65, 16 digits
    """
    digits = "".join(c for c in card_number if c.isdigit())
    length = len(digits)

    if not digits:
        return CardType.UNKNOWN

    # Visa: starts with 4
    if digits[0] == "4" and length in (13, 16):
        return CardType.VISA

    # Mastercard: starts with 51-55 or 2221-2720
    if length == 16:
        first_two = int(digits[:2])
        first_four = int(digits[:4])

        if 51 <= first_two <= 55:
            return CardType.MASTERCARD
        if 2221 <= first_four <= 2720:
            return CardType.MASTERCARD

    # Amex: starts with 34 or 37
    if length == 15 and digits[:2] in ("34", "37"):
        return CardType.AMEX

    # Discover: starts with 6011, 65, 644-649
    if length == 16:
        if digits[:4] == "6011":
            return CardType.DISCOVER
        if digits[:2] == "65":
            return CardType.DISCOVER
        first_three = int(digits[:3])
        if 644 <= first_three <= 649:
            return CardType.DISCOVER

    return CardType.UNKNOWN


class CreditCardMasker:
    """Masks credit card numbers while preserving format."""

    # Pattern to detect credit card numbers
    CARD_PATTERN = re.compile(
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b"  # 16 digits with optional separators
        r"|\b\d{15}\b"  # 15 digits (Amex)
        r"|\b\d{13}\b"  # 13 digits (old Visa)
    )

    def __init__(self, mask_char: str = "*"):
        """Initialize the masker.

        Args:
            mask_char: Character to use for masking
        """
        self.mask_char = mask_char

    def _extract_digits(self, card_number: str) -> str:
        """Extract only digits from a card number."""
        return "".join(c for c in card_number if c.isdigit())

    def mask(self, card_number: str) -> str:
        """Mask a credit card number, preserving format.

        Args:
            card_number: The card number (may include dashes/spaces)

        Returns:
            Masked card number with format preserved
        """
        digits = self._extract_digits(card_number)

        if len(digits) < 4:
            return self.mask_char * len(card_number)

        last_four = digits[-4:]
        digits_to_mask = len(digits) - 4

        # Build masked version preserving format
        result = []
        digit_count = 0

        for char in card_number:
            if char.isdigit():
                if digit_count < digits_to_mask:
                    result.append(self.mask_char)
                else:
                    result.append(char)
                digit_count += 1
            else:
                result.append(char)

        return "".join(result)

    def get_card_info(self, card_number: str) -> CardInfo:
        """Get information about a credit card.

        Args:
            card_number: The card number

        Returns:
            CardInfo with type, validity, and masked number
        """
        digits = self._extract_digits(card_number)
        card_type = identify_card_type(digits)
        valid = luhn_checksum(digits)
        masked = self.mask(card_number)
        last_four = digits[-4:] if len(digits) >= 4 else digits

        return CardInfo(
            card_type=card_type,
            valid=valid,
            masked=masked,
            last_four=last_four,
        )

    def detect_and_mask(self, text: str) -> str:
        """Detect and mask credit card numbers in text.

        Args:
            text: Text that may contain credit card numbers

        Returns:
            Text with card numbers masked
        """
        def replace_match(match: re.Match) -> str:
            card = match.group()
            # Only mask if it passes Luhn check (likely a real card number)
            digits = self._extract_digits(card)
            if luhn_checksum(digits):
                return self.mask(card)
            return card

        return self.CARD_PATTERN.sub(replace_match, text)


def main() -> None:
    """Demonstrate the credit card masker."""
    print("=" * 60)
    print("Solution 1: Credit Card Masker")
    print("=" * 60)

    masker = CreditCardMasker()

    # Test cards (these are standard test numbers)
    test_cards = [
        ("4111-1111-1111-1111", "Visa"),
        ("4111 1111 1111 1111", "Visa with spaces"),
        ("4111111111111111", "Visa no separators"),
        ("5500-0000-0000-0004", "Mastercard"),
        ("378282246310005", "American Express"),
        ("6011-1111-1111-1117", "Discover"),
        ("4222222222222", "Visa 13-digit"),
    ]

    print("\n1. Masking Tests")
    print("-" * 40)
    for card, description in test_cards:
        masked = masker.mask(card)
        print(f"{description}:")
        print(f"  Original: {card}")
        print(f"  Masked:   {masked}")
        print()

    # Test card info
    print("2. Card Info Tests")
    print("-" * 40)
    for card, description in test_cards:
        info = masker.get_card_info(card)
        print(f"{description}:")
        print(f"  Type: {info.card_type.value}")
        print(f"  Valid (Luhn): {info.valid}")
        print(f"  Last 4: {info.last_four}")
        print()

    # Test Luhn validation
    print("3. Luhn Validation")
    print("-" * 40)
    valid_numbers = ["4111111111111111", "5500000000000004", "378282246310005"]
    invalid_numbers = ["4111111111111112", "1234567890123456"]

    for num in valid_numbers:
        print(f"{num}: {'Valid' if luhn_checksum(num) else 'Invalid'}")

    for num in invalid_numbers:
        print(f"{num}: {'Valid' if luhn_checksum(num) else 'Invalid'}")

    # Test text detection
    print("\n4. Text Detection")
    print("-" * 40)
    test_text = """
    Customer payment info:
    Primary card: 4111-1111-1111-1111
    Backup card: 5500 0000 0000 0004
    Old card: 4222222222222
    Invalid number: 1234-5678-9012-3456
    """

    print("Original text:")
    print(test_text)
    print("\nMasked text:")
    print(masker.detect_and_mask(test_text))

    print("=" * 60)
    print("Solution 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
