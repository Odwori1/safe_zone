// FILE: src/hooks/use-webrtc.ts
import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebRTCProps {
  roomId: string;
  onParticipantsUpdate?: (participants: any[]) => void;
}

export const useWebRTC = ({ roomId, onParticipantsUpdate }: UseWebRTCProps) => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<Map<string, MediaStream>>(new Map());
  const [isMuted, setIsMuted] = useState(true);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [participants, setParticipants] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map());
  const localStreamRef = useRef<MediaStream | null>(null);

  // Initialize WebSocket connection
  const connect = useCallback(async () => {
    try {
      // Get user media (microphone access)
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      localStreamRef.current = stream;
      setLocalStream(stream);
      
      // Start muted for privacy
      stream.getAudioTracks().forEach(track => {
        track.enabled = false;
      });
      setIsMuted(true);

      // Connect to WebSocket
      const token = localStorage.getItem('access_token');
      const wsUrl = `ws://localhost:8001/api/v1/audio/${roomId}/ws?token=${token}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

    } catch (error) {
      console.error('Failed to connect:', error);
      throw error;
    }
  }, [roomId]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'user.joined':
        handleUserJoined(data.user);
        break;
      case 'user.left':
        handleUserLeft(data.user_id);
        break;
      case 'user.presence':
        handleUserPresence(data.user_id, data.audio_enabled, data.is_speaking);
        break;
      case 'webrtc.offer':
        handleWebRTCOffer(data.from_user_id, data.offer);
        break;
      case 'webrtc.answer':
        handleWebRTCAnswer(data.from_user_id, data.answer);
        break;
      case 'ice.candidate':
        handleICECandidate(data.from_user_id, data.candidate);
        break;
      case 'participants.list':
        setParticipants(data.participants);
        onParticipantsUpdate?.(data.participants);
        break;
    }
  }, []);

  // WebRTC Handlers
  const handleUserJoined = useCallback(async (user: any) => {
    if (localStreamRef.current) {
      await createPeerConnection(user.id, localStreamRef.current);
    }
  }, []);

  const handleUserLeft = useCallback((userId: string) => {
    const pc = peerConnectionsRef.current.get(userId);
    if (pc) {
      pc.close();
      peerConnectionsRef.current.delete(userId);
    }
    
    setRemoteStreams(prev => {
      const newStreams = new Map(prev);
      newStreams.delete(userId);
      return newStreams;
    });

    setParticipants(prev => prev.filter(p => p.id !== userId));
  }, []);

  const createPeerConnection = useCallback(async (userId: string, localStream: MediaStream) => {
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    });

    // Add local stream
    localStream.getTracks().forEach(track => {
      pc.addTrack(track, localStream);
    });

    // Handle incoming stream
    pc.ontrack = (event) => {
      const remoteStream = event.streams[0];
      setRemoteStreams(prev => new Map(prev.set(userId, remoteStream)));
    };

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'ice.candidate',
          target_user_id: userId,
          candidate: event.candidate
        }));
      }
    };

    peerConnectionsRef.current.set(userId, pc);

    // Create and send offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'webrtc.offer',
        target_user_id: userId,
        offer: offer
      }));
    }
  }, []);

  const handleWebRTCOffer = useCallback(async (fromUserId: string, offer: any) => {
    const pc = peerConnectionsRef.current.get(fromUserId) || 
                await createPeerConnection(fromUserId, localStreamRef.current!);
    
    await pc.setRemoteDescription(offer);
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);

    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({
        type: 'webrtc.answer',
        target_user_id: fromUserId,
        answer: answer
      }));
    }
  }, []);

  const handleWebRTCAnswer = useCallback(async (fromUserId: string, answer: any) => {
    const pc = peerConnectionsRef.current.get(fromUserId);
    if (pc) {
      await pc.setRemoteDescription(answer);
    }
  }, []);

  const handleICECandidate = useCallback(async (fromUserId: string, candidate: any) => {
    const pc = peerConnectionsRef.current.get(fromUserId);
    if (pc) {
      await pc.addIceCandidate(candidate);
    }
  }, []);

  const handleUserPresence = useCallback((userId: string, audioEnabled: boolean, isSpeaking: boolean) => {
    setParticipants(prev => prev.map(p => 
      p.id === userId ? { ...p, audio_enabled: audioEnabled, is_speaking: isSpeaking } : p
    ));
  }, []);

  // Audio Controls
  const toggleMute = useCallback(() => {
    if (localStreamRef.current) {
      const audioTracks = localStreamRef.current.getAudioTracks();
      audioTracks.forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!audioTracks[0].enabled);

      // Notify other participants
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'user.presence',
          audio_enabled: audioTracks[0].enabled,
          is_speaking: false
        }));
      }
    }
  }, []);

  // Cleanup
  const disconnect = useCallback(() => {
    // Close all peer connections
    peerConnectionsRef.current.forEach(pc => pc.close());
    peerConnectionsRef.current.clear();

    // Stop local stream
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
      setLocalStream(null);
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setRemoteStreams(new Map());
    setParticipants([]);
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    localStream,
    remoteStreams,
    isMuted,
    isSpeaking,
    participants,
    isConnected,
    connect,
    disconnect,
    toggleMute
  };
};
