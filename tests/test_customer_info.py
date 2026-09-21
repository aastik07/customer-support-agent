import pytest
from backend.tools.customer_info import get_customer_info

def test_get_customer_info_valid():
    result = get_customer_info("CUST-00391")
    assert result["found"] is True
    assert result["customer_id"] == "CUST-00391"
    assert result["customer_name"] == "Liam Hargreaves"
    assert result["total_orders"] == 1
    assert len(result["orders"]) == 1
    assert result["orders"][0]["order_id"] == "NB-1042873"

def test_get_customer_info_unknown():
    result = get_customer_info("CUST-999999")
    assert result["found"] is False
    assert result["customer_id"] == "CUST-999999"
    assert "error" in result

def test_get_customer_info_invalid_empty():
    result = get_customer_info("")
    assert result["found"] is False
    assert result["customer_id"] == ""
    assert "error" in result
