'use client';

import { useState, useEffect } from 'react';
import { useJournalsStore } from '@/stores/journals-store';
import { JournalPrompt } from '@/types/journals';
import { Sparkles, Loader2, Shuffle } from 'lucide-react';

export default function JournalPrompts() {
  const { getPrompts, prompts, isLoading } = useJournalsStore();
  const [selectedPrompt, setSelectedPrompt] = useState<JournalPrompt | null>(null);
  const [showPrompts, setShowPrompts] = useState(false);

  useEffect(() => {
    if (showPrompts && prompts.length === 0) {
      getPrompts();
    }
  }, [showPrompts, prompts.length, getPrompts]);

  const getRandomPrompt = () => {
    if (prompts.length > 0) {
      const randomIndex = Math.floor(Math.random() * prompts.length);
      setSelectedPrompt(prompts[randomIndex]);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!showPrompts) {
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            <h3 className="font-semibold text-lg">Need Inspiration?</h3>
          </div>
          <button
            onClick={() => setShowPrompts(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Show Prompts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-600" />
          <h3 className="font-semibold text-lg">Writing Prompts</h3>
        </div>
        <button
          onClick={() => setShowPrompts(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          Hide
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
          <span className="ml-2 text-gray-600">Loading prompts...</span>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Random Prompt Section */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-purple-800">Today's Prompt</h4>
              <button
                onClick={getRandomPrompt}
                className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700"
              >
                <Shuffle className="h-4 w-4" />
                Shuffle
              </button>
            </div>
            {selectedPrompt ? (
              <div>
                <p className="text-purple-700 mb-2">{selectedPrompt.prompt_text}</p>
                <div className="flex gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(selectedPrompt.difficulty_level)}`}>
                    {selectedPrompt.difficulty_level}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                    {selectedPrompt.category}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-purple-600 text-sm">Click shuffle to get a random prompt</p>
            )}
          </div>

          {/* All Prompts List */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">All Prompts</h4>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {prompts.map((prompt) => (
                <div
                  key={prompt.id}
                  className="p-3 border border-gray-200 rounded-lg hover:border-purple-300 transition-colors cursor-pointer"
                  onClick={() => setSelectedPrompt(prompt)}
                >
                  <p className="text-gray-800 text-sm mb-2">{prompt.prompt_text}</p>
                  <div className="flex gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(prompt.difficulty_level)}`}>
                      {prompt.difficulty_level}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                      {prompt.category}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
