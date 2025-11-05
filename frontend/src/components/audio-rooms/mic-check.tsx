// FILE: src/components/audio-rooms/mic-check.tsx
'use client';
import { useState, useEffect, useRef } from 'react';

interface MicCheckProps {
  onClose: () => void;
  onContinue: () => void;
}

export default function MicCheck({ onClose, onContinue }: MicCheckProps) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [volume, setVolume] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const startMicTest = async () => {
    try {
      setError(null);
      
      // Request microphone access
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      setStream(mediaStream);
      
      // Set up audio context for volume analysis
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(mediaStream);
      const analyser = audioContext.createAnalyser();
      
      analyser.fftSize = 256;
      source.connect(analyser);
      
      analyserRef.current = analyser;
      setIsRecording(true);
      
      // Start volume monitoring
      monitorVolume();
      
      // Play audio feedback
      if (audioRef.current) {
        audioRef.current.srcObject = mediaStream;
      }
      
    } catch (err) {
      setError('Failed to access microphone. Please check your permissions.');
      console.error('Microphone access error:', err);
    }
  };

  const monitorVolume = () => {
    if (!analyserRef.current) return;
    
    const analyser = analyserRef.current;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    const checkVolume = () => {
      analyser.getByteFrequencyData(dataArray);
      
      // Calculate average volume
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const average = sum / dataArray.length;
      
      // Convert to percentage (0-100)
      const volumePercent = Math.min(100, (average / 255) * 100);
      setVolume(volumePercent);
      
      if (isRecording) {
        animationRef.current = requestAnimationFrame(checkVolume);
      }
    };
    
    checkVolume();
  };

  const stopMicTest = () => {
    setIsRecording(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setVolume(0);
  };

  const handleContinue = () => {
    stopMicTest();
    onContinue();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md dark:bg-gray-800">
        <h2 className="text-2xl font-bold mb-4 dark:text-white">Microphone Check</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400">
            {error}
          </div>
        )}
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4 dark:text-gray-400">
            Let's make sure your microphone is working properly before joining the room.
          </p>
          
          {/* Volume Meter */}
          <div className="bg-gray-200 rounded-full h-4 mb-2 overflow-hidden dark:bg-gray-700">
            <div 
              className="bg-green-500 h-full transition-all duration-100"
              style={{ width: `${volume}%` }}
            ></div>
          </div>
          
          <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
            <span>Silent</span>
            <span>Speak now...</span>
            <span>Loud</span>
          </div>
          
          <div className="mt-4 text-center">
            {volume > 30 ? (
              <div className="text-green-600 font-medium dark:text-green-400">
                ✅ Microphone is picking up sound!
              </div>
            ) : volume > 10 ? (
              <div className="text-yellow-600 font-medium dark:text-yellow-400">
                🎤 We can hear you, try speaking louder
              </div>
            ) : isRecording ? (
              <div className="text-gray-600 dark:text-gray-400">
                🔇 Speak into your microphone...
              </div>
            ) : null}
          </div>
        </div>

        {/* Hidden audio element for playback */}
        <audio ref={audioRef} muted autoPlay />
        
        <div className="flex justify-between gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
          
          {!isRecording ? (
            <button
              onClick={startMicTest}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Start Test
            </button>
          ) : (
            <button
              onClick={handleContinue}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            >
              Continue to Room
            </button>
          )}
        </div>
        
        {isRecording && (
          <button
            onClick={stopMicTest}
            className="w-full mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Stop Test
          </button>
        )}
        
        <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
          <p>💡 Tips:</p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Speak in a normal voice volume</li>
            <li>Ensure your microphone is not muted in system settings</li>
            <li>Close other applications that might use your microphone</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
