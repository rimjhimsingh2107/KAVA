'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, FileText, ArrowLeft, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

interface ClaimValidationProps {
  onNext: () => void;
  onPrev: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function ClaimValidation({ onNext, onPrev, onDataUpdate, claimData }: ClaimValidationProps) {
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState<any>(null);

  useEffect(() => {
    if (claimData.documents && claimData.documents.length > 0 && !validation) {
      validateClaim();
    }
  }, [claimData.documents]);

  const validateClaim = async () => {
    setValidating(true);
    try {
      const claimPacket = {
        claim_id: `claim_${Date.now()}`,
        policy_number: claimData.claimInfo?.policyNumber || '',
        claimant_name: claimData.claimInfo?.claimantName || '',
        incident_date: claimData.claimInfo?.incidentDate || new Date().toISOString(),
        property_address: claimData.claimInfo?.propertyAddress || '',
        documents: claimData.documents || [],
        estimated_damage: parseFloat(claimData.claimInfo?.estimatedDamage || '0'),
      };

      const response = await axios.post('http://localhost:8000/api/validate-claim', claimPacket);
      setValidation(response.data);
      onDataUpdate({ validation: response.data, claimPacket });
      
      if (response.data.missing_documents && response.data.missing_documents.length > 0) {
        toast.error(`Missing ${response.data.missing_documents.length} required documents`);
      } else if (response.data.approved) {
        toast.success('Claim validation passed!');
      } else {
        toast.error('Claim validation failed');
      }
    } catch (error) {
      console.error('Validation error:', error);
      toast.error('Failed to validate claim');
    } finally {
      setValidating(false);
    }
  };


  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100';
    if (score >= 0.6) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Claim Validation</h2>
        <p className="text-gray-600">
          Our AI Judge is analyzing your claim against insurance policy rules and fraud indicators.
        </p>
      </div>

      {validating && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Validating your claim...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
          </div>
        </div>
      )}

      {validation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Overall Score */}
          <div className={`p-6 rounded-lg ${getScoreBgColor(validation.overall_score)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Validation Score</h3>
                <p className="text-sm text-gray-600">
                  Confidence: {(validation.confidence * 100).toFixed(1)}%
                </p>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${getScoreColor(validation.overall_score)}`}>
                  {(validation.overall_score * 100).toFixed(0)}%
                </div>
                <div className="flex items-center space-x-2">
                  {validation.approved ? (
                    <>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-green-600 font-medium">Approved</span>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-5 w-5 text-red-600" />
                      <span className="text-red-600 font-medium">Needs Review</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Missing Documents */}
          {validation.missing_documents && validation.missing_documents.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-yellow-800">Missing Documents</h4>
                  <ul className="mt-2 space-y-1">
                    {validation.missing_documents.map((doc: string, index: number) => (
                      <li key={index} className="text-sm text-yellow-700">• {doc}</li>
                    ))}
                  </ul>
                  <p className="mt-3 text-sm text-yellow-700">
                    Please upload the missing documents and re-validate your claim.
                  </p>
                </div>
              </div>
            </div>
          )}


          {/* Rule Evaluation Details */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Rule Evaluation</h4>
            <div className="space-y-3">
              {validation.rules_evaluated?.map((rule: any, index: number) => (
                <div key={index} className="flex items-start space-x-3">
                  {rule.passed ? (
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{rule.description}</p>
                    <p className="text-xs text-gray-600">{rule.rationale}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-500">
                        Confidence: {(rule.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-gray-500">
                        Weight: {(rule.weight * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Fraud Indicators */}
          {validation.fraud_indicators && validation.fraud_indicators.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-red-800">Fraud Indicators Detected</h4>
                  <ul className="mt-2 space-y-1">
                    {validation.fraud_indicators.map((indicator: string, index: number) => (
                      <li key={index} className="text-sm text-red-700">• {indicator}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* AI Rationale */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">AI Judge Rationale</h4>
            <p className="text-sm text-blue-700">{validation.rationale}</p>
          </div>
        </motion.div>
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={onPrev}
          className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </button>
        
        <button
          onClick={onNext}
          disabled={!validation || validating}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <span>Generate Proof</span>
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
