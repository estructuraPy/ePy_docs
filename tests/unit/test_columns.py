"""
Test suite for column width calculation functionality (core feature).
"""

import pytest
from ePy_docs.core._document import ColumnWidthCalculator


class TestColumnWidthCalculator:
    """Test column width calculation functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.calculator = ColumnWidthCalculator()

    def test_calculate_width_single_column(self):
        """Test width calculation for single column documents."""
        # Full width in 1-column layout
        width = self.calculator.calculate_width("paper", 1, 1.0)
        assert width == 6.5, "Full width should be 6.5 inches for paper"
        
        # Fractional width (0.5 of 6.5 = 3.25)
        width = self.calculator.calculate_width("paper", 1, 0.5)
        assert width == 3.25, "Half width should be 3.25 inches (0.5 * 6.5)"

    def test_calculate_width_two_column(self):
        """Test width calculation for two column documents."""
        width = self.calculator.calculate_width("paper", 2, 2.0)
        assert width == 6.5, "Full width should be 6.5 inches for paper"
        
        width = self.calculator.calculate_width("paper", 2, 1.0)
        expected = 3.1
        assert width == expected, f"Single column width should be {expected}"

    def test_get_width_string(self):
        """Test width string formatting."""
        width_str = self.calculator.get_width_string(6.5)
        assert width_str == "6.5in", "Width string should be formatted as inches"
        
        width_str = self.calculator.get_width_string(3.25)
        assert width_str == "3.25in", "Width string should maintain precision"

    def test_invalid_column_span(self):
        """Test handling of column spans larger than layout columns."""
        # Requesting 3 columns in a 2-column layout should calculate width
        # 3 * 3.1 (single width) + 2 * 0.3 (gaps) = 9.9
        width = self.calculator.calculate_width("paper", 2, 3.0)
        expected = 3 * 3.1 + 2 * 0.3  # 9.9
        assert abs(width - expected) < 0.01, f"Expected {expected}, got {width}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
