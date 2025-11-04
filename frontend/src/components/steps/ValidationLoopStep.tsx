'use client';

import { useState, useEffect } from 'react';
import { getApiUrl } from '@/config/api';
import { Shield, RefreshCw, CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';

interface ValidationLoopStepProps {
  onNext: () => void;
  onPrev: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function ValidationLoopStep({ onNext, onPrev, onDataUpdate, claimData }: ValidationLoopStepProps) {
  const [validating, setValidating] = useState(false);
  const [validationHistory, setValidationHistory] = useState<any[]>([]);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [finalValidation, setFinalValidation] = useState<any>(null);

  const runValidationLoop = async () => {
    if (!claimData.claimPacket) {
      toast.error('No claim packet available');
      return;
    }

    // Clear previous validation data
    setValidating(true);
    setValidationHistory([]);
    setCurrentIteration(0);
    setFinalValidation(null);

    try {
      // Add cache-busting and unique claim packet data
      const requestData = {
        claim_packet: {
          ...claimData.claimPacket,
          // Add timestamp to ensure unique request
          validation_timestamp: new Date().toISOString()
        },
        max_iterations: 3,
      };

      console.log('🔍 Sending validation request:', requestData);

      const response = await fetch(getApiUrl('/api/validation-loop'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache', // Prevent caching
        },
        cache: 'no-store', // Force fresh request
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error('Validation failed');
      }

      const result = await response.json();
      
      console.log('🔥 RAW API RESPONSE:', result);
      console.log('🔥 FINAL VALIDATION SCORE:', result.final_validation.overall_score);
      console.log('🔥 CLAIM ID:', result.final_validation.claim_id);
      
      // Force re-render by clearing state first
      setValidationHistory([]);
      setFinalValidation(null);
      
      // Wait for React to update
      setTimeout(() => {
        console.log('✅ Setting new validation data:', {
          score: result.final_validation.overall_score,
          iterations: result.iterations_completed,
          claimId: result.final_validation.claim_id
        });

        setValidationHistory(result.validation_history);
        setFinalValidation(result.final_validation);
        setCurrentIteration(result.iterations_completed);
        
        onDataUpdate({ 
          validationHistory: result.validation_history,
          finalValidation: result.final_validation,
          analysisDepth: result.final_analysis_depth,
          totalImprovement: result.total_improvement
        });
        
        toast.success(`ENHANCED VALIDATION: ${(result.final_validation.overall_score * 100).toFixed(1)}% via ${result.final_analysis_depth} in ${result.iterations_completed} iterations`);
      }, 100);
    } catch (error) {
      console.error('❌ Validation error:', error);
      toast.error('Failed to run validation loop');
    } finally {
      setValidating(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI Judge Validation Loop
        </h2>
        <p className="text-gray-600">
          Run iterative validation with automatic improvements until score stabilizes
        </p>
      </div>

      {/* Claim Packet Summary */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Claim Packet Ready</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-blue-700 font-medium">Claim ID:</span>
            <p className="text-blue-900">{claimData.claimPacket?.claim_id}</p>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Claimant:</span>
            <p className="text-blue-900">{claimData.claimPacket?.claimant_name}</p>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Documents:</span>
            <p className="text-blue-900">{claimData.claimPacket?.documents?.length || 0}</p>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Damage:</span>
            <p className="text-blue-900">${claimData.claimPacket?.estimated_damage?.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Start Validation Button */}
      {validationHistory.length === 0 && !validating && (
        <div className="text-center">
          <button
            onClick={runValidationLoop}
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 mx-auto"
          >
            <Shield className="h-5 w-5" />
            <span>Start AI Judge Validation</span>
          </button>
        </div>
      )}

      {/* Validation Progress */}
      {validating && (
        <div className="text-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Running AI Judge validation loop...</p>
          <p className="text-sm text-gray-500 mt-2">
            This may take a few moments as we analyze your claim and auto-fetch additional receipts
          </p>
        </div>
      )}

      {/* Validation History */}
      {validationHistory.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-medium text-gray-900 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Validation Progress
          </h3>
          
          {validationHistory.map((iteration, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium text-gray-900">
                    Iteration {iteration.iteration}
                  </h4>
                  <p className="text-sm text-blue-600 font-medium">
                    {iteration.analysis_depth?.replace(/_/g, ' ') || 'Standard Analysis'}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBadge(iteration.score)}`}>
                    {(iteration.score * 100).toFixed(1)}%
                  </span>
                  {iteration.improvement !== undefined && iteration.improvement !== 0 && (
                    <p className={`text-xs mt-1 ${iteration.improvement > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {iteration.improvement > 0 ? '+' : ''}{(iteration.improvement * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Rules Passed:</span>
                  <p className="font-medium text-gray-900">
                    {iteration.validation.rules_evaluated?.filter((r: any) => r.passed).length || 0} / {iteration.validation.rules_evaluated?.length || 0}
                  </p>
                </div>
                <div>
                  <span className="text-gray-600">Confidence:</span>
                  <p className="font-medium text-gray-900">{(iteration.validation.confidence * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <span className="text-gray-600">Documents:</span>
                  <p className="font-medium text-gray-900">{iteration.documents_processed || 'N/A'}</p>
                </div>
                <div>
                  <span className="text-gray-600">Status:</span>
                  <p className={`font-medium ${iteration.validation.approved ? 'text-green-600' : 'text-red-600'}`}>
                    {iteration.validation.approved ? 'Approved' : 'Needs Review'}
                  </p>
                </div>
              </div>

              {/* Analysis Depth Details */}
              {iteration.analysis_depth && (
                <div className="mt-3 p-3 bg-gray-50 rounded">
                  <span className="text-gray-600 text-sm font-medium">Analysis Type:</span>
                  <p className="text-sm text-gray-800 mt-1">
                    {iteration.analysis_depth === 'BASIC_SCREENING' && '🏃‍♂️ Surface-level validation for quick approval/rejection'}
                    {iteration.analysis_depth === 'ENHANCED_WITH_RECEIPTS' && '💳 Enhanced analysis with Knot receipt integration'}
                    {iteration.analysis_depth === 'FORENSIC_ANALYSIS' && '🕵️ Deep forensic examination with cross-referencing'}
                    {iteration.analysis_depth === 'EXPERT_REVIEW' && '⚖️ Comprehensive expert-level final assessment'}
                  </p>
                </div>
              )}

              {iteration.validation.missing_documents?.length > 0 && (
                <div className="mt-3">
                  <span className="text-gray-600 text-sm">Missing Documents:</span>
                  <ul className="text-sm text-red-600 mt-1">
                    {iteration.validation.missing_documents.map((doc: string, i: number) => (
                      <li key={i}>• {doc}</li>
                    ))}
                  </ul>
                </div>
              )}

              {iteration.validation.fraud_indicators?.length > 0 && (
                <div className="mt-3">
                  <span className="text-gray-600 text-sm">Fraud Indicators:</span>
                  <ul className="text-sm text-red-600 mt-1">
                    {iteration.validation.fraud_indicators.map((indicator: string, i: number) => (
                      <li key={i}>• {indicator}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Final Results */}
      {finalValidation && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="font-medium text-green-900">Validation Complete</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <span className="text-green-700 font-medium">Final Score:</span>
              <p className={`text-2xl font-bold ${getScoreColor(finalValidation.overall_score)}`}>
                {(finalValidation.overall_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <span className="text-green-700 font-medium">Iterations:</span>
              <p className="text-xl font-bold text-green-900">{currentIteration}</p>
            </div>
            <div>
              <span className="text-green-700 font-medium">Status:</span>
              <p className={`text-xl font-bold ${finalValidation.approved ? 'text-green-600' : 'text-red-600'}`}>
                {finalValidation.approved ? 'APPROVED' : 'REVIEW REQUIRED'}
              </p>
            </div>
          </div>

          <div className="text-sm text-green-800">
            <p className="font-medium mb-2">AI Judge Rationale:</p>
            <p className="bg-green-100 p-3 rounded">{finalValidation.rationale}</p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between pt-6">
        <button
          onClick={onPrev}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={onNext}
          disabled={!finalValidation}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <Shield className="h-4 w-4" />
          <span>Generate Final Outputs</span>
        </button>
      </div>
    </div>
  );
}
