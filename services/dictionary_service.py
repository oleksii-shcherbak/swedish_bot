import json
import gzip
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SwedishDictionary:
    """Service for Swedish word lookups using SALDO dictionary."""

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
        
        # Load strong verbs
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

    def lookup(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Look up a word in the dictionary.

        Args:
            word: The word to look up (case-insensitive).

        Returns:
            Dictionary with lookup results or None if not found.
        """
        word = word.lower().strip()
        
        # Priority 1: Check strong verbs override first
        if word in self.strong_verbs:
            return {
                'ambiguous': False,
                'data': self.strong_verbs[word],
                'word': word
            }
        
        # Priority 2: Check if word is ambiguous
        if word in self.ambiguous_words:
            return {
                'ambiguous': True,
                'meanings': self.ambiguous_words[word],
                'word': word
            }
        
        # Priority 3: Normal dictionary lookup
        result = self.data.get(word)

        if result is None:
            return None

        return {'ambiguous': False, 'data': result, 'word': word}

    def format_word_card(self, word_data: Dict[str, Any], word: str) -> str:
        """
        Format word data as a Telegram message card.

        Args:
            word_data: Dictionary containing word information.
            word: The original word queried.

        Returns:
            Formatted string for Telegram message.
        """
        # Check if this is a word form
        if word_data.get('is_form'):
            return self._format_word_form(word_data, word)

        word_type = word_data.get('type', 'unknown')

        # Start with word header (removed separator line)
        card = f"📘 *{word.upper()}*\n\n"

        # Add word type
        type_emoji = self._get_type_emoji(word_type)
        card += f"{type_emoji} *Type:* {self._format_type_name(word_type)}\n"

        # Add group information if available
        if word_data.get('group') and word_data['group'] != word_type.capitalize():
            card += f"📚 *Group:* {word_data['group']}\n"

        card += "\n"

        # Format based on word type
        if word_type == 'noun':
            card += self._format_noun(word_data)
        elif word_type == 'verb':
            card += self._format_verb(word_data)
        elif word_type == 'adjective':
            card += self._format_adjective(word_data)
        elif word_type == 'adverb':
            card += self._format_adverb(word_data)
        elif word_type == 'pronoun':
            card += self._format_pronoun(word_data)
        elif word_type == 'proper_noun':
            card += self._format_proper_noun(word_data)
        elif word_type == 'numeral':
            card += self._format_numeral(word_data)
        else:
            card += self._format_other(word_data)

        return card

    def _format_word_form(self, word_data: Dict[str, Any], word: str) -> str:
        """Format a word form (conjugated verb, declined noun, etc.)."""
        base_word = word_data.get('base_word', '')
        form_type = word_data.get('form_type', '')
        word_type = word_data.get('type', 'unknown')

        # Start with form header (removed separator line)
        card = f"📘 *{word.upper()}*\n\n"

        # Explain what form this is
        card += f"ℹ️ This is the *{form_type}* of _{base_word}_\n\n"

        # Add type and group info
        type_emoji = self._get_type_emoji(word_type)
        card += f"{type_emoji} *Type:* {self._format_type_name(word_type)}\n"

        if word_data.get('group'):
            card += f"📚 *Group:* {word_data['group']}\n"

        card += "\n"

        # Show full conjugation/declension
        if word_type == 'verb' and 'forms' in word_data:
            card += "*Full conjugation:*\n"
            forms = word_data['forms']
            card += f"• Infinitive: _att {forms.get('infinitive', '—')}_\n"
            card += f"• Present: _{forms.get('present', '—')}_\n"
            card += f"• Past: _{forms.get('past', '—')}_\n"
            card += f"• Supine: _{forms.get('supine', '—')}_\n"

        elif word_type == 'noun' and 'forms' in word_data:
            gender = word_data.get('gender', 'en')
            card += f"*Gender:* {gender}\n\n"
            card += "*Full declension:*\n"
            forms = word_data['forms']
            if isinstance(forms, list) and len(forms) >= 4:
                card += f"• Singular indefinite: _{gender} {forms[0]}_\n"
                card += f"• Singular definite: _{forms[1]}_\n"
                card += f"• Plural indefinite: _{forms[2] if forms[2] != '-' else 'no plural'}_\n"
                card += f"• Plural definite: _{forms[3] if forms[3] != '-' else 'no plural'}_\n"

        elif word_type == 'adjective' and 'forms' in word_data:
            card += "*Full forms:*\n"
            forms = word_data['forms']
            card += f"• En-form: _{forms.get('en_form', '—')}_\n"
            card += f"• Ett-form: _{forms.get('ett_form', '—')}_\n"
            card += f"• Plural/Definite: _{forms.get('plural', '—')}_\n"
            if forms.get('comparative'):
                card += f"• Comparative: _{forms.get('comparative', '—')}_\n"
            if forms.get('superlative'):
                card += f"• Superlative: _{forms.get('superlative', '—')}_\n"

        return card

    def _get_type_emoji(self, word_type: str) -> str:
        """Get emoji for word type."""
        emojis = {
            'noun': '📦',
            'verb': '🏃',
            'adjective': '🎨',
            'adverb': '🔄',
            'pronoun': '👤',
            'preposition': '📍',
            'conjunction': '🔗',
            'interjection': '❗',
            'proper_noun': '🏷️',
            'numeral': '🔢',
            'unknown': '❓'
        }
        return emojis.get(word_type, '📝')

    def _format_type_name(self, word_type: str) -> str:
        """Format type name for display."""
        type_names = {
            'noun': 'Noun (Substantiv)',
            'verb': 'Verb',
            'adjective': 'Adjective (Adjektiv)',
            'adverb': 'Adverb',
            'pronoun': 'Pronoun (Pronomen)',
            'preposition': 'Preposition',
            'conjunction': 'Conjunction (Konjunktion)',
            'interjection': 'Interjection',
            'proper_noun': 'Proper Noun (Egennamn)',
            'numeral': 'Numeral (Räkneord)',
            'unknown': 'Unknown'
        }
        return type_names.get(word_type, word_type.capitalize())

    def _format_noun(self, word_data: Dict[str, Any]) -> str:
        """Format noun information."""
        forms = word_data.get('forms', [])
        gender = word_data.get('gender', 'en')

        result = f"*Gender:* {gender}\n\n"

        if forms:
            if isinstance(forms, list):
                if len(forms) >= 4:
                    result += "*Declension:*\n"
                    result += f"• Singular indefinite: _{gender} {forms[0]}_\n"
                    result += f"• Singular definite: _{forms[1]}_\n"
                    result += f"• Plural indefinite: _{forms[2] if forms[2] != '-' else 'no plural'}_\n"
                    result += f"• Plural definite: _{forms[3] if forms[3] != '-' else 'no plural'}_\n"
                else:
                    result += f"*Base form:* _{forms[0] if forms else word_data.get('word', '—')}_\n"

        return result

    def _format_verb(self, word_data: Dict[str, Any]) -> str:
        """Format verb conjugation."""
        forms = word_data.get('forms', {})

        if not forms:
            return "*No conjugation data available*\n"

        if isinstance(forms, dict):
            result = "*Conjugation:*\n"
            result += f"• Infinitive: _att {forms.get('infinitive', '—')}_\n"
            if forms.get('present'):
                result += f"• Present: _{forms.get('present', '—')}_\n"
            if forms.get('past'):
                result += f"• Past: _{forms.get('past', '—')}_\n"
            if forms.get('supine'):
                result += f"• Supine: _{forms.get('supine', '—')}_\n"
        else:
            result = f"*Base form:* _{word_data.get('word', '—')}_\n"

        return result

    def _format_adjective(self, word_data: Dict[str, Any]) -> str:
        """Format adjective forms."""
        forms = word_data.get('forms', {})

        if not forms:
            return "*No form data available*\n"

        if isinstance(forms, dict):
            result = "*Forms:*\n"
            result += f"• En-form: _{forms.get('en_form', '—')}_\n"
            result += f"• Ett-form: _{forms.get('ett_form', '—')}_\n"
            result += f"• Plural/Definite: _{forms.get('plural', '—')}_\n"

            if 'comparative' in forms or 'superlative' in forms:
                result += "\n*Comparison:*\n"
                if forms.get('comparative'):
                    result += f"• Comparative: _{forms.get('comparative', '—')}_\n"
                if forms.get('superlative'):
                    result += f"• Superlative: _{forms.get('superlative', '—')}_\n"
        else:
            result = f"*Base form:* _{word_data.get('word', '—')}_\n"

        return result

    def _format_adverb(self, word_data: Dict[str, Any]) -> str:
        """Format adverb information."""
        return f"*Base form:* _{word_data.get('word', '—')}_\n"

    def _format_pronoun(self, word_data: Dict[str, Any]) -> str:
        """Format pronoun information."""
        return f"*Base form:* _{word_data.get('word', '—')}_\n"

    def _format_proper_noun(self, word_data: Dict[str, Any]) -> str:
        """Format proper noun information."""
        return "*Category:* Name or place\n"

    def _format_numeral(self, word_data: Dict[str, Any]) -> str:
        """Format numeral information."""
        word = word_data.get('word', '')
        
        card = "*Cardinal number*\n"
        
        # Add ordinal if available
        if word in self.ordinals:
            ordinal = self.ordinals[word]
            card += f"\n*Ordinal form:* _{ordinal}_\n"
        
        return card

    def _format_other(self, word_data: Dict[str, Any]) -> str:
        """Format other word types."""
        return f"*Base form:* _{word_data.get('word', '—')}_\n"

    def get_suggestions(self, partial: str, limit: int = 5) -> List[str]:
        """Get word suggestions for partial input."""
        partial = partial.lower().strip()
        suggestions = []

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
