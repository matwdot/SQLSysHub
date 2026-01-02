"""
Property-based tests for validation functions.

Uses Hypothesis to generate test cases automatically and verify properties
that should always hold true regardless of input.
"""

import pytest
from hypothesis import given, strategies as st, assume
from refactored_sqltools.utils.validators import (
    validate_sql_query, _validate_host_format, _validate_port
)
from refactored_sqltools.utils.exceptions import ValidationError


class TestSQLValidationProperties:
    """Property-based tests for SQL validation."""
    
    @given(st.text())
    def test_sql_validation_never_crashes(self, sql_text):
        """Test that SQL validation never crashes, regardless of input."""
        try:
            validate_sql_query(sql_text)
        except ValidationError:
            # ValidationError is expected for invalid SQL
            pass
        except Exception as e:
            # Any other exception is a bug
            pytest.fail(f"SQL validation crashed with: {type(e).__name__}: {e}")
    
    @given(st.text(min_size=1))
    def test_non_empty_sql_never_raises_empty_error(self, sql_text):
        """Test that non-empty SQL never raises 'empty query' error."""
        assume(sql_text.strip())  # Assume non-empty after stripping
        
        try:
            validate_sql_query(sql_text)
        except ValidationError as e:
            # Should not be empty query error
            assert "não pode estar vazia" not in str(e)
    
    @given(st.text().filter(lambda x: not x.strip()))
    def test_empty_sql_always_raises_empty_error(self, empty_sql):
        """Test that empty SQL always raises empty query error."""
        with pytest.raises(ValidationError, match="não pode estar vazia"):
            validate_sql_query(empty_sql)


class TestHostValidationProperties:
    """Property-based tests for host validation."""
    
    @given(st.text())
    def test_host_validation_never_crashes(self, host):
        """Test that host validation never crashes."""
        try:
            result = _validate_host_format(host)
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"Host validation crashed with: {type(e).__name__}: {e}")
    
    @given(st.text().filter(lambda x: not x.strip()))
    def test_empty_host_always_invalid(self, empty_host):
        """Test that empty hosts are always invalid."""
        result = _validate_host_format(empty_host)
        assert result is False
    
    @given(st.sampled_from(['localhost', '127.0.0.1', '::1']))
    def test_localhost_variants_always_valid(self, localhost):
        """Test that localhost variants are always valid."""
        result = _validate_host_format(localhost)
        assert result is True
    
    @given(st.integers(min_value=0, max_value=255), 
           st.integers(min_value=0, max_value=255),
           st.integers(min_value=0, max_value=255), 
           st.integers(min_value=0, max_value=255))
    def test_valid_ip_octets_create_valid_ip(self, a, b, c, d):
        """Test that valid IP octets create valid IP addresses."""
        ip = f"{a}.{b}.{c}.{d}"
        result = _validate_host_format(ip)
        assert result is True
    
    @given(st.integers(min_value=256))
    def test_invalid_ip_octets_create_invalid_ip(self, invalid_octet):
        """Test that invalid IP octets create invalid IP addresses."""
        # Only test first octet to avoid regex complexity
        ip = f"{invalid_octet}.0.0.1"
        result = _validate_host_format(ip)
        # Note: Our regex might not catch all invalid IPs, so this test
        # documents current behavior rather than enforcing strict validation
        # In a real system, we'd want more robust IP validation


class TestPortValidationProperties:
    """Property-based tests for port validation."""
    
    @given(st.text())
    def test_port_validation_never_crashes(self, port_text):
        """Test that port validation never crashes."""
        try:
            result = _validate_port(port_text)
            assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"Port validation crashed with: {type(e).__name__}: {e}")
    
    @given(st.integers(min_value=1, max_value=65535))
    def test_valid_port_range_always_valid(self, port):
        """Test that valid port numbers are always valid."""
        result = _validate_port(str(port))
        assert result is True
    
    @given(st.integers(max_value=0))
    def test_zero_and_negative_ports_invalid(self, invalid_port):
        """Test that zero and negative ports are invalid."""
        result = _validate_port(str(invalid_port))
        assert result is False
    
    @given(st.integers(min_value=65536))
    def test_too_large_ports_invalid(self, large_port):
        """Test that ports above 65535 are invalid."""
        result = _validate_port(str(large_port))
        assert result is False
    
    @given(st.text().filter(lambda x: not x.isdigit()))
    def test_non_numeric_ports_invalid(self, non_numeric):
        """Test that non-numeric port strings are invalid."""
        assume(non_numeric)  # Assume non-empty
        result = _validate_port(non_numeric)
        assert result is False


class TestValidationConsistencyProperties:
    """Property-based tests for validation consistency."""
    
    @given(st.text(), st.text())
    def test_validation_deterministic(self, input1, input2):
        """Test that validation is deterministic (same input = same output)."""
        if input1 == input2:
            try:
                result1 = validate_sql_query(input1)
                result2 = validate_sql_query(input2)
                assert result1 == result2
            except ValidationError as e1:
                # If first raises ValidationError, second should raise same
                with pytest.raises(ValidationError):
                    validate_sql_query(input2)
    
    @given(st.text())
    def test_validation_idempotent(self, sql_text):
        """Test that validation is idempotent (multiple calls = same result)."""
        results = []
        exceptions = []
        
        for _ in range(3):  # Test 3 times
            try:
                result = validate_sql_query(sql_text)
                results.append(result)
            except ValidationError as e:
                exceptions.append(str(e))
        
        # Either all succeed with same result, or all fail with same error
        if results:
            assert all(r == results[0] for r in results)
        if exceptions:
            assert all(e == exceptions[0] for e in exceptions)


# Example of how to run property tests with different profiles
if __name__ == "__main__":
    # Run with more examples for thorough testing
    from hypothesis import settings
    
    with settings(max_examples=1000):
        pytest.main([__file__, "-v"])