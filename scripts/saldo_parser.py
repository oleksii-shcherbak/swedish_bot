import xml.etree.ElementTree as ET
import json
from collections import defaultdict


def parse_saldo_final():
    """Parse SALDO with correct priority and form generation."""

    print("Final SALDO parsing...")

    tree = ET.parse('data/saldo.xml')
    root = tree.getroot()

    # Collect ALL entries
    all_entries = defaultdict(list)

    for entry in root.findall('.//LexicalEntry'):
        for form_repr in entry.findall('.//FormRepresentation'):
            word_data = {}
            for feat in form_repr.findall('feat'):
                word_data[feat.get('att')] = feat.get('val')

            if 'writtenForm' in word_data:
                word = word_data['writtenForm'].lower()
                all_entries[word].append(word_data)

    print(f"Found {len(all_entries)} unique words")

    dictionary = {}

    # Process each word
    for word, entries in all_entries.items():
        # Special handling for words with critical verb forms
        if word == 'vara' and any(e.get('paradigm') == 'vb_4m_vara' for e in entries):
            # Force verb entry for vara
            verb_entry = next(e for e in entries if e.get('paradigm') == 'vb_4m_vara')
            process_entry(word, verb_entry, dictionary)
        elif word == 'ha' and any(e.get('paradigm') == 'vb_2m_ha' for e in entries):
            # Force verb entry for ha
            verb_entry = next(e for e in entries if e.get('paradigm') == 'vb_2m_ha')
            process_entry(word, verb_entry, dictionary)
        elif word == 'stor' and any(e.get('partOfSpeech', '').startswith('av') for e in entries):
            # Force adjective entry for stor (not noun)
            adj_entry = next(e for e in entries if e.get('partOfSpeech', '').startswith('av'))
            process_entry(word, adj_entry, dictionary)
        else:
            # Normal priority: vb > av > nn > rest (prioritize adjectives over nouns)
            priority = {'vb': 1, 'av': 2, 'nn': 3, 'ab': 4, 'pm': 10}
            entries_sorted = sorted(entries, key=lambda x: priority.get(x.get('partOfSpeech', '')[:2], 99))
            process_entry(word, entries_sorted[0], dictionary)

    return dictionary


def process_entry(word, entry_data, dictionary):
    """Process a single entry and add to dictionary."""

    pos = entry_data.get('partOfSpeech', '')
    paradigm = entry_data.get('paradigm', '')

    # Create base entry
    entry = {
        'word': word,  # Store the word itself
        'type': get_word_type(pos),
        'paradigm': paradigm,
        'group': get_group(paradigm, pos)
    }

    # Generate forms
    forms = generate_forms(word, paradigm, pos)
    if forms:
        entry['forms'] = forms

    # Add gender for nouns
    if pos.startswith('nn'):
        entry['gender'] = get_gender(paradigm)

    dictionary[word] = entry

    # Add inflected forms
    add_inflected_forms(dictionary, word, forms, entry)


def get_word_type(pos):
    """Convert POS to word type."""
    mapping = {
        'nn': 'noun', 'vb': 'verb', 'av': 'adjective',
        'pm': 'proper_noun', 'ab': 'adverb', 'pp': 'preposition',
        'pn': 'pronoun', 'in': 'interjection', 'vbm': 'verb',
        'nnm': 'noun', 'avm': 'adjective', 'abm': 'adverb',
        'nl': 'numeral'
    }
    base = pos[:3] if pos.startswith(('vbm', 'nnm', 'avm', 'abm')) else pos[:2]
    return mapping.get(base, 'unknown')


def get_gender(paradigm):
    """Get gender from paradigm."""
    # n in second position after _ usually means neuter
    if 'nn_6' in paradigm:
        return 'ett'
    elif 'nn_5n' in paradigm:
        return 'ett'
    elif '_n_' in paradigm or paradigm.endswith('_n'):
        return 'ett'
    return 'en'


def get_group(paradigm, pos):
    """Get grammatical group."""
    if pos.startswith('nn'):
        if '_0' in paradigm:
            return 'Uncountable'
        elif '_1' in paradigm:
            return 'Declension 1 (en, -or)'
        elif '_2' in paradigm:
            return 'Declension 2 (en, -ar)'
        elif '_3' in paradigm:
            return 'Declension 3 (en, -er)'
        elif '_5n' in paradigm:
            return 'Declension 4 (ett, -n)'
        elif '_6' in paradigm:
            return 'Declension 5 (ett, no change)'
        elif '_4' in paradigm or '_5' in paradigm:
            return 'Declension variant'
    elif pos.startswith('vb'):
        if paradigm == 'vb_4m_vara':
            return 'Irregular verb (vara)'
        elif paradigm == 'vb_2m_ha':
            return 'Irregular verb (ha)'
        elif '4' in paradigm:
            return 'Verb group 4 (strong)'
        elif '1' in paradigm or 'va' in paradigm:
            return 'Verb group 1 (-ar)'
        elif '2' in paradigm:
            return 'Verb group 2 (-er)'
        elif '3' in paradigm:
            return 'Verb group 3 (short)'
    return ''


