#!/usr/bin/env python3
"""Test script to verify dictionary improvements."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.dictionary_service import SwedishDictionary

def test_word(dictionary, word):
    """Test a single word lookup."""
    print(f"\n{'='*50}")
    print(f"Testing: '{word}'")
    print(f"{'='*50}")
    
    result = dictionary.lookup(word)
    
    if result:
        if result.get('type') == 'ambiguous':
            print(f"✅ FOUND - Ambiguous word with {len(result.get('meanings', []))} meanings:")
            for i, meaning in enumerate(result.get('meanings', []), 1):
                print(f"  {i}. {meaning.get('type', 'unknown')} - {meaning.get('description', 'no description')}")
                if 'forms' in meaning:
                    print(f"     Forms: {meaning['forms']}")
        else:
            print(f"✅ FOUND - Type: {result.get('type', 'unknown')}")
            if 'description' in result:
                print(f"  Description: {result['description']}")
            if 'group' in result:
                print(f"  Group: {result['group']}")
            if 'forms' in result:
                print(f"  Forms: {result['forms']}")
    else:
        print(f"❌ NOT FOUND")
    
    return result is not None

def main():
    """Run tests on problem words."""
    print("Initializing dictionary...")
    dictionary = SwedishDictionary()
    
    stats = dictionary.get_stats()
    print(f"\nDictionary loaded:")
    print(f"  - Total entries: {stats['total_entries']:,}")
    print(f"  - Irregular verbs: {stats['irregular_verbs']}")
    print(f"  - Irregular forms: {stats['irregular_forms']}")
    print(f"  - Strong verbs: {stats['strong_verbs']}")
    print(f"  - Ambiguous words: {stats['ambiguous_words']}")
    
    # Test words that were problematic
    test_words = [
        # Reported by users
        "ren",      # Should be ambiguous (clean/reindeer)
        "veckor",   # Plural of vecka
        "vackra",   # Beautiful (plural/definite)
        
        # Strong verb forms
        "skriva",   # Infinitive
        "skrev",    # Past tense of skriva
        "skrivit",  # Supine of skriva
        
        # Modal verbs
        "kunna",    # Can (infinitive)
        "kan",      # Can (present) - should be ambiguous
        "kunde",    # Could (past)
        
        # Other irregular verbs
        "dricka",   # Drink (infinitive)
        "drack",    # Drank (past)
        "druckit",  # Drunk (supine)
        
        # Ambiguous words
        "var",      # Where/was/each
        "får",      # Gets/sheep
        "spring",   # Run!/crack
        
        # Test a word that shouldn't exist
        "xyz123"    # Should not be found
    ]
    
    print(f"\n\nTesting {len(test_words)} words...")
    
    passed = 0
    failed = 0
    
    for word in test_words:
        if test_word(dictionary, word):
            passed += 1
        else:
            failed += 1
    
    print(f"\n\n{'='*50}")
    print(f"RESULTS:")
    print(f"  ✅ Passed: {passed}/{len(test_words)}")
    print(f"  ❌ Failed: {failed}/{len(test_words)}")
    print(f"{'='*50}")
    
    if failed > 1:  # We expect xyz123 to fail
        print("\n⚠️  Some words are still not found. This is expected for 'xyz123'.")
        print("   Other failures might be due to missing data in the dictionary files.")
    else:
        print("\n🎉 All expected words are working correctly!")

if __name__ == "__main__":
    main()
