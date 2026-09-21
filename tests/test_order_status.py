import pytest
from backend.tools.order_status import check_order_status

def test_check_order_status_valid_delivered():
    result = check_order_status("NB-1042873")
    assert result["found"] is True
    assert result["order_id"] == "NB-1042873"
    assert result["status"] == "Delivered"
    assert result["customer_name"] == "Liam Hargreaves"

def test_check_order_status_valid_delayed():
    result = check_order_status("NB-1095768")
    assert result["found"] is True
    assert result["order_id"] == "NB-1095768"
    assert result["status"] == "Delayed"

def test_check_order_status_unknown():
    result = check_order_status("NB-9999999")
    assert result["found"] is False
    assert result["order_id"] == "NB-9999999"
    assert "error" in result

def test_check_order_status_invalid_empty():
    result = check_order_status("")
    assert result["found"] is False
    assert result["order_id"] == ""
    assert "error" in result
