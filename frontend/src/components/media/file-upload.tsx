'use client';

import { useCallback, useState } from 'react';
import { useFileUpload } from '@/hooks/use-file-upload';
import { Upload, X, File, Music, Video, Image, FileText, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onFileUploaded: (fileInfo: { fileId: string; url: string; fileType: string }) => void;
  acceptedFileTypes?: string;
  maxFileSize?: number; // in bytes
  fileType: 'audio' | 'video' | 'image' | 'document';
}

export default function FileUpload({
  onFileUploaded,
  acceptedFileTypes,
  maxFileSize = 50 * 1024 * 1024, // 50MB default
  fileType,
}: FileUploadProps) {
  const { uploadState, uploadFile, resetUpload } = useFileUpload();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Get proper accepted file types for each file type
  const getAcceptedFileTypes = () => {
    switch (fileType) {
      case 'audio':
        return 'audio/*,.mp3,.wav,.ogg,.m4a,.aac';
      case 'video':
        return 'video/*,.mp4,.mov,.avi,.mkv,.webm';
      case 'image':
        return 'image/*,.jpg,.jpeg,.png,.gif,.webp,.bmp';
      case 'document':
        return '.pdf,.doc,.docx,.txt,.rtf';
      default:
        return '*';
    }
  };

  const getFileTypeIcon = (type: string) => {
    switch (type) {
      case 'audio':
        return <Music className="h-8 w-8 text-blue-600" />;
      case 'video':
        return <Video className="h-8 w-8 text-purple-600" />;
      case 'image':
        return <Image className="h-8 w-8 text-green-600" />;
      default:
        return <FileText className="h-8 w-8 text-gray-600" />;
    }
  };

  const getFileTypeText = (type: string) => {
    switch (type) {
      case 'audio':
        return 'Audio file (MP3, WAV, etc.)';
      case 'video':
        return 'Video file (MP4, MOV, etc.)';
      case 'image':
        return 'Image file (JPG, PNG, etc.)';
      default:
        return 'Document file (PDF, DOC, etc.)';
    }
  };

  const handleFile = async (file: File) => {
    console.log('📁 File selected:', {
      name: file.name,
      type: file.type,
      size: file.size,
      fileType: fileType
    });

    // Validate file size
    if (file.size > maxFileSize) {
      alert(`File size must be less than ${maxFileSize / 1024 / 1024}MB`);
      return;
    }

    // Validate file type
    const acceptedTypes = getAcceptedFileTypes().split(',');
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidType = acceptedTypes.some(type => {
      if (type.startsWith('.')) {
        return type === fileExtension;
      } else if (type.endsWith('/*')) {
        const category = type.split('/')[0];
        return file.type.startsWith(category + '/');
      }
      return file.type === type;
    });

    if (!isValidType) {
      alert(`Please select a valid ${fileType} file. Accepted types: ${acceptedTypes.join(', ')}`);
      return;
    }

    setSelectedFile(file);

    try {
      console.log('🔄 Starting file upload...');
      const result = await uploadFile(file, fileType);
      console.log('✅ File upload successful:', result);
      onFileUploaded({
        fileId: result.fileId,
        url: result.url,
        fileType: fileType,
      });
    } catch (error) {
      console.error('❌ Upload failed:', error);
      // Don't show alert here - let the component display the error
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    resetUpload();
  };

  if (selectedFile) {
    return (
      <div className={`border-2 border-dashed rounded-lg p-4 ${
        uploadState.error ? 'border-red-300 bg-red-50' : 
        uploadState.fileId ? 'border-green-300 bg-green-50' :
        'border-blue-300 bg-blue-50'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getFileTypeIcon(fileType)}
            <div>
              <p className="font-medium text-sm text-gray-900">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {getFileTypeText(fileType)}
              </p>
            </div>
          </div>
          
          {!uploadState.isUploading && (
            <button
              onClick={removeFile}
              className="p-1 hover:bg-gray-200 rounded-full transition-colors"
              type="button"
            >
              <X className="h-4 w-4 text-gray-500" />
            </button>
          )}
        </div>

        {uploadState.isUploading && (
          <div className="mt-3">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadState.progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-1 text-center">
              Uploading... {Math.round(uploadState.progress)}%
            </p>
          </div>
        )}

        {uploadState.error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <p className="text-xs text-red-700 font-medium">Upload failed</p>
            </div>
            <p className="text-xs text-red-600 mt-1">{uploadState.error}</p>
            <button
              onClick={removeFile}
              className="text-xs text-red-600 hover:text-red-800 mt-1 font-medium"
              type="button"
            >
              Try again
            </button>
          </div>
        )}

        {uploadState.fileId && !uploadState.error && (
          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <p className="text-xs text-green-700 font-medium">Upload complete</p>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
        dragActive
          ? 'border-blue-400 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400 bg-gray-50'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        className="hidden"
        id={`file-upload-${fileType}`}
        accept={getAcceptedFileTypes()}
        onChange={handleChange}
      />

      <div className="flex flex-col items-center space-y-3">
        <Upload className="h-8 w-8 text-gray-400" />

        <div className="text-center">
          <label
            htmlFor={`file-upload-${fileType}`}
            className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium text-sm"
          >
            Choose a file
          </label>
          <p className="text-xs text-gray-500 mt-1">or drag and drop here</p>
        </div>

        <div className="text-xs text-gray-500 text-center">
          <p>{getFileTypeText(fileType)}</p>
          <p>Max size: {maxFileSize / 1024 / 1024}MB</p>
        </div>
      </div>
    </div>
  );
}
