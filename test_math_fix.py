#!/usr/bin/env python3
"""Test de validation - Logique mathématique Point A.2"""

test_cases = [
    {
        "input": "(x-2)² = 49",
        "expected": ["x = 9", "x = -5"],
        "type": "equation_quadratique"
    },
    {
        "input": "(x-3)² = 16",
        "expected": ["x = 7", "x = -1"],
        "type": "equation_quadratique"
    },
    {
        "input": "3x + 5 = 20",
        "expected": ["x = 5"],
        "type": "equation_lineaire"
    },
    {
        "input": "659 + 341",
        "expected": ["1000"],
        "type": "calcul_arithmetique"
    }
]

def test_math_detection():
    from fix_math_logic import detect_math_type
    
    print("🧪 Test de détection des types...")
    for case in test_cases:
        detected = detect_math_type(case["input"])
        status = "✅" if detected == case["type"] else "❌"
        print(f"{status} {case['input'][:20]}... → {detected}")

if __name__ == "__main__":
    print("="*50)
    print("TEST LOGIQUE MATHÉMATIQUE - Point A.2")
    print("="*50)
    test_math_detection()
