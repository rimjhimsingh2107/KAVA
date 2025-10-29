'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, CheckCircle, AlertCircle, CreditCard, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface DocumentUploadStepProps {
  onNext: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

interface ReceiptSyncStatus {
  company: string;
  logo: string;
  status: 'pending' | 'syncing' | 'complete' | 'error';
  count?: number;
}

export default function DocumentUploadStep({ onNext, onDataUpdate, claimData }: DocumentUploadStepProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);
  const [syncingReceipts, setSyncingReceipts] = useState(false);
  const [receiptSyncStatus, setReceiptSyncStatus] = useState<ReceiptSyncStatus[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const syncReceipts = async () => {
    setSyncingReceipts(true);
    
    // Companies to sync (based on the receipts.json file)
    const companies = [
      { name: 'Home Depot', logo: '🏠', count: 0 },
      { name: 'Amazon', logo: '📦', count: 0 },
      { name: 'Walmart', logo: '🛒', count: 0 }
    ];

    // Initialize sync status
    setReceiptSyncStatus(companies.map(c => ({
      company: c.name,
      logo: c.logo,
      status: 'pending'
    })));

    try {
      // Simulate syncing each company with realistic timing
      for (let i = 0; i < companies.length; i++) {
        const company = companies[i];
        
        // Update to syncing status
        setReceiptSyncStatus(prev => prev.map((status, idx) => 
          idx === i ? { ...status, status: 'syncing' } : status
        ));

        // Simulate API call delay (realistic timing)
        await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
        
        // Call backend to fetch receipts for this company
        try {
          const response = await fetch('http://localhost:8000/api/sync-receipts', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              company: company.name.toLowerCase().replace(' ', '_'),
              claimant_name: 'Test User', // In real app, get from form
              date_range: {
                start: '2024-01-01',
                end: '2025-12-31'
              }
            }),
          });

          if (response.ok) {
            const result = await response.json();
            const receiptCount = result.receipts?.length || 0;
            
            // Update to complete status
            setReceiptSyncStatus(prev => prev.map((status, idx) => 
              idx === i ? { ...status, status: 'complete', count: receiptCount } : status
            ));
            
            // Add receipts to uploaded documents
            if (result.receipts && result.receipts.length > 0) {
              setUploadedDocs(prev => [...prev, ...result.receipts]);
              
              // Also update claimData documents immediately
              const allDocs = [...uploadedDocs, ...result.receipts];
              onDataUpdate({ 
                documents: allDocs
              });
            }
          } else {
            throw new Error(`Failed to sync ${company.name}`);
          }
        } catch (error) {
          console.error(`Error syncing ${company.name}:`, error);
          setReceiptSyncStatus(prev => prev.map((status, idx) => 
            idx === i ? { ...status, status: 'error' } : status
          ));
        }
      }

      toast.success('Receipt sync completed!');
      
      // Update parent component with ALL documents (uploaded + synced)
      const finalDocuments = [...uploadedDocs];
      console.log('📄 Final combined documents:', finalDocuments.length);
      
      onDataUpdate({ 
        documents: finalDocuments,
        knotReceiptsCount: finalDocuments.filter(doc => doc.source === 'knot_api').length
      });
      
    } catch (error) {
      console.error('Receipt sync error:', error);
      toast.error('Failed to sync receipts');
    } finally {
      setSyncingReceipts(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'application/pdf': ['.pdf'],
    },
    multiple: true,
  });

  const uploadDocuments = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/api/upload-documents', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setUploadedDocs(result.documents);
      onDataUpdate({ documents: result.documents });
      
      toast.success(`Successfully processed ${result.documents.length} documents with OCR`);
      onNext();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload documents');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload Documents
        </h2>
        <p className="text-gray-600">
          Upload receipts, lease agreements, and damage photos for your wildfire claim
        </p>
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
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports: JPG, PNG, PDF (Max 10MB each)
            </p>
          </div>
        )}
      </div>

      {/* Receipt Sync Section */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-medium text-gray-900 flex items-center">
              <CreditCard className="h-5 w-5 mr-2 text-green-600" />
              Sync Your Receipts
            </h3>
            <p className="text-sm text-gray-600">
              Automatically fetch receipts from your connected accounts via Knot API
            </p>
          </div>
          <button
            onClick={syncReceipts}
            disabled={syncingReceipts}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {syncingReceipts ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Syncing...</span>
              </>
            ) : (
              <>
                <CreditCard className="h-4 w-4" />
                <span>Sync Receipts</span>
              </>
            )}
          </button>
        </div>

        {/* Receipt Sync Status */}
        {receiptSyncStatus.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {receiptSyncStatus.map((status, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 transition-all duration-300 ${
                  status.status === 'complete' 
                    ? 'border-green-300 bg-green-50' 
                    : status.status === 'syncing'
                    ? 'border-blue-300 bg-blue-50'
                    : status.status === 'error'
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{status.logo}</div>
                    <div>
                      <p className="font-medium text-gray-900">{status.company}</p>
                      {status.status === 'complete' && status.count !== undefined && (
                        <p className="text-sm text-green-600">{status.count} receipts found</p>
                      )}
                      {status.status === 'syncing' && (
                        <p className="text-sm text-blue-600">Fetching receipts...</p>
                      )}
                      {status.status === 'error' && (
                        <p className="text-sm text-red-600">Sync failed</p>
                      )}
                      {status.status === 'pending' && (
                        <p className="text-sm text-gray-500">Waiting...</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center">
                    {status.status === 'syncing' && (
                      <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
                    )}
                    {status.status === 'complete' && (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    )}
                    {status.status === 'error' && (
                      <AlertCircle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">Selected Files:</h3>
          {files.map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
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
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Progress */}
      {uploadedDocs.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-medium text-gray-900">Processed Documents:</h3>
          {uploadedDocs.map((doc, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{doc.filename}</p>
                  <p className="text-xs text-gray-600">
                    OCR Confidence: {(doc.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>
              </div>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                {doc.document_type}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between pt-6">
        <div></div>
        <button
          onClick={uploadDocuments}
          disabled={files.length === 0 || uploading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              <span>Upload & Process with OCR</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
