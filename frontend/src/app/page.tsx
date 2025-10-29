'use client';

import { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import ClaimWizard from '@/components/ClaimWizard';
import Header from '@/components/Header';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Toaster position="top-right" />
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              KAVA
            </h1>
            <p className="text-xl text-gray-600 mb-2">
              AI-Powered Insurance Claim Validation
            </p>
            <p className="text-gray-500">
              Upload your documents, let AI validate your claim, and get blockchain-verified proof
            </p>
          </div>
          
          <ClaimWizard />
        </div>
      </main>
    </div>
  );
}
