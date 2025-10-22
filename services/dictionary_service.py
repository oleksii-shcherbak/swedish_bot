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
        Returns format compatible with main.py expectations.
        
        Args:
            word: The Swedish word to look up.
            
        Returns:
            Dictionary with word information or None if not found.
            Format:
            - {'ambiguous': True, 'meanings': [...], 'word': word} for ambiguous
            - {'ambiguous': False, 'data': {...}, 'word': word} for regular words
        """
        word = word.lower().strip()
        
        # 1. Check ambiguous words first
        if word in self.ambiguous_words:
            logger.info(f"Found ambiguous word: {word}")
            return {
                'ambiguous': True,
                'meanings': self.ambiguous_words[word],
                'word': word
            }
        
        # 2. Check ordinal numbers
        if word in self.ordinals:
            logger.info(f"Found ordinal number: {word}")
            return {
                'ambiguous': False,
                'data': self.ordinals[word],
                'word': word
            }
        
        # 3. Check irregular verbs - both infinitive and all forms
        if word in self.irregular_verbs:
            # Direct infinitive match
            verb_data = self.irregular_verbs[word]
            logger.info(f"Found irregular verb (infinitive): {word}")
            formatted = self._format_irregular_verb(verb_data)
            return {
                'ambiguous': False,
                'data': formatted,
                'word': word
            }
        
        if word in self.irregular_forms_lookup:
            # Found as an inflected form
            matches = self.irregular_forms_lookup[word]
            if len(matches) == 1:
                # Single match - return the verb
                verb_data = matches[0]['verb_data']
                logger.info(f"Found irregular verb form '{word}' ({matches[0]['form_type']}) -> {verb_data['infinitive']}")
                formatted = self._format_irregular_verb(verb_data)
                return {
                    'ambiguous': False,
                    'data': formatted,
                    'word': verb_data['infinitive']  # Return infinitive as the word
                }
            else:
                # Multiple matches - treat as ambiguous
                meanings = []
                for match in matches:
                    verb_data = match['verb_data']
                    meanings.append(self._format_irregular_verb(verb_data))
                logger.info(f"Found ambiguous irregular verb form '{word}' with {len(matches)} meanings")
                return {
                    'ambiguous': True,
                    'meanings': meanings,
                    'word': word
                }
        
        # 4. Check strong verbs (legacy)
        if word in self.strong_verbs:
            logger.info(f"Found strong/modal verb: {word}")
            return {
                'ambiguous': False,
                'data': self.strong_verbs[word],
                'word': word
            }
        
        # Check if word is a form of a strong verb
        for verb_infinitive, verb_data in self.strong_verbs.items():
            if 'forms' in verb_data:
                forms = verb_data['forms']
                if word in forms.values():
                    logger.info(f"Found strong verb form '{word}' -> {verb_infinitive}")
                    return {
                        'ambiguous': False,
                        'data': verb_data,
                        'word': verb_infinitive
                    }
        
        # 5. Check main SALDO dictionary
        if word in self.data:
            logger.info(f"Found word in SALDO: {word}")
            return {
                'ambiguous': False,
                'data': self.data[word],
                'word': word
            }
        
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

    def format_word_card(self, word_data: Dict[str, Any], word: str) -> str:
        """
        Format word data into a Telegram-formatted card.
        
        Args:
            word_data: Dictionary containing word information.
            word: The word being displayed.
            
        Returns:
            Formatted string for Telegram message.
        """
        word_type = word_data.get('type', 'unknown')
        
        # Start with word and type
        card = f"🔤 *{word.upper()}*\n"
        card += f"📚 _{word_type.capitalize()}_\n"
        
        # Add group/category if available
        if 'group' in word_data:
            card += f"📂 {word_data['group']}\n"
        
        card += "\n"
        
        # Format based on word type
        if word_type == 'noun':
            card += self._format_noun(word_data)
        elif word_type == 'verb':
            card += self._format_verb(word_data)
        elif word_type == 'adjective':
            card += self._format_adjective(word_data)
        elif word_type == 'numeral':
            card += self._format_numeral(word_data)
        else:
            card += self._format_other(word_data)
        
        # Add description if available
        if 'description' in word_data:
            card += f"\n📝 _{word_data['description']}_\n"
        
        return card

    def _format_noun(self, word_data: Dict[str, Any]) -> str:
        """Format noun information."""
        forms = word_data.get('forms', [])
        gender = word_data.get('gender', '—')
        
        card = f"*Gender:* {gender}\n\n"
        
        if isinstance(forms, list) and len(forms) >= 4:
            card += "*Forms:*\n"
            card += f"• Singular indefinite: _{forms[0]}_\n"
            card += f"• Singular definite: _{forms[1]}_\n"
            card += f"• Plural indefinite: _{forms[2]}_\n"
            card += f"• Plural definite: _{forms[3]}_\n"
        elif forms:
            card += f"*Forms:* {forms}\n"
        
        return card

    def _format_verb(self, word_data: Dict[str, Any]) -> str:
        """Format verb information."""
        forms = word_data.get('forms', {})
        
        if isinstance(forms, dict):
            card = "*Forms:*\n"
            if 'infinitive' in forms:
                card += f"• Infinitive: _{forms.get('infinitive', '—')}_\n"
            if 'present' in forms:
                card += f"• Present: _{forms.get('present', '—')}_\n"
            if 'past' in forms:
                card += f"• Past: _{forms.get('past', '—')}_\n"
            if 'supine' in forms:
                card += f"• Supine: _{forms.get('supine', '—')}_\n"
            if 'imperative' in forms:
                card += f"• Imperative: _{forms.get('imperative', '—')}_\n"
            if 'past_participle' in forms:
                card += f"• Past participle: _{forms.get('past_participle', '—')}_\n"
            
            # Add passive forms if present
            if 'passive_infinitive' in forms:
                card += "\n*Passive forms:*\n"
                card += f"• Passive infinitive: _{forms.get('passive_infinitive', '—')}_\n"
            if 'passive_present' in forms:
                card += f"• Passive present: _{forms.get('passive_present', '—')}_\n"
            if 'passive_past' in forms:
                card += f"• Passive past: _{forms.get('passive_past', '—')}_\n"
        else:
            card = f"*Forms:* {forms}\n"
        
        return card

    def _format_adjective(self, word_data: Dict[str, Any]) -> str:
        """Format adjective information."""
        forms = word_data.get('forms', {})
        
        if isinstance(forms, dict):
            card = "*Forms:*\n"
            if 'en_form' in forms:
                card += f"• En-form: _{forms.get('en_form', '—')}_\n"
            if 'ett_form' in forms:
                card += f"• Ett-form: _{forms.get('ett_form', '—')}_\n"
            if 'plural' in forms:
                card += f"• Plural: _{forms.get('plural', '—')}_\n"
            if 'comparative' in forms:
                card += f"• Comparative: _{forms.get('comparative', '—')}_\n"
            if 'superlative' in forms:
                card += f"• Superlative: _{forms.get('superlative', '—')}_\n"
        elif isinstance(forms, list) and len(forms) >= 3:
            card = "*Forms:*\n"
            card += f"• En-form: _{forms[0]}_\n"
            card += f"• Ett-form: _{forms[1]}_\n"
            card += f"• Plural/definite: _{forms[2]}_\n"
            if len(forms) > 3:
                card += f"• Comparative: _{forms[3]}_\n"
            if len(forms) > 4:
                card += f"• Superlative: _{forms[4]}_\n"
        else:
            card = f"*Forms:* {forms}\n"
        
        return card

    def _format_numeral(self, word_data: Dict[str, Any]) -> str:
        """Format numeral information."""
        card = f"*Cardinal:* _{word_data.get('cardinal', '—')}_\n"
        card += f"*Ordinal:* _{word_data.get('ordinal', '—')}_\n"
        return card

    def _format_other(self, word_data: Dict[str, Any]) -> str:
        """Format other word types."""
        return f"*Base form:* _{word_data.get('word', '—')}_\n"

    def get_suggestions(self, partial: str, limit: int = 5) -> List[str]:
        """
        Get word suggestions for a misspelled word.
        
        Args:
            partial: The word to get suggestions for.
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
