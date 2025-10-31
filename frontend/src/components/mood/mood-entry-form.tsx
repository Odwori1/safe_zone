'use client';

import { useState } from 'react';
import { useMoodStore } from '@/stores/mood-store';
import { MOOD_CATEGORIES, type MoodCategory } from '@/types/mood';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

export function MoodEntryForm() {
  const { createMood, loading, error } = useMoodStore();
  const [selectedMood, setSelectedMood] = useState('');
  const [intensity, setIntensity] = useState(5);
  const [notes, setNotes] = useState('');
  const [triggers, setTriggers] = useState('');
  const [activities, setActivities] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<MoodCategory | 'all'>('all');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedMood) {
      alert('Please select a mood');
      return;
    }

    await createMood({
      mood: selectedMood,
      intensity,
      notes: notes || undefined,
      triggers: triggers ? triggers.split(',').map(t => t.trim()).filter(t => t) : [],
      activities: activities ? activities.split(',').map(a => a.trim()).filter(a => a) : [],
    });

    // Reset form on success
    if (!error) {
      setSelectedMood('');
      setIntensity(5);
      setNotes('');
      setTriggers('');
      setActivities('');
    }
  };

  const filteredCategories = selectedCategory === 'all' 
    ? Object.values(MOOD_CATEGORIES)
    : [MOOD_CATEGORIES[selectedCategory]];

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <h2 className="text-xl font-bold mb-4">Track Your Mood</h2>
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Category Filter */}
        <div>
          <Label htmlFor="category" className="block text-sm font-medium mb-2">
            Filter by Category
          </Label>
          <select
            id="category"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as MoodCategory | 'all')}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Categories</option>
            {Object.values(MOOD_CATEGORIES).map(category => (
              <option key={category.name} value={category.name}>
                {category.label}
              </option>
            ))}
          </select>
        </div>

        {/* Mood Selection */}
        <div>
          <Label htmlFor="mood" className="block text-sm font-medium mb-2">
            How are you feeling?
          </Label>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-60 overflow-y-auto">
            {filteredCategories.map(category => (
              <div key={category.name} className="space-y-2">
                <div 
                  className="text-xs font-medium px-2 py-1 rounded text-white"
                  style={{ backgroundColor: category.color }}
                >
                  {category.label}
                </div>
                {category.moods.map(mood => (
                  <button
                    key={mood}
                    type="button"
                    onClick={() => setSelectedMood(mood)}
                    className={`w-full text-left p-2 text-sm rounded border transition-colors ${
                      selectedMood === mood
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {mood}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Intensity Slider */}
        <div>
          <Label htmlFor="intensity" className="block text-sm font-medium mb-2">
            Intensity: {intensity}/10
          </Label>
          <input
            type="range"
            id="intensity"
            min="1"
            max="10"
            value={intensity}
            onChange={(e) => setIntensity(Number(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Very Low</span>
            <span>Neutral</span>
            <span>Very High</span>
          </div>
        </div>

        {/* Notes */}
        <div>
          <Label htmlFor="notes" className="block text-sm font-medium mb-2">
            Notes (Optional)
          </Label>
          <Textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any additional thoughts about how you're feeling..."
            rows={3}
          />
        </div>

        {/* Triggers */}
        <div>
          <Label htmlFor="triggers" className="block text-sm font-medium mb-2">
            Triggers (Optional)
          </Label>
          <input
            type="text"
            id="triggers"
            value={triggers}
            onChange={(e) => setTriggers(e.target.value)}
            placeholder="What triggered this mood? (comma separated)"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Activities */}
        <div>
          <Label htmlFor="activities" className="block text-sm font-medium mb-2">
            Activities (Optional)
          </Label>
          <input
            type="text"
            id="activities"
            value={activities}
            onChange={(e) => setActivities(e.target.value)}
            placeholder="What were you doing? (comma separated)"
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          disabled={loading || !selectedMood}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Logging Mood...' : 'Log Mood'}
        </Button>
      </form>
    </div>
  );
}
