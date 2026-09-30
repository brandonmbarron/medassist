from src.agent.graph import route
from src.guardrails.redact import redact
from src.guardrails.safety import check_output


def test_redacts_ssn_phone_email_member_id():
    out = redact("SSN 123-45-6789, call 502-555-0199, a@b.com, member M0001234")
    assert "123-45-6789" not in out
    assert "502-555-0199" not in out
    assert "a@b.com" not in out
    assert "M0001234" not in out


def test_urgent_always_escalates_even_with_high_confidence():
    assert route({"intent": "urgent_clinical", "confidence": 0.99}) == "escalate"


def test_low_confidence_escalates():
    assert route({"intent": "benefits", "confidence": 0.3}) == "escalate"


def test_ungrounded_answer_is_flagged():
    assert "no_citation" in check_output("Your MRI copay is $150.", citations=[])


def test_medical_advice_is_flagged():
    flags = check_output("You should stop taking that medication.", ["doc#1"])
    assert "possible_medical_advice" in flags
