import pytest
import re
from backend.tools.support_ticket import create_support_ticket

def test_create_support_ticket_valid():
    result = create_support_ticket("CUST-00391", "The item arrived damaged and I would like a replacement.")
    assert result["success"] is True
    assert result["customer_id"] == "CUST-00391"
    assert result["status"] == "Open"
    assert "issue_summary" in result
    assert "expected_response_by" in result
    
    # Verify ticket ID format: TKT-XXXXXX (6 uppercase alphanumeric)
    ticket_id = result["ticket_id"]
    assert re.match(r"^TKT-[A-Z0-9]{6}$", ticket_id) is not None

def test_create_support_ticket_invalid_customer():
    result = create_support_ticket("", "The item arrived damaged.")
    assert result["success"] is False
    assert result["customer_id"] == ""
    assert "error" in result

def test_create_support_ticket_invalid_issue_empty():
    result = create_support_ticket("CUST-00391", "")
    assert result["success"] is False
    assert result["customer_id"] == "CUST-00391"
    assert "error" in result

def test_create_support_ticket_invalid_issue_short():
    result = create_support_ticket("CUST-00391", "bad")
    assert result["success"] is False
    assert result["customer_id"] == "CUST-00391"
    assert "error" in result
