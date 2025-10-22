# Bot Improvement Plan

## ✅ COMPLETED (October 22, 2025)

### All Issues Resolved:

1. ✅ Missing strong/modal verb forms - Comprehensive irregular verbs database (238 verbs)
2. ✅ Ambiguous words not detected - All reported words added and working
3. ✅ User feedback system - Report button and logging system implemented

## Implementation Completed

### Step 1: Strong Verbs File ✅ DONE
Created `data/irregular_verbs_comprehensive.json` with 238 irregular verbs

### Step 2: Expanded Ambiguous Words ✅ DONE
Updated `data/ambiguous_words.json` with all reported words:
- ren (adjective/noun)
- vecka (noun/verb)
- veckor (plural form)
- vackra (adjective form)

### Step 3: Update Dictionary Service ✅ DONE
Fixed return format to be consistent:
- `{'ambiguous': True/False, 'data': {...}, 'word': word}`

### Step 4: Add Report Button ✅ DONE
Report button on every word card working correctly

### Step 5: Feedback Logging System ✅ DONE
Log reported words to `data/reported_words.json` - 3 reports received and resolved

## Deployment Status

✅ Committed to Git: October 22, 2025
✅ Pushed to GitHub: October 22, 2025
✅ Railway auto-deployment: In progress
✅ All tests passing locally

## Files to Modify

1. `services/dictionary_service.py` - Add strong verbs priority
2. `main.py` - Add report button and feedback handler
3. `data/ambiguous_words.json` - Expand with vecka, ren
4. `data/reported_words.json` - Create empty array

## How to Add More Words

### Strong Verbs
Edit `data/strong_verbs.json`:
```json
{
  "verb_infinitive": {
    "type": "verb",
    "group": "Verb group 4 (strong)",
    "forms": {
      "infinitive": "...",
      "present": "...",
      "past": "...",
      "supine": "..."
    }
  }
}
```

### Ambiguous Words
Edit `data/ambiguous_words.json` - follow existing format with detailed forms

## Deployment
After changes:
1. Test locally
2. Compress dictionary: `python3 compress_dictionary.py`
3. Commit and push
4. Railway auto-deploys

## User Feedback Collection
Users click "Report Issue" button → word saved to `reported_words.json` → you review and add to exception files
