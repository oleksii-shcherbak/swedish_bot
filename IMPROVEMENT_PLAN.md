# Bot Improvement Plan

## Issues to Address

1. Missing strong/modal verb forms (skriva, dricka, kunna, etc.)
2. Ambiguous words not detected (vecka, ren, etc.)
3. User feedback system needed

## Implementation Steps

### Step 1: Strong Verbs File (DONE)
Created `data/strong_verbs.json` with 19 common strong/modal verbs

### Step 2: Expanded Ambiguous Words
Replace `data/ambiguous_words.json` with `data/ambiguous_words_expanded.json`

### Step 3: Update Dictionary Service
Add strong verbs loading (DONE) and lookup priority

### Step 4: Add Report Button
Add "Report Issue" button to every word card

### Step 5: Feedback Logging System
Log reported words to `data/reported_words.json`

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
