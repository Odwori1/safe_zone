import { z } from 'zod';

export const postCreateSchema = z.object({
  content: z.string().min(1, 'Content is required').max(5000, 'Content too long'),
  content_type: z.enum(['text', 'journal', 'audio', 'video']).default('text'),
  mood: z.string().max(50, 'Mood too long').optional(),
  visibility: z.enum(['public', 'private', 'support_group']).default('public'),
  is_anonymous: z.boolean().default(false),
  audio_url: z.string().max(500).optional(),
  audio_duration: z.number().min(1).max(3600).optional(),
  file_size: z.number().min(1).optional(),
  mime_type: z.string().max(100).optional(),
  video_url: z.string().max(500).optional(),
  video_duration: z.number().min(1).max(3600).optional(),
  thumbnail_url: z.string().max(500).optional(),
  video_width: z.number().min(1).max(3840).optional(),
  video_height: z.number().min(1).max(2160).optional(),
});

export type PostCreateFormData = z.infer<typeof postCreateSchema>;
