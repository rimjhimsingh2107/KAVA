'use client';

import { useState, useCallback } from 'react';
import { getApiUrl } from '@/config/api';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import axios from 'axios';

interface DocumentUploadProps {
  onNext: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function DocumentUpload({ onNext, onDataUpdate, claimData }: DocumentUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [processedDocs, setProcessedDocs] = useState<any[]>([]);
  const [claimInfo, setClaimInfo] = useState({
    policyNumber: '',
    claimantName: '',
    incidentDate: '',
    propertyAddress: '',
    estimatedDamage: '',
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setProcessedDocs(prev => prev.filter((_, i) => i !== index));
  };

  const processDocuments = async () => {
    if (files.length === 0) {
      toast.error('Please upload at least one document');
      return;
    }

    if (!claimInfo.policyNumber || !claimInfo.claimantName || !claimInfo.incidentDate) {
      toast.error('Please fill in all required claim information');
      return;
    }

    setUploading(true);
    const processed = [];

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('files', file);

        const response = await axios.post(getApiUrl('/api/upload-documents'), formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        processed.push(...response.data.documents);
      }

      setProcessedDocs(processed);
      
      // Update claim data with processed documents and claim info
      onDataUpdate({
        documents: processed,
        claimInfo: {
          ...claimInfo,
          incidentDate: new Date(claimInfo.incidentDate).toISOString(),
        },
      });

      toast.success('Documents processed successfully!');
      onNext();
    } catch (error) {
      console.error('Error processing documents:', error);
      toast.error('Failed to process documents. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Documents</h2>
        <p className="text-gray-600">
          Upload your insurance policy, damage photos, receipts, and any other relevant documents.
        </p>
      </div>

      {/* Claim Information Form */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Claim Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Policy Number *
            </label>
            <input
              type="text"
              value={claimInfo.policyNumber}
              onChange={(e) => setClaimInfo(prev => ({ ...prev, policyNumber: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter policy number"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Claimant Name *
            </label>
            <input
              type="text"
              value={claimInfo.claimantName}
              onChange={(e) => setClaimInfo(prev => ({ ...prev, claimantName: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your full name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Incident Date *
            </label>
            <input
              type="date"
              value={claimInfo.incidentDate}
              onChange={(e) => setClaimInfo(prev => ({ ...prev, incidentDate: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Property Address
            </label>
            <input
              type="text"
              value={claimInfo.propertyAddress}
              onChange={(e) => setClaimInfo(prev => ({ ...prev, propertyAddress: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter property address"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Damage Amount
            </label>
            <input
              type="number"
              value={claimInfo.estimatedDamage}
              onChange={(e) => setClaimInfo(prev => ({ ...prev, estimatedDamage: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter estimated damage amount"
            />
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              Drag & drop files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports: JPG, PNG, PDF (max 10MB each)
            </p>
          </div>
        )}
      </div>

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900">Uploaded Files</h4>
          {files.map((file, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <File className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="text-red-500 hover:text-red-700"
              >
                <X className="h-5 w-5" />
              </button>
            </motion.div>
          ))}
        </div>
      )}

      {/* Process Documents Button */}
      <div className="flex justify-end">
        <button
          onClick={processDocuments}
          disabled={uploading || files.length === 0}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <CheckCircle className="h-4 w-4" />
              <span>Process Documents</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
