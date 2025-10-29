'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, Download, ExternalLink, Copy, CheckCircle, ArrowLeft, Hash } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

interface ProofGenerationProps {
  onPrev: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function ProofGeneration({ onPrev, onDataUpdate, claimData }: ProofGenerationProps) {
  const [generating, setGenerating] = useState(false);
  const [proofCard, setProofCard] = useState<any>(null);
  const [transactionHash, setTransactionHash] = useState<string>('');
  const [verificationUrl, setVerificationUrl] = useState<string>('');

  useEffect(() => {
    if (claimData.validation && !proofCard) {
      generateProof();
    }
  }, [claimData.validation]);

  const generateProof = async () => {
    setGenerating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/generate-proof', {
        claim_packet: claimData.claimPacket,
        validation: claimData.validation,
      });

      setProofCard(response.data.proof_card);
      setTransactionHash(response.data.transaction_hash);
      setVerificationUrl(response.data.verification_url);
      
      onDataUpdate({
        proofCard: response.data.proof_card,
        transactionHash: response.data.transaction_hash,
        verificationUrl: response.data.verification_url,
      });

      toast.success('Proof card generated and anchored to blockchain!');
    } catch (error) {
      console.error('Proof generation error:', error);
      toast.error('Failed to generate proof card');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copied to clipboard!`);
  };

  const downloadClaimPacket = () => {
    const claimPacket = {
      claim_info: claimData.claimInfo,
      documents: claimData.documents?.map((doc: any) => ({
        filename: doc.filename,
        document_type: doc.document_type,
        extracted_data: doc.extracted_data,
        confidence_score: doc.confidence_score,
      })),
      validation: claimData.validation,
      proof_card: proofCard,
      blockchain_verification: {
        transaction_hash: transactionHash,
        verification_url: verificationUrl,
      },
      generated_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(claimPacket, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `claim_packet_${claimData.claimPacket?.claim_id || 'unknown'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success('Claim packet downloaded!');
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Blockchain Proof Generation</h2>
        <p className="text-gray-600">
          Your claim has been cryptographically signed and anchored to the Sepolia blockchain for verification.
        </p>
      </div>

      {generating && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Generating cryptographic proof...</p>
            <p className="text-sm text-gray-500 mt-2">Anchoring to Sepolia blockchain</p>
          </div>
        </div>
      )}

      {proofCard && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Proof Card */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Shield className="h-8 w-8" />
                <div>
                  <h3 className="text-xl font-bold">Claim Proof Card</h3>
                  <p className="text-blue-100">Blockchain Verified</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">
                  {(claimData.validation?.overall_score * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-blue-100">Validation Score</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-blue-100">Claim Hash</p>
                <p className="font-mono text-xs break-all">{proofCard.claim_hash.substring(0, 32)}...</p>
              </div>
              <div>
                <p className="text-blue-100">Timestamp</p>
                <p>{new Date(proofCard.timestamp * 1000).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-blue-100">Rules Version</p>
                <p>{proofCard.validation_rules_version}</p>
              </div>
              <div>
                <p className="text-blue-100">Judge Score</p>
                <p>{(proofCard.judge_score * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>

          {/* Blockchain Details */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Hash className="h-5 w-5" />
              <span>Blockchain Verification</span>
            </h4>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Transaction Hash
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={transactionHash}
                    readOnly
                    className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-md font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(transactionHash, 'Transaction hash')}
                    className="p-2 text-gray-500 hover:text-gray-700"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Claim Hash
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={proofCard.claim_hash}
                    readOnly
                    className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-md font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(proofCard.claim_hash, 'Claim hash')}
                    className="p-2 text-gray-500 hover:text-gray-700"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Signature
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={proofCard.agent_signature}
                    readOnly
                    className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-md font-mono text-sm"
                  />
                  <button
                    onClick={() => copyToClipboard(proofCard.agent_signature, 'Agent signature')}
                    className="p-2 text-gray-500 hover:text-gray-700"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Verification Instructions */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-green-800">Verification Complete</h4>
                <p className="text-sm text-green-700 mt-1">
                  Your claim has been successfully validated and anchored to the blockchain. 
                  Anyone can verify this claim using the transaction hash above.
                </p>
                <div className="mt-3 flex items-center space-x-4">
                  <a
                    href={verificationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-2 text-sm text-green-700 hover:text-green-800"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>View on Blockchain Explorer</span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {claimData.documents?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Documents Processed</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {claimData.validation?.rules_evaluated?.filter((r: any) => r.passed).length || 0}
              </div>
              <div className="text-sm text-gray-600">Rules Passed</div>
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {(claimData.validation?.confidence * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-600">AI Confidence</div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <button
              onClick={onPrev}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back</span>
            </button>
            
            <button
              onClick={downloadClaimPacket}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Download Claim Packet</span>
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
