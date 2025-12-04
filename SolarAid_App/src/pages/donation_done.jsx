import React, { useEffect, useState } from "react";
import { CheckCircle } from "lucide-react";
import axios from "axios";
import PremiumCertificate from "../components/PremiumCertificate";
import { useNavigate } from "react-router-dom";

export default function DonationComplete() {
  const [impactMessage, setImpactMessage] = useState("Generating message...");
  const [showPopup, setShowPopup] = useState(false);
  const [certificateData, setCertificateData] = useState(null);
  const [myUser, setMyUser] = useState(null);
  const [userLoading, setUserLoading] = useState(true);

  const getDonationData = () => {
    try {
      const stored = localStorage.getItem("donationData");
      if (stored) return JSON.parse(stored);
    } catch { }
    return { kwh: 50, recipient_type: "home" };
  };

  const donationData = getDonationData();

  useEffect(() => {
    async function fetchMessage() {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/thankyou");
        const data = await res.json();
        setImpactMessage(data.message);
      } catch {
        setImpactMessage("Thank you! Your donation is making a real impact.");
      }
    }
    fetchMessage();
  }, []);

  async function openCertificate() {
    const userId = localStorage.getItem("user_id");

    // === 1. GENERATE CERTIFICATE METRICS FROM BACKEND ===
    const res = await fetch("http://127.0.0.1:5000/api/certificate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        kwh: donationData.kwh,
        recipient_type: donationData.recipient_type,
      }),
    });

    const data = await res.json();
    setCertificateData(data);

    // === 2. SAVE TRANSACTION INTO SUPABASE ===
    await fetch("http://127.0.0.1:5000/api/save-transaction", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        certificate_id: data.certificate_id,
        user_id: userId,
        donation_kwh: donationData.kwh,
        impact_metric: data.impact_metric,
        context: donationData.recipient_type,
        co2: data.co2_kg,
      }),
    });

    setShowPopup(true);
  }

// LOAD USER PROFILE
  useEffect(() => {
    async function loadUser() {
      const uid = localStorage.getItem("user_id");
      if (!uid) return;

      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/user-profile/${uid}`);
        setMyUser(res.data);
      } catch (err) {
        console.error("❌ Failed to load user profile:", err);
      } finally {
        setUserLoading(false);
      }
    }

    loadUser();
  }, []);
  
  
  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-6 py-20 text-center">

      {/* NAVBAR */}
      <div className="fixed top-0 left-0 w-full bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF] backdrop-blur-md shadow-sm z-[999]">
        <div className="w-full py-3 px-2 grid grid-cols-3 items-center">
          
          <button
            onClick={() => navigate("/home")}
            className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                        backdrop-blur hover:bg-white/30 transition justify-self-start"
          >
            ← Back
          </button>

          <div className="flex justify-center">
            <img src="/src/assets/logo.png" alt="Logo" className="w-10 h-10" />
            <span className="text-3xl font-semibold text-black">SolarAid</span>
          </div>

          {/* Profile on right */}
          <div className="flex justify-end items-center pr-6">
            {!userLoading && myUser ? (
              <div className="flex items-center gap-3 bg-black/10 px-3 py-1 rounded-full shadow-sm">
                <img src={myUser.User_Img} className="w-10 h-10 rounded-full border border-black shadow" />
                <span className="font-semibold text-black text-lg">{myUser.User_Name}</span>
              </div>
            ) : (
              <div></div>
            )}
          </div>

        </div>
      </div>

      <CheckCircle className="w-20 h-20 text-[#6C00FF] mb-6 mt-4" />

      <h1 className="text-4xl font-bold text-gray-900 mb-2">
        Thank You for Your Donation!
      </h1>

      <div className="bg-gradient-to-r from-blue-500 via-purple-600 to-[#6C00FF] text-white px-8 py-4 rounded-2xl mb-6 shadow-lg">
        <p className="text-sm opacity-90">You donated</p>
        <p className="text-5xl font-bold">{donationData.kwh} kWh</p>
        <p className="text-sm opacity-90">
          to {donationData.location || "a community in need"}
        </p>
      </div>

      <p className="text-gray-600 text-lg max-w-2xl mb-10">{impactMessage}</p>

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

      {showPopup && certificateData && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] overflow-auto">
          <PremiumCertificate
            finalAmount={donationData.kwh}
            recipientType={donationData.recipient_type}
            aiData={certificateData}
            onClose={() => setShowPopup(false)}
          />
        </div>
      )}
    </div>
  );
}
