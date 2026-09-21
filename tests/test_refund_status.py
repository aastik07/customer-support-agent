import pytest
from backend.tools.refund_status import check_refund_status

def test_check_refund_status_none():
    result = check_refund_status("NB-1042873")
    assert result["found"] is True
    assert result["order_id"] == "NB-1042873"
    assert result["refund_status"] == "None"
    assert "No refund has been requested" in result["refund_description"]

def test_check_refund_status_requested():
    result = check_refund_status("NB-1063017")
    assert result["found"] is True
    assert result["order_id"] == "NB-1063017"
    assert result["refund_status"] == "Refund Requested"
    assert "currently under review" in result["refund_description"]

def test_check_refund_status_refunded():
    result = check_refund_status("NB-1034682")
    assert result["found"] is True
    assert result["order_id"] == "NB-1034682"
    assert result["refund_status"] == "Refunded"
    assert "already been issued" in result["refund_description"]

def test_check_refund_status_unknown():
    result = check_refund_status("NB-9999999")
    assert result["found"] is False
    assert result["order_id"] == "NB-9999999"
    assert "error" in result

def test_check_refund_status_invalid_empty():
    result = check_refund_status("")
    assert result["found"] is False
    assert result["order_id"] == ""
    assert "error" in result
