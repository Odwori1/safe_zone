import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from app.database.database import database
from app.schemas.mood_taxonomy import get_mood_category, get_mood_insights

class CRUDMood:
    async def create(self, user_id: UUID, mood_in) -> Optional[asyncpg.Record]:
        """Create new mood entry"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                INSERT INTO mood_entries (
                    user_id, mood, intensity, notes, source_type, source_id,
                    triggers, activities, physical_symptoms, social_context,
                    sleep_quality, energy_level, location, weather,
                    duration_minutes, medication_taken, medication_notes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
                RETURNING *
                """,
                user_id, mood_in.mood, getattr(mood_in, 'intensity', None),
                getattr(mood_in, 'notes', None), getattr(mood_in, 'source_type', 'standalone'),
                getattr(mood_in, 'source_id', None), getattr(mood_in, 'triggers', []),
                getattr(mood_in, 'activities', []), getattr(mood_in, 'physical_symptoms', []),
                getattr(mood_in, 'social_context', None), getattr(mood_in, 'sleep_quality', None),
                getattr(mood_in, 'energy_level', None), getattr(mood_in, 'location', None),
                getattr(mood_in, 'weather', None), getattr(mood_in, 'duration_minutes', None),
                getattr(mood_in, 'medication_taken', False), getattr(mood_in, 'medication_notes', None)
            )

    async def create_from_post(self, user_id: UUID, post_id: UUID, mood: str, intensity: int, **kwargs):
        """Create mood entry from post"""
        mood_data = {'mood': mood, 'intensity': intensity, 'source_type': 'post', 'source_id': post_id, **kwargs}
        return await self.create(user_id, type('MoodIn', (), mood_data)())

    async def create_from_journal(self, user_id: UUID, journal_id: UUID, mood: str, intensity: int, **kwargs):
        """Create mood entry from journal"""
        mood_data = {'mood': mood, 'intensity': intensity, 'source_type': 'journal', 'source_id': journal_id, **kwargs}
        return await self.create(user_id, type('MoodIn', (), mood_data)())

    async def get(self, mood_id: UUID, user_id: UUID = None) -> Optional[asyncpg.Record]:
        """Get mood entry by ID"""
        async with database.pool.acquire() as conn:
            if user_id:
                await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow("SELECT * FROM mood_entries WHERE id = $1", mood_id)

    async def get_user_entries(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Get mood entries by user"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
                user_id, limit, offset
            )

    async def get_mood_entries_by_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> List[asyncpg.Record]:
        """Alias for get_user_entries"""
        return await self.get_user_entries(user_id, limit, offset)

    async def get_recent_entries(self, user_id: UUID, days: int) -> List[asyncpg.Record]:
        """Get recent mood entries"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2 ORDER BY created_at DESC",
                user_id, days
            )

    async def count_user_entries(self, user_id: UUID) -> int:
        """Count user's mood entries"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.fetchval("SELECT COUNT(*) FROM mood_entries WHERE user_id = $1", user_id)
            return result or 0

    async def update(self, mood_id: UUID, user_id: UUID, mood_in):
        """Update mood entry"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            return await conn.fetchrow(
                """
                UPDATE mood_entries SET mood = $1, intensity = $2, notes = $3, triggers = $4, activities = $5,
                physical_symptoms = $6, social_context = $7, sleep_quality = $8, energy_level = $9,
                location = $10, weather = $11, duration_minutes = $12, medication_taken = $13,
                medication_notes = $14, updated_at = NOW() WHERE id = $15 RETURNING *
                """,
                mood_in.mood, getattr(mood_in, 'intensity', None), getattr(mood_in, 'notes', None),
                getattr(mood_in, 'triggers', []), getattr(mood_in, 'activities', []),
                getattr(mood_in, 'physical_symptoms', []), getattr(mood_in, 'social_context', None),
                getattr(mood_in, 'sleep_quality', None), getattr(mood_in, 'energy_level', None),
                getattr(mood_in, 'location', None), getattr(mood_in, 'weather', None),
                getattr(mood_in, 'duration_minutes', None), getattr(mood_in, 'medication_taken', False),
                getattr(mood_in, 'medication_notes', None), mood_id
            )

    async def delete(self, mood_id: UUID, user_id: UUID) -> bool:
        """Delete mood entry"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            result = await conn.execute("DELETE FROM mood_entries WHERE id = $1", mood_id)
            return "DELETE 1" in result

    async def get_mood_stats(self, user_id: UUID, days: int) -> Dict[str, Any]:
        """Get mood statistics"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Get entries for the period
            entries = await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2",
                user_id, days
            )

            if not entries:
                return {
                    "total_entries": 0,
                    "average_intensity": 0,
                    "most_common_mood": None,
                    "mood_frequency": {},
                    "weekly_trend": [],
                    "source_distribution": [],
                    "top_triggers": [],
                    "top_activities": []
                }

            # Calculate statistics
            total_entries = len(entries)
            avg_intensity = sum(entry['intensity'] or 0 for entry in entries) / total_entries

            # Mood frequency
            mood_counts = {}
            for entry in entries:
                mood = entry['mood']
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            most_common_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else None

            # Source distribution
            source_counts = {}
            for entry in entries:
                source_type = entry['source_type'] or 'standalone'
                source_counts[source_type] = source_counts.get(source_type, 0) + 1
            source_distribution = [{"source_type": k, "count": v} for k, v in source_counts.items()]

            # Top triggers and activities
            trigger_counts = {}
            activity_counts = {}
            for entry in entries:
                for trigger in entry['triggers'] or []:
                    trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
                for activity in entry['activities'] or []:
                    activity_counts[activity] = activity_counts.get(activity, 0) + 1

            top_triggers = [{"trigger": k, "count": v} for k, v in sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
            top_activities = [{"activity": k, "count": v} for k, v in sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

            # Weekly trend (simplified)
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)

            weekly_data = []
            current_date = week_ago
            while current_date <= today:
                day_entries = [e for e in entries if e['created_at'].date() == current_date]
                if day_entries:
                    avg_day_intensity = sum(e['intensity'] or 0 for e in day_entries) / len(day_entries)
                    weekly_data.append({
                        "date": current_date.isoformat(),
                        "avg_intensity": round(avg_day_intensity, 1),
                        "entry_count": len(day_entries)
                    })
                current_date += timedelta(days=1)

            return {
                "total_entries": total_entries,
                "average_intensity": round(avg_intensity, 1),
                "most_common_mood": most_common_mood,
                "mood_frequency": mood_counts,
                "weekly_trend": weekly_data,
                "source_distribution": source_distribution,
                "top_triggers": top_triggers,
                "top_activities": top_activities
            }

    # Hybrid methods that return empty for now (to avoid errors)
    async def get_hybrid_entries(self, user_id: UUID, days: int) -> List[asyncpg.Record]:
        """Get hybrid entries - placeholder to avoid errors"""
        return []

    async def get_hybrid_entries_safe(self, user_id: UUID, days: int) -> List[asyncpg.Record]:
        """Get hybrid entries safe - placeholder to avoid errors"""
        return []

    async def get_hybrid_entries_raw(self, user_id: UUID, days: int) -> List[Dict[str, Any]]:
        """Get hybrid entries raw - placeholder to avoid errors"""
        return []

    async def get_enhanced_hybrid_entries(self, user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
        """
        ENHANCED HYBRID: Get mood entries with post/journal context using separate queries
        """
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))

            # Get basic mood entries
            mood_entries = await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2 ORDER BY created_at DESC",
                user_id, days
            )

            enhanced_entries = []
            for entry in mood_entries:
                entry_dict = dict(entry)
                source_type = entry_dict.get('source_type')
                source_id = entry_dict.get('source_id')

                # Add post context if applicable
                if source_type == 'post' and source_id:
                    try:
                        post = await conn.fetchrow(
                            "SELECT title, content FROM posts WHERE id = $1 AND user_id = $2",
                            source_id, user_id
                        )
                        if post:
                            entry_dict['post_title'] = post['title']
                            entry_dict['post_content'] = post['content']
                    except Exception:
                        pass  # Skip if post not found or error

                # Add journal context if applicable
                elif source_type == 'journal' and source_id:
                    try:
                        journal = await conn.fetchrow(
                            "SELECT title, content FROM journals WHERE id = $1 AND user_id = $2",
                            source_id, user_id
                        )
                        if journal:
                            entry_dict['journal_title'] = journal['title']
                            entry_dict['journal_content'] = journal['content']
                    except Exception:
                        pass  # Skip if journal not found or error

                enhanced_entries.append(entry_dict)

            return enhanced_entries

    async def get_clinical_insights(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get clinical insights from mood patterns"""
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            
            entries = await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2 ORDER BY created_at DESC",
                user_id, days
            )
            
            if len(entries) < 3:
                return {
                    "dominant_category": None,
                    "pattern_insights": ["Insufficient data for clinical analysis"],
                    "clinical_recommendations": ["Continue tracking moods regularly"],
                    "risk_factors": [],
                    "positive_patterns": []
                }
            
            # Analyze mood patterns
            category_counts = {}
            intensity_trend = []
            negative_streak = 0
            max_negative_streak = 0
            positive_days = 0
            negative_days = 0
            
            for entry in entries:
                # Categorize mood
                category = get_mood_category(entry['mood'])
                if category:
                    category_counts[category.value] = category_counts.get(category.value, 0) + 1
                
                # Track streaks
                if category and 'negative' in category.value:
                    negative_streak += 1
                    max_negative_streak = max(max_negative_streak, negative_streak)
                    negative_days += 1
                else:
                    negative_streak = 0
                    if category and 'positive' in category.value:
                        positive_days += 1
            
            # Generate insights
            insights = []
            recommendations = []
            risk_factors = []
            positive_patterns = []
            
            # Dominant category analysis
            dominant_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
            
            if dominant_category:
                if 'negative' in dominant_category:
                    insights.append(f"Predominantly {dominant_category.replace('_', ' ')} mood pattern")
                    if max_negative_streak >= 3:
                        risk_factors.append(f"Extended negative mood streak ({max_negative_streak} days)")
                        recommendations.append("Consider discussing patterns with mental health professional")
                elif 'positive' in dominant_category:
                    positive_patterns.append(f"Consistently {dominant_category.replace('_', ' ')} mood pattern")
                    insights.append("Strong positive mood foundation")
            
            # Ratio analysis
            total_days = len(entries)
            if total_days > 0:
                positive_ratio = positive_days / total_days
                negative_ratio = negative_days / total_days
                
                if negative_ratio > 0.7:
                    risk_factors.append("High frequency of negative moods")
                    recommendations.append("Explore mood triggers and coping strategies")
                elif positive_ratio > 0.7:
                    positive_patterns.append("High frequency of positive moods")
                    recommendations.append("Leverage positive patterns for wellbeing")
            
            # Default recommendations if none generated
            if not recommendations:
                recommendations = [
                    "Continue current self-care practices",
                    "Maintain regular mood tracking",
                    "Notice patterns between activities and moods"
                ]
            
            return {
                "dominant_category": dominant_category,
                "pattern_insights": insights,
                "clinical_recommendations": recommendations,
                "risk_factors": risk_factors,
                "positive_patterns": positive_patterns
            }

    async def get_enhanced_stats(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Get enhanced statistics with clinical insights"""
        basic_stats = await self.get_mood_stats(user_id, days)
        clinical_insights = await self.get_clinical_insights(user_id, days)
        
        # Add category distribution to basic stats
        async with database.pool.acquire() as conn:
            await conn.execute("SELECT set_current_user_id($1);", str(user_id))
            entries = await conn.fetch(
                "SELECT * FROM mood_entries WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '1 day' * $2",
                user_id, days
            )
            
            category_distribution = {}
            for entry in entries:
                category = get_mood_category(entry['mood'])
                if category:
                    category_distribution[category.value] = category_distribution.get(category.value, 0) + 1
        
        basic_stats['category_distribution'] = category_distribution
        basic_stats['clinical_insights'] = clinical_insights
        
        return basic_stats

    async def get_mood_taxonomy(self) -> Dict[str, Any]:
        """Get professional mood taxonomy"""
        from app.schemas.mood_taxonomy import get_all_moods_by_category, MoodCategory
        categories = get_all_moods_by_category()
        total_moods = sum(len(moods) for moods in categories.values())
        
        return {
            "categories": {category.value: moods for category, moods in categories.items()},
            "total_moods": total_moods
        }

mood_crud = CRUDMood()
