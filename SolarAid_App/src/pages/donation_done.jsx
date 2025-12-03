import React, { useEffect, useState } from "react";
import { CheckCircle, X } from "lucide-react";
import PremiumCertificate from "../components/PremiumCertificate";

export default function DonationComplete() {
  const [impactMessage, setImpactMessage] = useState("Generating message...");
  const [showPopup, setShowPopup] = useState(false);

  // Get donation data from localStorage or URL params
  const getDonationData = () => {
    try {
      const stored = localStorage.getItem('donationData');
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (err) {
      console.error('Error reading donation data:', err);
    }
    // Default values
    return { kwh: 50, recipient_type: 'home' };
  };

  useEffect(() => {
    async function fetchMessage() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/thankyou`);
        const data = await res.json();
        setImpactMessage(data.message);
      } catch (err) {
        setImpactMessage("Thank you! Your donation is making a real impact.");
      }
    }
    fetchMessage();
  }, []);

  async function openCertificate() {
    setShowPopup(true);
  }

  // Get donation data for display
  const donationData = getDonationData();

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6 py-20 text-center">
      <CheckCircle className="w-20 h-20 text-[#6C00FF] mb-6" />

      <h1 className="text-4xl font-bold text-gray-900 mb-2">
        Thank You for Your Donation!
      </h1>

      {/* Show the actual donated amount */}
      <div className="bg-gradient-to-r from-blue-500 via-purple-600 to-[#6C00FF] text-white px-8 py-4 rounded-2xl mb-6 shadow-lg">
        <p className="text-sm opacity-90">You donated</p>
        <p className="text-5xl font-bold">{donationData.kwh} kWh</p>
        <p className="text-sm opacity-90">to {donationData.location || 'a community in need'}</p>
      </div>

      <p className="text-gray-600 text-lg max-w-2xl mb-10">{impactMessage}</p>

      {/* 💳 The Certificate Card (your preferred UI) */}
      <div className="w-full max-w-2xl border-4 border-[#5A32FF] rounded-3xl p-10 shadow-xl mb-10">
        <h2 className="text-3xl font-bold text-[#5A32FF] mb-3">
          Donation Certificate
        </h2>
        <p className="text-gray-600 text-md mb-8">
          This certificate confirms your contribution in supporting rural communities.
        </p>

        <button
          onClick={openCertificate}
          className="px-10 py-4 bg-[#5A32FF] hover:bg-[#6C00FF] text-white rounded-full font-semibold transition text-lg"
        >
          View Certificate
        </button>
      </div>

      {/* 🏛️ PREMIUM ROYAL CERTIFICATE VIEWER */}
      {showPopup && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] overflow-auto">
          <PremiumCertificate 
            finalAmount={donationData.kwh} 
            recipientType={donationData.recipient_type}
            onClose={() => setShowPopup(false)}
          />
        </div>
      )}
    </div>
  );
}