def generate_forms(word, paradigm, pos):
    """Generate inflected forms."""

    if pos.startswith('vb'):
        # Special verbs first
        if paradigm == 'vb_4m_vara':
            return {'infinitive': 'vara', 'present': 'är', 'past': 'var', 'supine': 'varit'}
        elif paradigm == 'vb_2m_ha':
            return {'infinitive': 'ha', 'present': 'har', 'past': 'hade', 'supine': 'haft'}
        # Regular patterns
        elif '1' in paradigm or 'va' in paradigm:
            if word.endswith('a'):
                stem = word[:-1]
                return {'infinitive': word, 'present': word + 'r', 'past': stem + 'ade', 'supine': stem + 'at'}
        elif '2' in paradigm:
            if word.endswith('a'):
                stem = word[:-1]
                if stem and stem[-1] in 'ptksx':
                    return {'infinitive': word, 'present': stem + 'er', 'past': stem + 'te', 'supine': stem + 't'}
                return {'infinitive': word, 'present': stem + 'er', 'past': stem + 'de', 'supine': stem + 't'}

    elif pos.startswith('nn'):
        # Nouns by paradigm pattern
        if '_0' in paradigm:
            return [word, word + 'en', '-', '-']
        elif '_1' in paradigm:
            if word.endswith('a'):
                stem = word[:-1]
                return [word, word + 'n', stem + 'or', stem + 'orna']
            return [word, word + 'n', word + 'or', word + 'orna']
        elif '_2' in paradigm:
            return [word, word + 'en', word + 'ar', word + 'arna']
        elif '_3' in paradigm:
            return [word, word + 'en', word + 'er', word + 'erna']
        elif 'nn_5n' in paradigm:
            # Special handling for äpple-type words (nn_5n_saldo)
            # These are ett-words that take -n in plural
            if word.endswith('e'):
                stem = word[:-1]  # Remove final 'e'
                return [word, stem + 'et', stem + 'en', stem + 'ena']
            elif word.endswith('a'):
                stem = word[:-1]  # Remove final 'a'
                return [word, stem + 'at', stem + 'an', stem + 'ana']
            elif word.endswith('um'):
                stem = word[:-2]  # Remove 'um'
                return [word, stem + 'et', stem + 'a', stem + 'ana']
            elif word[-1] in 'oiuyåäö':  # Other vowels
                # For vowels o, i, u, y, å, ä, ö: add 't' directly
                return [word, word + 't', word + 'n', word + 'na']
            else:
                # Consonant ending: add 'et'
                return [word, word + 'et', word + 'n', word + 'na']
        elif '_6' in paradigm:
            return [word, word + 'et', word, word + 'en']

    elif pos.startswith('av'):
        # Adjectives
        if word == 'stor':  # Known irregular
            return {'en_form': 'stor', 'ett_form': 'stort', 'plural': 'stora',
                    'comparative': 'större', 'superlative': 'störst'}
        # Regular
        ett = word + 't' if not word.endswith(('t', 'd')) else word
        plural = word + 'a' if not word.endswith('a') else word
        return {'en_form': word, 'ett_form': ett, 'plural': plural,
                'comparative': word + 'are', 'superlative': word + 'ast'}

    return None


def add_inflected_forms(dictionary, base_word, forms, entry_data):
    """Add inflected forms to dictionary."""
    if not forms:
        return

    word_type = entry_data['type']

    if word_type == 'verb' and isinstance(forms, dict):
        for form_type, form_value in forms.items():
            if form_value and form_value != base_word:
                if form_value not in dictionary:
                    dictionary[form_value] = {
                        'type': 'verb',
                        'is_form': True,
                        'base_word': base_word,
                        'form_type': form_type,
                        'group': entry_data.get('group'),
                        'forms': forms
                    }

    elif word_type == 'noun' and isinstance(forms, list):
        form_names = ['singular indefinite', 'singular definite',
                      'plural indefinite', 'plural definite']
        for i, form in enumerate(forms):
            if form and form != base_word and form != '-':
                if form not in dictionary:
                    dictionary[form] = {
                        'type': 'noun',
                        'is_form': True,
                        'base_word': base_word,
                        'form_type': form_names[i],
                        'group': entry_data.get('group'),
                        'gender': entry_data.get('gender'),
                        'forms': forms
                    }

    elif word_type == 'adjective' and isinstance(forms, dict):
        for form_type, form_value in forms.items():
            # Add all forms except en_form (which is usually the base word)
            if form_value and form_value != base_word:
                if form_value not in dictionary:
                    dictionary[form_value] = {
                        'type': 'adjective',
                        'is_form': True,
                        'base_word': base_word,
                        'form_type': form_type.replace('_', ' '),
                        'group': 'Adjective',
                        'forms': forms
                    }


if __name__ == '__main__':
    dictionary = parse_saldo_final()

    with open('data/swedish_dictionary_complete.json', 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(dictionary)} entries")

    # Test critical words
    test_words = ['vara', 'är', 'äpple', 'äpplen', 'hus', 'huset']
    print("\nTesting:")
    for word in test_words:
        if word in dictionary:
            entry = dictionary[word]
            print(f"✓ {word}: {entry['type']} - {entry.get('form_type', 'base')}")
            if word in ['äpple', 'vara']:
                print(f"  Forms: {entry.get('forms')}")
        else:
            print(f"✗ {word} NOT FOUND")
