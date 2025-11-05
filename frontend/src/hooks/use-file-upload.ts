import { useState } from 'react';
import { apiClient } from '@/lib/api-client';

interface FileUploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
  uploadUrl: string | null;
  fileId: string | null;
}

interface UseFileUploadReturn {
  uploadState: FileUploadState;
  uploadFile: (
    file: File,
    fileType: 'audio' | 'video' | 'image' | 'document'
  ) => Promise<{ fileId: string; url: string }>;
  resetUpload: () => void;
}

export const useFileUpload = (): UseFileUploadReturn => {
  const [uploadState, setUploadState] = useState<FileUploadState>({
    isUploading: false,
    progress: 0,
    error: null,
    uploadUrl: null,
    fileId: null,
  });

  const uploadFile = async (
    file: File,
    fileType: 'audio' | 'video' | 'image' | 'document'
  ) => {
    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
      uploadUrl: null,
      fileId: null,
    });

    try {
      console.log('📤 Starting file upload process:', {
        name: file.name,
        size: file.size,
        type: file.type,
        fileType,
      });

      // ADDED: Check authentication before proceeding
      if (!apiClient.isAuthenticated()) {
        throw new Error('Please log in to upload files');
      }

      // 1. Get presigned URL from backend
      console.log('🔄 Requesting presigned URL...');
      const uploadInfo = await apiClient.uploadFile({
        file_name: file.name,
        original_filename: file.name,
        file_size: file.size,
        mime_type: file.type,
        file_type: fileType,
      });

      console.log('✅ Upload info received:', uploadInfo);

      if (!uploadInfo.upload_url) {
        throw new Error('No upload URL received from server');
      }

      // Construct full upload URL
      const fullUploadUrl = `http://localhost:8001${uploadInfo.upload_url}`;
      console.log('🔗 Full upload URL:', fullUploadUrl);

      // 2. Upload file using FormData with authentication
      console.log('🔄 Uploading file using FormData with auth...');

      const formData = new FormData();
      formData.append('file', file);

      // Get the authentication token
      const token = apiClient.getAccessToken();
      console.log('🔐 Authentication token available:', !!token);

      const uploadResponse = await fetch(fullUploadUrl, {
        method: 'POST',
        headers: {
          // Include authorization header for authentication
          ...(token && { 'Authorization': `Bearer ${token}` }),
          // Don't set Content-Type - let browser set it with boundary for FormData
        },
        body: formData,
      });

      console.log('📥 Upload response status:', uploadResponse.status);

      if (!uploadResponse.ok) {
        let errorText;
        try {
          const errorData = await uploadResponse.json();
          errorText = errorData.detail || JSON.stringify(errorData);
        } catch {
          errorText = await uploadResponse.text();
        }

        console.error('❌ Upload failed:', {
          status: uploadResponse.status,
          statusText: uploadResponse.statusText,
          error: errorText
        });

        throw new Error(`Upload failed: ${uploadResponse.status} - ${errorText}`);
      }

      const uploadResult = await uploadResponse.json();
      console.log('✅ File upload successful:', uploadResult);

      // Construct the file access URL for use in posts
      const fileAccessUrl = `http://localhost:8001${uploadResult.file_url}`;

      setUploadState({
        isUploading: false,
        progress: 100,
        error: null,
        uploadUrl: fileAccessUrl,
        fileId: uploadInfo.file_id,
      });

      return {
        fileId: uploadInfo.file_id,
        url: fileAccessUrl
      };

    } catch (error) {
      console.error('❌ File upload error:', error);

      let errorMessage = 'Upload failed';
      if (error instanceof Error) {
        errorMessage = error.message;
        
        // ADDED: Specific error message for authentication issues
        if (errorMessage.includes('403') || errorMessage.includes('Not authenticated')) {
          errorMessage = 'Please log in to upload files';
        }
      }

      setUploadState((prev) => ({
        ...prev,
        isUploading: false,
        error: errorMessage
      }));

      throw error;
    }
  };

  const resetUpload = () => {
    setUploadState({
      isUploading: false,
      progress: 0,
      error: null,
      uploadUrl: null,
      fileId: null,
    });
  };

  return {
    uploadState,
    uploadFile,
    resetUpload,
  };
};
