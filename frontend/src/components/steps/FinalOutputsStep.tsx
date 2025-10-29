'use client';

import { useState } from 'react';
import { Download, Shield, Award, ExternalLink, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface FinalOutputsStepProps {
  onPrev: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function FinalOutputsStep({ onPrev, onDataUpdate, claimData }: FinalOutputsStepProps) {
  const [generating, setGenerating] = useState(false);
  const [finalOutputs, setFinalOutputs] = useState<any>(null);

  const generateFinalOutputs = async () => {
    if (!claimData.finalValidation) {
      toast.error('No validation data available');
      return;
    }

    setGenerating(true);

    try {
      const response = await fetch('http://localhost:8000/api/generate-final-outputs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim_packet: claimData.claimPacket,
          validation: claimData.finalValidation,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate final outputs');
      }

      const result = await response.json();
      setFinalOutputs(result);
      onDataUpdate({ 
        finalOutputs: result,
        proofCard: result.proof_card,
        trustBadge: result.trust_badge,
        finalPdfPath: result.final_claim_packet_pdf 
      });
      
      toast.success('Final outputs generated successfully!');
    } catch (error) {
      console.error('Generate outputs error:', error);
      toast.error('Failed to generate final outputs');
    } finally {
      setGenerating(false);
    }
  };

  const downloadClaimPacket = async () => {
    if (!claimData.claimPacket?.claim_id) {
      toast.error('No claim ID available');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/download-final-pdf/${claimData.claimPacket.claim_id}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `claim_${claimData.claimPacket.claim_id}_final_validated.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('AI Validation Report downloaded!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download validation report');
    }
  };

  const downloadCompletePackage = async () => {
    if (!claimData.claimPacket?.claim_id) {
      toast.error('No claim ID available');
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/download-complete-package/${claimData.claimPacket.claim_id}`);
      
      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `claim_${claimData.claimPacket.claim_id}_COMPLETE_PACKAGE.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Complete Claim Package downloaded!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download complete package');
    }
  };

  const getTrustBadgeColor = (badge: string) => {
    switch (badge) {
      case 'GOLD_TRUST': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'SILVER_TRUST': return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'BRONZE_TRUST': return 'bg-orange-100 text-orange-800 border-orange-300';
      default: return 'bg-red-100 text-red-800 border-red-300';
    }
  };

  const getTrustBadgeIcon = (badge: string) => {
    switch (badge) {
      case 'GOLD_TRUST': return '🥇';
      case 'SILVER_TRUST': return '🥈';
      case 'BRONZE_TRUST': return '🥉';
      default: return '⚠️';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Final Outputs
        </h2>
        <p className="text-gray-600">
          Generate final claim packet PDF, attestation score, and proof card with ECDSA signature
        </p>
      </div>

      {/* Validation Summary */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Validation Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <span className="text-blue-700 font-medium">Final Score:</span>
            <p className="text-2xl font-bold text-blue-900">
              {claimData.finalValidation ? (claimData.finalValidation.overall_score * 100).toFixed(1) : 0}%
            </p>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Status:</span>
            <p className={`text-lg font-bold ${claimData.finalValidation?.approved ? 'text-green-600' : 'text-red-600'}`}>
              {claimData.finalValidation?.approved ? 'APPROVED' : 'REVIEW REQUIRED'}
            </p>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Iterations:</span>
            <p className="text-lg font-bold text-blue-900">
              {claimData.validationHistory?.length || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      {!finalOutputs && (
        <div className="text-center">
          <button
            onClick={generateFinalOutputs}
            disabled={generating || !claimData.finalValidation}
            className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Generating Final Outputs...</span>
              </>
            ) : (
              <>
                <Award className="h-5 w-5" />
                <span>Generate Final Outputs</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Final Outputs Display */}
      {finalOutputs && (
        <div className="space-y-6">
          {/* Trust Badge */}
          <div className="text-center">
            <div className={`inline-flex items-center px-6 py-3 rounded-full border-2 ${getTrustBadgeColor(finalOutputs.trust_badge)}`}>
              <span className="text-2xl mr-2">{getTrustBadgeIcon(finalOutputs.trust_badge)}</span>
              <span className="font-bold text-lg">{finalOutputs.trust_badge.replace('_', ' ')}</span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Attestation Score: {(finalOutputs.attestation_score * 100).toFixed(1)}%
            </p>
          </div>

          {/* Outputs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* COMPLETE CLAIM PACKAGE - PRIMARY */}
            <div className="border-2 border-blue-500 rounded-lg p-6 bg-blue-50 shadow-lg">
              <div className="flex items-center mb-4">
                <Download className="h-8 w-8 text-blue-600 mr-2" />
                <div>
                  <h3 className="font-bold text-gray-900">Complete Claim Package</h3>
                  <span className="text-xs text-blue-600 font-semibold">RECOMMENDED</span>
                </div>
              </div>
              <p className="text-sm text-gray-700 mb-4 leading-relaxed">
                📦 <strong>ZIP file</strong> with all documents organized by type:<br/>
                • Cover letter (AI-generated)<br/>
                • All your uploaded documents<br/>
                • Receipts, photos, reports<br/>
                • AI validation report
              </p>
              <button
                onClick={downloadCompletePackage}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2 font-semibold shadow-md hover:shadow-lg transition"
              >
                <Download className="h-5 w-5" />
                <span>Download Complete Package</span>
              </button>
            </div>

            {/* AI Validation Report */}
            <div className="border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Download className="h-6 w-6 text-green-600 mr-2" />
                <h3 className="font-medium text-gray-900">AI Validation Report</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                PDF with AI Judge analysis, trust score, and validation details
              </p>
              <button
                onClick={downloadClaimPacket}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center justify-center space-x-2"
              >
                <Download className="h-4 w-4" />
                <span>Download Report PDF</span>
              </button>
            </div>

            {/* Proof Card */}
            <div className="border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Shield className="h-6 w-6 text-purple-600 mr-2" />
                <h3 className="font-medium text-gray-900">Cryptographic Proof</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="text-gray-600">Claim Hash:</span>
                  <p className="font-mono text-xs break-all">{finalOutputs.proof_card?.claim_hash?.substring(0, 24)}...</p>
                </div>
                <div>
                  <span className="text-gray-600">ECDSA Signature:</span>
                  <p className="font-mono text-xs break-all">{finalOutputs.proof_card?.ecdsa_signature?.substring(0, 24)}...</p>
                </div>
              </div>
              <a
                href={finalOutputs.verification_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center justify-center space-x-2"
              >
                <ExternalLink className="h-4 w-4" />
                <span>Verify Proof</span>
              </a>
            </div>
          </div>

          {/* Proof Details */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-3">Proof Verification Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Proof ID:</span>
                <p className="font-mono">{finalOutputs.proof_id}</p>
              </div>
              <div>
                <span className="text-gray-600">Verification URL:</span>
                <p className="font-mono text-xs break-all">{finalOutputs.verification_url}</p>
              </div>
              <div>
                <span className="text-gray-600">Judge Score:</span>
                <p className="font-bold">{(finalOutputs.proof_card?.judge_score * 100).toFixed(1)}%</p>
              </div>
              <div>
                <span className="text-gray-600">Rules Version:</span>
                <p>{finalOutputs.proof_card?.validation_rules_version}</p>
              </div>
            </div>
          </div>

          {/* Success Message */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-green-900 mb-2">
              Claim Processing Complete!
            </h3>
            <p className="text-green-800">
              Your claim has been processed through our AI Judge validation system. 
              The final outputs include a validated claim packet PDF and cryptographic proof card 
              with ECDSA signature for verification.
            </p>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between pt-6">
        <button
          onClick={onPrev}
          disabled={generating}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100"
        >
          Back
        </button>
        {finalOutputs && (
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <CheckCircle className="h-4 w-4" />
            <span>Process New Claim</span>
          </button>
        )}
      </div>
    </div>
  );
}
