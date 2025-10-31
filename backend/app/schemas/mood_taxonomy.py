"""
Professional Mental Health Mood Taxonomy
Based on clinical psychology and affect theory
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

class MoodCategory(str, Enum):
    """Clinical mood categories"""
    POSITIVE_HIGH_ENERGY = "positive_high_energy"
    POSITIVE_LOW_ENERGY = "positive_low_energy" 
    NEGATIVE_HIGH_ENERGY = "negative_high_energy"
    NEGATIVE_LOW_ENERGY = "negative_low_energy"
    NEUTRAL_STATES = "neutral_states"
    MIXED_STATES = "mixed_states"
    CLINICAL_STATES = "clinical_states"

class ProfessionalMood(str, Enum):
    """Comprehensive professional mood vocabulary"""
    
    # Positive High Energy
    JOYFUL = "joyful"
    EXCITED = "excited"
    ENTHUSIASTIC = "enthusiastic"
    ENERGETIC = "energetic"
    EUPHORIC = "euphoric"
    INSPIRED = "inspired"
    MOTIVATED = "motivated"
    CONFIDENT = "confident"
    PROUD = "proud"
    ACCOMPLISHED = "accomplished"
    OPTIMISTIC = "optimistic"
    HOPEFUL = "hopeful"
    DETERMINED = "determined"
    
    # Positive Low Energy
    CALM = "calm"
    PEACEFUL = "peaceful"
    CONTENT = "content"
    SERENE = "serene"
    RELAXED = "relaxed"
    GRATEFUL = "grateful"
    APPRECIATIVE = "appreciative"
    SATISFIED = "satisfied"
    FULFILLED = "fulfilled"
    BALANCED = "balanced"
    
    # Negative High Energy
    ANXIOUS = "anxious"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    IRRITATED = "irritated"
    AGITATED = "agitated"
    STRESSED = "stressed"
    OVERWHELMED = "overwhelmed"
    PANICKED = "panicked"
    RESTLESS = "restless"
    TENSE = "tense"
    
    # Negative Low Energy
    SAD = "sad"
    DEPRESSED = "depressed"
    LONELY = "lonely"
    EMPTY = "empty"
    HOPELESS = "hopeless"
    FATIGUED = "fatigued"
    EXHAUSTED = "exhausted"
    NUMB = "numb"
    APATHETIC = "apathetic"
    WITHDRAWN = "withdrawn"
    
    # Neutral States
    NEUTRAL = "neutral"
    FOCUSED = "focused"
    PRESENT = "present"
    MINDFUL = "mindful"
    CONTEMPLATIVE = "contemplative"
    REFLECTIVE = "reflective"
    CURIOUS = "curious"
    OBSERVANT = "observant"
    
    # Mixed States
    BITTERSWEET = "bittersweet"
    NOSTALGIC = "nostalgic"
    MELANCHOLIC = "melancholic"
    CONFLICTED = "conflicted"
    AMBIVALENT = "ambivalent"
    UNCERTAIN = "uncertain"
    VULNERABLE = "vulnerable"
    SENSITIVE = "sensitive"
    
    # Clinical States (use with caution)
    DISSOCIATED = "dissociated"
    TRIGGERED = "triggered"
    MANIC = "manic"
    HYPOMANIC = "hypomanic"
    PARANOID = "paranoid"
    OBSESSIVE = "obsessive"
    COMPULSIVE = "compulsive"

# Mood categorization mapping
MOOD_CATEGORIES: Dict[ProfessionalMood, MoodCategory] = {
    # Positive High Energy
    ProfessionalMood.JOYFUL: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.EXCITED: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.ENTHUSIASTIC: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.ENERGETIC: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.EUPHORIC: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.INSPIRED: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.MOTIVATED: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.CONFIDENT: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.PROUD: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.ACCOMPLISHED: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.OPTIMISTIC: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.HOPEFUL: MoodCategory.POSITIVE_HIGH_ENERGY,
    ProfessionalMood.DETERMINED: MoodCategory.POSITIVE_HIGH_ENERGY,
    
    # Positive Low Energy
    ProfessionalMood.CALM: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.PEACEFUL: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.CONTENT: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.SERENE: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.RELAXED: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.GRATEFUL: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.APPRECIATIVE: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.SATISFIED: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.FULFILLED: MoodCategory.POSITIVE_LOW_ENERGY,
    ProfessionalMood.BALANCED: MoodCategory.POSITIVE_LOW_ENERGY,
    
    # Negative High Energy
    ProfessionalMood.ANXIOUS: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.ANGRY: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.FRUSTRATED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.IRRITATED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.AGITATED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.STRESSED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.OVERWHELMED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.PANICKED: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.RESTLESS: MoodCategory.NEGATIVE_HIGH_ENERGY,
    ProfessionalMood.TENSE: MoodCategory.NEGATIVE_HIGH_ENERGY,
    
    # Negative Low Energy
    ProfessionalMood.SAD: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.DEPRESSED: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.LONELY: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.EMPTY: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.HOPELESS: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.FATIGUED: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.EXHAUSTED: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.NUMB: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.APATHETIC: MoodCategory.NEGATIVE_LOW_ENERGY,
    ProfessionalMood.WITHDRAWN: MoodCategory.NEGATIVE_LOW_ENERGY,
    
    # Neutral States
    ProfessionalMood.NEUTRAL: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.FOCUSED: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.PRESENT: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.MINDFUL: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.CONTEMPLATIVE: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.REFLECTIVE: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.CURIOUS: MoodCategory.NEUTRAL_STATES,
    ProfessionalMood.OBSERVANT: MoodCategory.NEUTRAL_STATES,
    
    # Mixed States
    ProfessionalMood.BITTERSWEET: MoodCategory.MIXED_STATES,
    ProfessionalMood.NOSTALGIC: MoodCategory.MIXED_STATES,
    ProfessionalMood.MELANCHOLIC: MoodCategory.MIXED_STATES,
    ProfessionalMood.CONFLICTED: MoodCategory.MIXED_STATES,
    ProfessionalMood.AMBIVALENT: MoodCategory.MIXED_STATES,
    ProfessionalMood.UNCERTAIN: MoodCategory.MIXED_STATES,
    ProfessionalMood.VULNERABLE: MoodCategory.MIXED_STATES,
    ProfessionalMood.SENSITIVE: MoodCategory.MIXED_STATES,
    
    # Clinical States
    ProfessionalMood.DISSOCIATED: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.TRIGGERED: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.MANIC: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.HYPOMANIC: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.PARANOID: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.OBSESSIVE: MoodCategory.CLINICAL_STATES,
    ProfessionalMood.COMPULSIVE: MoodCategory.CLINICAL_STATES,
}

# Clinical insights and recommendations
CLINICAL_INSIGHTS: Dict[MoodCategory, Dict[str, any]] = {
    MoodCategory.POSITIVE_HIGH_ENERGY: {
        "energy_level": "high",
        "valence": "positive",
        "recommendations": [
            "Channel energy into productive activities",
            "Share positive energy with others",
            "Set meaningful goals"
        ]
    },
    MoodCategory.POSITIVE_LOW_ENERGY: {
        "energy_level": "low", 
        "valence": "positive",
        "recommendations": [
            "Practice mindfulness and presence",
            "Engage in gentle self-care",
            "Reflect on gratitude"
        ]
    },
    MoodCategory.NEGATIVE_HIGH_ENERGY: {
        "energy_level": "high",
        "valence": "negative", 
        "recommendations": [
            "Practice grounding techniques",
            "Use physical activity to release tension",
            "Try deep breathing exercises"
        ]
    },
    MoodCategory.NEGATIVE_LOW_ENERGY: {
        "energy_level": "low",
        "valence": "negative",
        "recommendations": [
            "Reach out to support network",
            "Set small, achievable goals",
            "Consider professional support if persistent"
        ]
    },
    MoodCategory.NEUTRAL_STATES: {
        "energy_level": "variable",
        "valence": "neutral", 
        "recommendations": [
            "Maintain balanced routines",
            "Practice mindfulness",
            "Engage in reflective activities"
        ]
    },
    MoodCategory.MIXED_STATES: {
        "energy_level": "variable",
        "valence": "mixed",
        "recommendations": [
            "Practice self-compassion",
            "Explore conflicting feelings through journaling",
            "Allow space for complex emotions"
        ]
    },
    MoodCategory.CLINICAL_STATES: {
        "energy_level": "variable", 
        "valence": "clinical",
        "recommendations": [
            "Consider professional mental health support",
            "Use crisis resources if needed",
            "Practice safety planning"
        ]
    }
}

def get_mood_category(mood: str) -> Optional[MoodCategory]:
    """Get the clinical category for a mood"""
    try:
        professional_mood = ProfessionalMood(mood.lower())
        return MOOD_CATEGORIES.get(professional_mood)
    except ValueError:
        return None

def get_mood_insights(mood: str) -> Dict[str, any]:
    """Get clinical insights and recommendations for a mood"""
    category = get_mood_category(mood)
    if category and category in CLINICAL_INSIGHTS:
        return CLINICAL_INSIGHTS[category]
    return {
        "energy_level": "unknown",
        "valence": "unknown", 
        "recommendations": ["Continue self-observation"]
    }

def validate_professional_mood(mood: str) -> bool:
    """Validate if a mood is in the professional taxonomy"""
    try:
        ProfessionalMood(mood.lower())
        return True
    except ValueError:
        return False

def get_all_moods_by_category() -> Dict[MoodCategory, List[str]]:
    """Get all moods organized by category"""
    result = {}
    for mood, category in MOOD_CATEGORIES.items():
        if category not in result:
            result[category] = []
        result[category].append(mood.value)
    return result
