"""
Verification Unit Test for Lokiini Biometrics & CNDP Engine
"""
import sys

# Ensure UTF-8 output encoding for cross-platform stability
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from liveness_detector import detector
from cin_ocr import cin_parser
from cndp_audit import generate_cndp_zero_knowledge_proof

def test_biometrics_pipeline():
    print("================================================================")
    print(" LOKIINI BIOMETRICS & CNDP ENGINE UNIT TESTS")
    print("================================================================")

    # 1. Test Moroccan CIN Parser
    print("\n[1] Testing Moroccan CIN Parsing & Validation...")
    valid_cins = ["BK849201", "AA12345", "BE998877", "k49201", "CD789123"]
    invalid_cins = ["12345", "INVALID", "", "Z"]

    for cin in valid_cins:
        res = cin_parser.parse_document(cin)
        assert res["is_valid_format"] is True, f"Failed for {cin}"
        print(f"  [OK] Valid CIN: {cin} -> Center: {res['issuing_center']}")

    for cin in invalid_cins:
        assert cin_parser.validate_cin_format(cin) is False, f"Should be invalid: {cin}"
        print(f"  [OK] Correctly rejected invalid CIN: '{cin}'")

    # 2. Test Liveness Detection
    print("\n[2] Testing Liveness Detection (ISO/IEC 30107-3)...")
    live_result = detector.evaluate_liveness(cin_number="BK849201", head_turn_detected=True, blink_count=2)
    assert live_result["is_live"] is True
    assert live_result["liveness_score"] >= 85.0
    print(f"  [OK] Liveness Score: {live_result['liveness_score']}% (Pass threshold: {live_result['threshold']}%)")
    print(f"  [OK] Attack Type: {live_result['attack_type']} ({live_result['iso_standard']})")

    # 3. Test CNDP Zero-Knowledge Proof
    print("\n[3] Testing CNDP Zero-Knowledge Cryptographic Proof...")
    cndp_proof = generate_cndp_zero_knowledge_proof("BK849201", live_result["liveness_score"])
    assert len(cndp_proof["audit_proof_sha256"]) == 64
    print(f"  [OK] CNDP Audit Hash (SHA-256): {cndp_proof['audit_proof_sha256']}")
    print(f"  [OK] Legal Reference: {cndp_proof['cndp_declaration_ref']}")

    print("\n================================================================")
    print(" ALL BIOMETRICS TESTS PASSED SUCCESSFULLY (100% OK)")
    print("================================================================")

if __name__ == "__main__":
    test_biometrics_pipeline()
