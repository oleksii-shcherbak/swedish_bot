import json
import gzip
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SwedishDictionary:
    """Service for Swedish word lookups using SALDO dictionary with irregular verb support."""

    def __init__(self, dict_path: Optional[str] = None, ambiguous_path: Optional[str] = None):
        """
        Initialize the Swedish dictionary service.

        Args:
            dict_path: Optional path to dictionary file.
            ambiguous_path: Optional path to ambiguous words file.
        """
        if dict_path is None:
            # Try compressed file first
            compressed_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'data',
                'dictionary.json.gz'
            )
            dict_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'data',
                'swedish_dictionary_complete.json'
            )
            
            # Use compressed if it exists
            if os.path.exists(compressed_path):
                dict_path = compressed_path
        
        if ambiguous_path is None:
            ambiguous_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'data',
                'ambiguous_words.json'
            )
        
        ordinal_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'ordinal_numbers.json'
        )
        
        strong_verbs_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'strong_verbs.json'
        )
        
        irregular_verbs_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'irregular_verbs_comprehensive.json'
        )

        # Load main dictionary
        try:
            # Check if compressed
            if dict_path.endswith('.gz'):
                with gzip.open(dict_path, 'rt', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} Swedish words from compressed dictionary")
            else:
                with open(dict_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Loaded {len(self.data)} Swedish words from SALDO")
        except FileNotFoundError:
            logger.error(f"Dictionary file not found: {dict_path}")
            self.data = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing dictionary: {e}")
            self.data = {}
        
        # Load ambiguous words
        try:
            with open(ambiguous_path, 'r', encoding='utf-8') as f:
                self.ambiguous_words = json.load(f)
            logger.info(f"Loaded {len(self.ambiguous_words)} ambiguous words")
        except FileNotFoundError:
            logger.warning(f"Ambiguous words file not found: {ambiguous_path}")
            self.ambiguous_words = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing ambiguous words: {e}")
            self.ambiguous_words = {}
        
        # Load ordinal numbers
        try:
            with open(ordinal_path, 'r', encoding='utf-8') as f:
                self.ordinals = json.load(f)
            logger.info(f"Loaded {len(self.ordinals)} ordinal numbers")
        except FileNotFoundError:
            logger.warning(f"Ordinal numbers file not found: {ordinal_path}")
            self.ordinals = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing ordinal numbers: {e}")
            self.ordinals = {}
        
        # Load strong verbs (legacy)
        try:
            with open(strong_verbs_path, 'r', encoding='utf-8') as f:
                self.strong_verbs = json.load(f)
            logger.info(f"Loaded {len(self.strong_verbs)} strong/modal verbs")
        except FileNotFoundError:
            logger.warning(f"Strong verbs file not found: {strong_verbs_path}")
            self.strong_verbs = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing strong verbs: {e}")
            self.strong_verbs = {}
        
        # Load comprehensive irregular verbs
        try:
            with open(irregular_verbs_path, 'r', encoding='utf-8') as f:
                self.irregular_verbs_data = json.load(f)
            
            # Build lookup tables
            self.irregular_verbs = {}
            self.irregular_forms_lookup = {}
            
            # Process each group
            for group_name, verbs in self.irregular_verbs_data.items():
                if group_name == 'metadata' or not isinstance(verbs, list):
                    continue
                
                for verb in verbs:
                    infinitive = verb.get('infinitive')
                    if not infinitive:
                        continue
                    
                    # Store the full verb data by infinitive
                    self.irregular_verbs[infinitive] = verb
                    
                    # Create lookups for all forms
                    forms_to_index = [
                        ('infinitive', infinitive),
                        ('present', verb.get('present')),
                        ('past', verb.get('past')),
                        ('supine', verb.get('supine')),
                        ('imperative', verb.get('imperative')),
                        ('past_participle', verb.get('past_participle'))
                    ]
                    
                    for form_type, form_value in forms_to_index:
                        if form_value and form_value != 'None':
                            # Add form to lookup
                            if form_value not in self.irregular_forms_lookup:
                                self.irregular_forms_lookup[form_value] = []
                            self.irregular_forms_lookup[form_value].append({
                                'infinitive': infinitive,
                                'form_type': form_type,
                                'verb_data': verb
                            })
            
            total_verbs = len(self.irregular_verbs)
            total_forms = len(self.irregular_forms_lookup)
            logger.info(f"Loaded {total_verbs} irregular verbs with {total_forms} unique forms")
            
        except FileNotFoundError:
            logger.warning(f"Irregular verbs file not found: {irregular_verbs_path}")
            self.irregular_verbs = {}
            self.irregular_forms_lookup = {}
        except Exception as e:
            logger.error(f"Error loading irregular verbs: {e}")
            self.irregular_verbs = {}
            self.irregular_forms_lookup = {}

    def lookup(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Look up a Swedish word with priority order.
        
        Priority:
        1. Check ambiguous words
        2. Check ordinal numbers
        3. Check irregular verbs (all forms)
        4. Check strong/modal verbs
        5. Check main SALDO dictionary
        
        Args:
            word: The Swedish word to look up.
            
        Returns:
            Dictionary with word information or None if not found.
        """
        word = word.lower().strip()
        
        # 1. Check ambiguous words first
        if word in self.ambiguous_words:
            logger.info(f"Found ambiguous word: {word}")
            return {
                'type': 'ambiguous',
                'meanings': self.ambiguous_words[word]
            }
        
        # 2. Check ordinal numbers
        if word in self.ordinals:
            logger.info(f"Found ordinal number: {word}")
            return self.ordinals[word]
        
        # 3. Check irregular verbs - both infinitive and all forms
        if word in self.irregular_verbs:
            # Direct infinitive match
            verb_data = self.irregular_verbs[word]
            logger.info(f"Found irregular verb (infinitive): {word}")
            return self._format_irregular_verb(verb_data)
        
        if word in self.irregular_forms_lookup:
            # Found as an inflected form
            matches = self.irregular_forms_lookup[word]
            if len(matches) == 1:
                # Single match - return the verb
                verb_data = matches[0]['verb_data']
                logger.info(f"Found irregular verb form '{word}' ({matches[0]['form_type']}) -> {verb_data['infinitive']}")
                return self._format_irregular_verb(verb_data)
            else:
                # Multiple matches - treat as ambiguous
                meanings = []
                for match in matches:
                    verb_data = match['verb_data']
                    meanings.append(self._format_irregular_verb(verb_data))
                logger.info(f"Found ambiguous irregular verb form '{word}' with {len(matches)} meanings")
                return {
                    'type': 'ambiguous',
                    'meanings': meanings
                }
        
        # 4. Check strong verbs (legacy)
        if word in self.strong_verbs:
            logger.info(f"Found strong/modal verb: {word}")
            return self.strong_verbs[word]
        
        # Check if word is a form of a strong verb
        for verb_infinitive, verb_data in self.strong_verbs.items():
            if 'forms' in verb_data:
                forms = verb_data['forms']
                if word in forms.values():
                    logger.info(f"Found strong verb form '{word}' -> {verb_infinitive}")
                    return verb_data
        
        # 5. Check main SALDO dictionary
        if word in self.data:
            logger.info(f"Found word in SALDO: {word}")
            return self.data[word]
        
        logger.warning(f"Word not found: {word}")
        return None
    
    def _format_irregular_verb(self, verb_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format irregular verb data for display.
        
        Args:
            verb_data: Raw verb data from irregular_verbs.json
            
        Returns:
            Formatted verb dictionary.
        """
        # Determine verb group based on pattern
        if verb_data.get('pattern') == 'highly_irregular':
            group = "Verb group 4 (highly irregular)"
        elif verb_data.get('pattern') == 'modal':
            group = "Modal verb"
        elif verb_data.get('pattern') == 'deponent':
            group = "Deponent verb (passive form only)"
        else:
            group = "Verb group 3 (strong)"
        
        # Build forms dictionary
        forms = {
            'infinitive': verb_data.get('infinitive'),
            'present': verb_data.get('present'),
            'past': verb_data.get('past'),
            'supine': verb_data.get('supine')
        }
        
        # Add optional forms if present
        if verb_data.get('imperative'):
            forms['imperative'] = verb_data.get('imperative')
        if verb_data.get('past_participle'):
            forms['past_participle'] = verb_data.get('past_participle')
        if verb_data.get('passive_infinitive'):
            forms['passive_infinitive'] = verb_data.get('passive_infinitive')
        if verb_data.get('passive_present'):
            forms['passive_present'] = verb_data.get('passive_present')
        if verb_data.get('passive_past'):
            forms['passive_past'] = verb_data.get('passive_past')
        
        result = {
            'type': 'verb',
            'group': group,
            'forms': forms
        }
        
        # Add meaning if available
        if verb_data.get('meaning'):
            result['description'] = verb_data.get('meaning')
        
        # Add frequency if available
        if verb_data.get('frequency'):
            result['frequency'] = verb_data.get('frequency')
        
        return result

    def suggest(self, partial: str, limit: int = 5) -> List[str]:
        """
        Suggest words starting with the given partial string.
        
        Args:
            partial: Partial word to search for.
            limit: Maximum number of suggestions.
            
        Returns:
            List of suggested words.
        """
        partial = partial.lower().strip()
        suggestions = []

        # First check irregular verbs
        for infinitive in self.irregular_verbs.keys():
            if infinitive.startswith(partial):
                suggestions.append(infinitive)
                if len(suggestions) >= limit:
                    return suggestions
        
        # Then check main dictionary
        for word, data in self.data.items():
            # Skip word forms for suggestions
            if not data.get('is_form'):
                if word.startswith(partial):
                    suggestions.append(word)
                    if len(suggestions) >= limit:
                        break

        return suggestions
    
    def get_suggestions(self, word: str, limit: int = 5) -> List[str]:
        """
        Get word suggestions for a misspelled word.
        Alias for suggest() to maintain compatibility.
        
        Args:
            word: The word to get suggestions for.
            limit: Maximum number of suggestions.
            
        Returns:
            List of suggested words.
        """
        return self.suggest(word, limit)

    def get_stats(self) -> Dict[str, int]:
        """Get dictionary statistics."""
        stats = {
            'total_entries': len(self.data),
            'irregular_verbs': len(self.irregular_verbs),
            'irregular_forms': len(self.irregular_forms_lookup),
            'strong_verbs': len(self.strong_verbs),
            'ambiguous_words': len(self.ambiguous_words),
            'base_words': 0,
            'word_forms': 0,
            'nouns': 0,
            'verbs': 0,
            'adjectives': 0
        }

        for word, data in self.data.items():
            if data.get('is_form'):
                stats['word_forms'] += 1
            else:
                stats['base_words'] += 1

            word_type = data.get('type')
            if word_type == 'noun':
                stats['nouns'] += 1
            elif word_type == 'verb':
                stats['verbs'] += 1
            elif word_type == 'adjective':
                stats['adjectives'] += 1

        return stats
