'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Circle, Upload, FileText, Shield } from 'lucide-react';
import DocumentUploadStep from './steps/DocumentUploadStep';
import CreatePacketStep from './steps/CreatePacketStep';
import ValidationLoopStep from './steps/ValidationLoopStep';
import FinalOutputsStep from './steps/FinalOutputsStep';

const steps = [
  { id: 1, name: 'Upload & OCR', icon: Upload },
  { id: 2, name: 'Create Packet', icon: FileText },
  { id: 3, name: 'AI Judge Loop', icon: Shield },
  { id: 4, name: 'Final Outputs', icon: CheckCircle },
];

export default function ClaimWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [claimData, setClaimData] = useState({
    documents: [],
    claimPacket: null,
    validationHistory: [],
    finalValidation: null,
    proofCard: null,
    trustBadge: null,
    finalPdfPath: null,
  });

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const updateClaimData = (data: any) => {
    console.log('🔄 Updating claim data:', data);
    setClaimData(prev => {
      const newData = { ...prev, ...data };
      console.log('📊 New claim data state:', newData);
      return newData;
    });
  };

  // Force clear validation data when going back to step 3
  const clearValidationData = () => {
    console.log('🧹 Clearing validation data');
    setClaimData(prev => ({
      ...prev,
      validationHistory: [],
      finalValidation: null,
      proofCard: null,
      trustBadge: null
    }));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Progress Steps */}
      <div className="px-6 py-4 bg-gray-50 border-b">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            
            return (
              <div key={step.id} className="flex items-center">
                <div className="flex items-center">
                  <div
                    className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                      isCompleted
                        ? 'bg-green-500 border-green-500 text-white'
                        : isCurrent
                        ? 'bg-blue-500 border-blue-500 text-white'
                        : 'bg-white border-gray-300 text-gray-400'
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="h-6 w-6" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <div className="ml-3">
                    <p
                      className={`text-sm font-medium ${
                        isCurrent ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                      }`}
                    >
                      {step.name}
                    </p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {currentStep === 1 && (
              <DocumentUploadStep
                onNext={nextStep}
                onDataUpdate={updateClaimData}
                claimData={claimData}
              />
            )}
            {currentStep === 2 && (
              <CreatePacketStep
                onNext={nextStep}
                onPrev={prevStep}
                onDataUpdate={updateClaimData}
                claimData={claimData}
              />
            )}
            {currentStep === 3 && (
              <ValidationLoopStep
                onNext={nextStep}
                onPrev={prevStep}
                onDataUpdate={updateClaimData}
                claimData={claimData}
              />
            )}
            {currentStep === 4 && (
              <FinalOutputsStep
                onPrev={prevStep}
                onDataUpdate={updateClaimData}
                claimData={claimData}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
