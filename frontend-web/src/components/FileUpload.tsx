import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from './ui/Button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  selectedFile?: File | null;
  onClear: () => void;
  label?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, selectedFile, onClear, label }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={cn(
            "relative h-[200px] w-full rounded-3xl border-2 border-dashed transition-all duration-200 ease-in-out flex flex-col items-center justify-center gap-4 cursor-pointer",
            isDragging
              ? "border-[#007AFF] bg-blue-50/50 scale-[1.02]"
              : "border-gray-200 bg-white/50 hover:border-gray-300 hover:bg-white/80"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleFileInput}
          />
          <div className="p-4 rounded-full bg-white shadow-sm border border-gray-100">
            <UploadCloud className="w-8 h-8 text-[#007AFF]" />
          </div>
          <div className="text-center space-y-1">
            <p className="text-lg font-medium text-gray-900">
              {label || '将简历拖放到此处'}
            </p>
            <p className="text-sm text-gray-500">
              支持 PDF, DOCX, TXT 格式，最大 10MB
            </p>
          </div>
          <Button variant="secondary" size="sm" className="mt-2">
            选择文件
          </Button>
        </div>
      ) : (
        <div className="relative h-[100px] w-full rounded-3xl border border-gray-200 bg-white flex items-center px-6 gap-4 shadow-sm">
            <div className="p-3 rounded-xl bg-blue-50">
                <FileText className="w-6 h-6 text-[#007AFF]" />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                    {selectedFile.name}
                </p>
                <p className="text-xs text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
            </div>
            <button 
                onClick={onClear}
                className="p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
            >
                <X className="w-5 h-5" />
            </button>
        </div>
      )}
    </div>
  );
};
