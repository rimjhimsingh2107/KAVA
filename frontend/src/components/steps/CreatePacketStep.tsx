'use client';

import { useState } from 'react';
import { FileText, User, MapPin, Calendar, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';
import { getApiUrl } from '@/config/api';

interface CreatePacketStepProps {
  onNext: () => void;
  onPrev: () => void;
  onDataUpdate: (data: any) => void;
  claimData: any;
}

export default function CreatePacketStep({ onNext, onPrev, onDataUpdate, claimData }: CreatePacketStepProps) {
  const [formData, setFormData] = useState({
    claim_id: `WF-${Date.now()}`,
    policy_number: '',
    claimant_name: '',
    incident_date: '',
    property_address: '',
    estimated_damage: '',
  });
  const [creating, setCreating] = useState(false);
  const [claimPacket, setClaimPacket] = useState<any>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const createClaimPacket = async () => {
    // Validate form
    if (!formData.claimant_name || !formData.policy_number || !formData.incident_date || !formData.property_address) {
      toast.error('Please fill in all required fields');
      return;
    }

    setCreating(true);

    try {
      const claimPacketData = {
        ...formData,
        estimated_damage: parseFloat(formData.estimated_damage) || 0,
        incident_date: new Date(formData.incident_date).toISOString(),
        documents: claimData.documents || [],
      };

      const response = await fetch(getApiUrl('/api/create-claim-packet'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(claimPacketData),
      });

      if (!response.ok) {
        throw new Error('Failed to create claim packet');
      }

      const result = await response.json();
      setClaimPacket(result.claim_packet);
      onDataUpdate({ 
        claimPacket: result.claim_packet,
        initialPdfPath: result.pdf_path 
      });
      
      toast.success('Claim packet created successfully!');
      onNext();
    } catch (error) {
      console.error('Create packet error:', error);
      toast.error('Failed to create claim packet');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Create Initial Claim Packet
        </h2>
        <p className="text-gray-600">
          Fill in your claim details to create the initial claim packet PDF
        </p>
      </div>

      {/* Uploaded Documents Summary */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Uploaded Documents</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          {claimData.documents?.map((doc: any, index: number) => (
            <div key={index} className="text-sm text-blue-800">
              • {doc.filename} ({doc.document_type})
            </div>
          ))}
        </div>
      </div>

      {/* Claim Information Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <User className="inline h-4 w-4 mr-1" />
            Claimant Name *
          </label>
          <input
            type="text"
            name="claimant_name"
            value={formData.claimant_name}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <FileText className="inline h-4 w-4 mr-1" />
            Policy Number *
          </label>
          <input
            type="text"
            name="policy_number"
            value={formData.policy_number}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="Enter policy number"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Calendar className="inline h-4 w-4 mr-1" />
            Incident Date *
          </label>
          <input
            type="date"
            name="incident_date"
            value={formData.incident_date}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <DollarSign className="inline h-4 w-4 mr-1" />
            Estimated Damage
          </label>
          <input
            type="number"
            name="estimated_damage"
            value={formData.estimated_damage}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-900"
            placeholder="Enter estimated damage amount"
            min="0"
            step="0.01"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <MapPin className="inline h-4 w-4 mr-1" />
          Property Address *
        </label>
        <textarea
          name="property_address"
          value={formData.property_address}
          onChange={handleInputChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-gray-900"
          placeholder="Enter full property address"
          required
        />
      </div>

      {/* Claim ID Display */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Generated Claim ID
        </label>
        <p className="text-lg font-mono text-gray-900">{formData.claim_id}</p>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between pt-6">
        <button
          onClick={onPrev}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={createClaimPacket}
          disabled={creating}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {creating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Creating Packet...</span>
            </>
          ) : (
            <>
              <FileText className="h-4 w-4" />
              <span>Create Claim Packet</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
