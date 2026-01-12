"""Tests for the calculator service.

TDD: These tests are written BEFORE the implementation.
"""

import pytest

from app.services.calculator import add, divide, multiply, subtract


class TestAdd:
    """Tests for the add function."""

    def test_add_positive_numbers(self) -> None:
        """Test adding two positive numbers."""
        assert add(2, 3) == 5

    def test_add_negative_numbers(self) -> None:
        """Test adding two negative numbers."""
        assert add(-2, -3) == -5

    def test_add_mixed_numbers(self) -> None:
        """Test adding positive and negative numbers."""
        assert add(-2, 5) == 3

    def test_add_zero(self) -> None:
        """Test adding with zero."""
        assert add(0, 5) == 5
        assert add(5, 0) == 5

    def test_add_floats(self) -> None:
        """Test adding floating point numbers."""
        assert add(2.5, 3.5) == 6.0


class TestSubtract:
    """Tests for the subtract function."""

    def test_subtract_positive_numbers(self) -> None:
        """Test subtracting two positive numbers."""
        assert subtract(5, 3) == 2

    def test_subtract_negative_numbers(self) -> None:
        """Test subtracting two negative numbers."""
        assert subtract(-5, -3) == -2

    def test_subtract_mixed_numbers(self) -> None:
        """Test subtracting positive and negative numbers."""
        assert subtract(-2, 5) == -7

    def test_subtract_zero(self) -> None:
        """Test subtracting with zero."""
        assert subtract(5, 0) == 5
        assert subtract(0, 5) == -5

    def test_subtract_floats(self) -> None:
        """Test subtracting floating point numbers."""
        assert subtract(5.5, 2.5) == 3.0


class TestMultiply:
    """Tests for the multiply function."""

    def test_multiply_positive_numbers(self) -> None:
        """Test multiplying two positive numbers."""
        assert multiply(2, 3) == 6

    def test_multiply_negative_numbers(self) -> None:
        """Test multiplying two negative numbers."""
        assert multiply(-2, -3) == 6

    def test_multiply_mixed_numbers(self) -> None:
        """Test multiplying positive and negative numbers."""
        assert multiply(-2, 5) == -10

    def test_multiply_by_zero(self) -> None:
        """Test multiplying by zero."""
        assert multiply(5, 0) == 0
        assert multiply(0, 5) == 0

    def test_multiply_floats(self) -> None:
        """Test multiplying floating point numbers."""
        assert multiply(2.5, 4) == 10.0


class TestDivide:
    """Tests for the divide function."""

    def test_divide_positive_numbers(self) -> None:
        """Test dividing two positive numbers."""
        assert divide(6, 3) == 2.0

    def test_divide_negative_numbers(self) -> None:
        """Test dividing two negative numbers."""
        assert divide(-6, -3) == 2.0

    def test_divide_mixed_numbers(self) -> None:
        """Test dividing positive and negative numbers."""
        assert divide(-6, 3) == -2.0

    def test_divide_zero_by_number(self) -> None:
        """Test dividing zero by a number."""
        assert divide(0, 5) == 0.0

    def test_divide_by_zero_raises_error(self) -> None:
        """Test that dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_divide_floats(self) -> None:
        """Test dividing floating point numbers."""
        assert divide(7.5, 2.5) == 3.0
