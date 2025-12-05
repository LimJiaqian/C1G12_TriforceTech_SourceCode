import React, { useEffect, useState } from 'react';
import html2canvas from 'html2canvas';
import { useNavigate } from "react-router-dom";

/**
 * Premium Sadaqah Jariah Certificate Component
 * Supports:
 * 1) New donation (with aiData)
 * 2) Viewing saved certificate history (historyData)
 */
export default function PremiumCertificate({
  finalAmount,
  recipientType = 'home',
  onClose,
  historyData = null,   // from history page
  aiData = null         // from DonationComplete
}) {
  const navigate = useNavigate();

  const isHistory = historyData !== null;
  const isNewDonation = aiData !== null;

  const [kwh, setKwh] = useState(
    isHistory ? historyData.Donation_kwh : (finalAmount || 50)
  );

  const [impact, setImpact] = useState(null);
  const [aiText, setAiText] = useState("Preparing your Jariah certificate...");
  const [isLoading, setIsLoading] = useState(true);
  const [certificateId, setCertificateId] = useState(
    isHistory ? historyData.Certificate_ID : ""
  );
  const [userName, setUserName] = useState("Contributor");

  // Load username
  async function fetchUserName() {
    try {
      const uid = localStorage.getItem("user_id");
      if (!uid) return;

      const res = await fetch(`http://127.0.0.1:5000/api/user-profile/${uid}`);
      const data = await res.json();
      if (data?.User_Name) setUserName(data.User_Name);
    } catch {}
  }

  // LOAD DATA BASED ON MODE
  useEffect(() => {
    fetchUserName();

    // --- HISTORY MODE ---
    if (isHistory) {
      setImpact({
        metric: historyData.Impact_Metric,
        co2: historyData.Co2,
      });
      setAiText(historyData.Impact_Metric);
      setCertificateId(historyData.Certificate_ID);
      setIsLoading(false);
      return;
    }

    // --- NEW DONATION MODE ---
    if (isNewDonation) {
      setImpact({
        metric: aiData.impact_metric,
        co2: aiData.co2_kg,
      });
      setAiText(aiData.ai_text || "");
      setCertificateId(aiData.certificate_id);
      setIsLoading(false);
      return;
    }

  }, [historyData, aiData, isHistory, isNewDonation]);

  // Generate image blob
  const generateImageBlob = async () => {
    const element = document.getElementById('certificate-node');
    const canvas = await html2canvas(element, {
      scale: 3,
      backgroundColor: '#FFFCF5',
      logging: false,
      useCORS: true,
    });

    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/png');
    });
  };

  // Download button
  const handleDownload = async () => {
    const blob = await generateImageBlob();
    const link = document.createElement('a');
    link.download = `Sadaqah-Jariah-Certificate-${certificateId}.png`;
    link.href = URL.createObjectURL(blob);
    link.click();
    URL.revokeObjectURL(link.href);
  };

  // SHARE (mobile only)
  const handleShare = async () => {
    const blob = await generateImageBlob();
    const file = new File([blob], "certificate.png", { type: "image/png" });

    const shareData = {
      title: "My Sadaqah Jariah Contribution",
      text: `Alhamdulillah, I contributed ${kwh} kWh ❤️`,
      files: [file],
    };

    if (navigator.share && navigator.canShare(shareData)) {
      await navigator.share(shareData);
    } else {
      alert("Sharing only supported on mobile. Downloading instead.");
      handleDownload();
    }
  };

  // LOADING SCREEN
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-20 text-center">
        <div>
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#D4AF37] mx-auto mb-4"></div>
          <p className="text-slate-600">Crafting your Jariah certificate...</p>
        </div>
      </div>
    );
  }

  // ============================================================
  //   ⭐ FULL CERTIFICATE DESIGN (UNTOUCHED — EXACTLY AS BEFORE)
  // ============================================================

  return (
    <div className="flex flex-col items-center py-10 bg-gray-100 min-h-screen">

      {/* Buttons */}
      <div className="mb-8 flex flex-col items-center gap-4">
        <button
          onClick={handleDownload}
          className="px-8 py-3 bg-[#D4AF37] text-white font-bold rounded-full shadow-lg hover:bg-[#c5a028]"
        >
          📥 Download Certificate
        </button>

        <button
          onClick={handleShare}
          className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold rounded-full shadow-xl"
        >
          Share to WhatsApp / Instagram
        </button>
      </div>

      {/* Certificate */}
      <div
        id="certificate-node"
        className="relative w-[800px] h-[1120px] bg-[#FFFCF5] text-center shadow-2xl overflow-hidden"
        style={{ fontFamily: "'Playfair Display', serif" }}
      >

        {/* Outer border */}
        <div className="absolute inset-4 border-[3px] border-[#D4AF37]"></div>
        <div className="absolute inset-6 border border-[#D4AF37]/50"></div>

        {/* Corners */}
        <div className="absolute top-4 left-4 w-16 h-16 border-t-[3px] border-l-[3px] border-[#D4AF37]"></div>
        <div className="absolute top-4 right-4 w-16 h-16 border-t-[3px] border-r-[3px] border-[#D4AF37]"></div>
        <div className="absolute bottom-4 left-4 w-16 h-16 border-b-[3px] border-l-[3px] border-[#D4AF37]"></div>
        <div className="absolute bottom-4 right-4 w-16 h-16 border-b-[3px] border-r-[3px] border-[#D4AF37]"></div>

        {/* Content */}
        <div className="relative z-10 flex flex-col items-center justify-between h-full py-24 px-16">

          {/* Header */}
          <div className="space-y-4">
            <h3 className="text-[#D4AF37] tracking-[0.4em] text-sm uppercase font-bold">
              Official Contribution
            </h3>
            <h1 className="text-6xl font-bold text-slate-800" style={{ fontFamily: "'Cinzel', serif" }}>
              Sadaqah Jariah
            </h1>
            <div className="w-32 h-1 bg-[#D4AF37] mx-auto mt-4"></div>
          </div>

          {/* kWh */}
          <div className="py-8 text-center">
            <p className="text-slate-500 italic mb-1">This certifies the generation of</p>

            <h2
              className="text-[120px] leading-none font-bold mt-2 bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  "linear-gradient(135deg, #d4af37 0%, #ffcc00 40%, #e1af25 60%, #ffd24d 100%)",
                fontFamily: "'Cinzel', serif",
              }}
            >
              {kwh}
            </h2>

            <p className="text-xl uppercase tracking-widest text-slate-800 font-bold mt-2">
              Kilowatt Hours
            </p>
            <p className="text-slate-400 text-sm mt-1">(Renewable Energy)</p>
          </div>

          {/* Awarded To */}
          <div className="mt-10 text-center">
            <p className="text-slate-500 text-lg italic">Awarded to</p>
            <h2
              className="text-4xl font-bold mt-2 bg-clip-text text-transparent"
              style={{
                backgroundImage:
                  "linear-gradient(135deg, #d4af37 0%, #ffcc00 40%, #e1af25 60%, #ffd24d 100%)",
                fontFamily: "'Cinzel', serif",
              }}
            >
              {userName}
            </h2>
          </div>

          {/* Impact */}
          <div className="bg-white/80 border border-[#D4AF37]/30 p-8 max-w-xl shadow-sm mt-10">
            <p className="text-emerald-700 font-bold uppercase tracking-wide text-sm mb-2">
              Direct Impact
            </p>

            <h2 className="text-3xl text-slate-800 mb-4">{impact?.metric}</h2>

            <div className="flex items-center justify-center gap-2 mb-4">
              <span className="text-2xl">🌱</span>
              <p className="text-emerald-600 font-semibold">{impact?.co2} kg CO₂ Avoided</p>
            </div>

            <p className="text-xl italic text-slate-600 leading-relaxed">"{aiText}"</p>
          </div>

          {/* Footer */}
          <div className="w-full flex justify-between items-end border-t border-[#D4AF37]/30 pt-8 mt-4">
            <div className="text-left">
              <p className="text-xs uppercase text-[#D4AF37] font-bold">Project</p>
              <p className="text-slate-800">SolarAid Grid Initiative</p>
            </div>

            <div className="w-24 h-24 border-4 border-[#D4AF37]/30 rounded-full flex items-center justify-center text-[#D4AF37]/50 font-bold uppercase text-[10px] rotate-[-15deg]">
              Verified
            </div>

            <div className="text-right">
              <p className="text-xs uppercase text-[#D4AF37] font-bold">Date</p>
              <p className="text-slate-800">{new Date().toLocaleDateString()}</p>

              <p className="text-xs uppercase text-[#D4AF37] font-bold mt-2">Certificate ID</p>
              <p className="text-slate-800">{certificateId}</p>
            </div>
          </div>
        </div>
      </div>

      {/* CLOSE BUTTON */}
      <button
        onClick={() => {
          if (isHistory) onClose();     // Close popup when viewing history
          else navigate("/home");       // New donation → go home
        }}
        className="fixed top-8 right-8 w-20 h-20 bg-white rounded-full shadow-lg 
                   flex items-center justify-center text-slate-600 
                   hover:bg-slate-100 transition text-3xl font-bold z-50"
      >
        ✕
      </button>

    </div>
  );
}
