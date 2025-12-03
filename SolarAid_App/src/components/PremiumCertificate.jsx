import React, { useEffect, useState } from 'react';
import html2canvas from 'html2canvas';
import { useNavigate } from "react-router-dom";

/**
 * Premium Sadaqah Jariah Certificate Component
 * Used for:
 * 1) New donation certificate generation
 * 2) Viewing saved certificate history
 * 
 * Props:
 * - finalAmount: donated kWh (new donations only)
 * - recipientType: 'clinic' | 'school' | 'disaster' | 'home'
 * - onClose: function to close modal
 * - historyData: (optional) data from past transaction
 */
export default function PremiumCertificate({
  finalAmount,
  recipientType = 'home',
  onClose,
  historyData = null,   // <-- NEW
}) {
  const navigate = useNavigate();

  // Detect history mode
  const isHistory = historyData !== null;

  // Certificate state
  const [kwh, setKwh] = useState(isHistory ? historyData.Donation_kwh : (finalAmount || 50));
  const [impact, setImpact] = useState(null);
  const [aiText, setAiText] = useState("Weaving your impact story...");
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isSharing, setIsSharing] = useState(false);

  // IMPORTANT: keep original certificate ID if viewing history
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

      if (data && data.User_Name) setUserName(data.User_Name);
    } catch (err) {
      console.log("Failed to load username:", err);
    }
  }

  // Load certificate data
  useEffect(() => {
    // --- HISTORY MODE ---
    if (isHistory) {
      setImpact({
        metric: historyData.Impact_Metric,
        co2: historyData.Co2,
      });

      setAiText(historyData.Impact_Metric); // or leave empty
      setCertificateId(historyData.Certificate_ID);
      setIsLoading(false);
      fetchUserName();
      return;
    }

    // --- NEW DONATION MODE ---
    async function fetchCertificateData() {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/certificate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ kwh, recipient_type: recipientType }),
        });

        const data = await res.json();

        setImpact({
          metric: data.impact_metric,
          co2: data.co2_kg,
        });

        setAiText(data.ai_text);
        setCertificateId(data.certificate_id);
      } catch (err) {
        console.error("Certificate fetch error:", err);
        setImpact({
          metric: `${Math.round(kwh / 0.18)} Hours of Study Light`,
          co2: (kwh * 0.76).toFixed(2),
        });
      } finally {
        setIsLoading(false);
      }
    }

    fetchCertificateData();
    fetchUserName();
  }, [isHistory, kwh, recipientType, historyData]);


  // Generate screenshot
  const generateImageBlob = async () => {
    const element = document.getElementById("certificate-node");
    const canvas = await html2canvas(element, {
      scale: 3,
      backgroundColor: "#FFFCF5",
      logging: false,
      useCORS: true,
    });

    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), "image/png");
    });
  };

  // Download handler
  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const blob = await generateImageBlob();
      const link = document.createElement("a");
      link.download = `Sadaqah-Jariah-Certificate-${certificateId}.png`;
      link.href = URL.createObjectURL(blob);
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error("Download error:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  // SHARE
  const handleNativeShare = async () => {
    setIsSharing(true);
    try {
      const element = document.getElementById("certificate-node");
      const canvas = await html2canvas(element, {
        scale: 3,
        backgroundColor: "#FFFCF5",
      });

      const blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/png")
      );

      const file = new File([blob], "certificate.png", { type: "image/png" });

      const shareData = {
        title: "My Sadaqah Jariah Contribution",
        text: `Alhamdulillah, I contributed ${kwh} kWh ❤️`,
        files: [file],
      };

      if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
        await navigator.share(shareData);
      } else {
        alert("Sharing only supported on mobile — downloading instead.");
        handleDownload();
      }
    } catch (err) {
      console.log(err);
    }
    setIsSharing(false);
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

  // --- DISPLAY CERTIFICATE (unchanged design) ---
  return (
    <div className="flex flex-col items-center py-10 bg-gray-100 min-h-screen">

      {/* Action Buttons */}
      <div className="mb-8 flex flex-col items-center gap-4">
        <button
          onClick={handleDownload}
          disabled={isDownloading || isSharing}
          className="px-8 py-3 bg-[#D4AF37] text-white font-bold rounded-full shadow-lg hover:bg-[#c5a028]"
        >
          📥 Download Certificate
        </button>

        <button
          onClick={handleNativeShare}
          disabled={isSharing || isDownloading}
          className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold rounded-full shadow-xl"
        >
          Share to WhatsApp / Instagram
        </button>
      </div>

      {/* Certificate content — EXACTLY unchanged */}
      <div
        id="certificate-node"
        className="relative w-[800px] h-[1120px] bg-[#FFFCF5] text-center shadow-2xl overflow-hidden"
        style={{ fontFamily: "'Playfair Display', serif" }}
      >

        {/* 2. THE CERTIFICATE CARD (A4 Aspect Ratio) */}
      <div 
        id="certificate-node"
        className="relative w-[800px] h-[1120px] bg-[#FFFCF5] text-center shadow-2xl overflow-hidden"
        style={{ fontFamily: "'Playfair Display', serif" }}
      >
        
        {/* --- DECORATIVE BORDERS (CSS Magic) --- */}
        {/* Outer Gold Border */}
        <div className="absolute inset-4 border-[3px] border-[#D4AF37]"></div>
        {/* Inner Thin Line */}
        <div className="absolute inset-6 border border-[#D4AF37]/50"></div>
        {/* Corner Ornaments (CSS Rotated Squares) */}
        <div className="absolute top-4 left-4 w-16 h-16 border-t-[3px] border-l-[3px] border-[#D4AF37]"></div>
        <div className="absolute top-4 right-4 w-16 h-16 border-t-[3px] border-r-[3px] border-[#D4AF37]"></div>
        <div className="absolute bottom-4 left-4 w-16 h-16 border-b-[3px] border-l-[3px] border-[#D4AF37]"></div>
        <div className="absolute bottom-4 right-4 w-16 h-16 border-b-[3px] border-r-[3px] border-[#D4AF37]"></div>

        {/* --- CONTENT LAYER --- */}
        <div className="relative z-10 flex flex-col items-center justify-between h-full py-24 px-16">
          
          {/* HEADER */}
          <div className="space-y-4">
            <h3 className="text-[#D4AF37] tracking-[0.4em] text-sm uppercase font-bold">
              Official Contribution
            </h3>
            <h1 className="text-6xl font-bold text-slate-800" style={{ fontFamily: "'Cinzel', serif" }}>
              Sadaqah Jariah
            </h1>
            <div className="w-32 h-1 bg-[#D4AF37] mx-auto mt-4"></div>
          </div>

          {/* HERO METRIC (The kWh) */}
          <div className="py-8 text-center">
            <p className="text-slate-500 italic mb-1">
              This certifies the generation of
            </p>

              <h2
                className="text-[120px] leading-none font-bold mt-2 bg-clip-text text-transparent"
                style={{
                  backgroundImage: "linear-gradient(135deg, #d4af37 0%, #ffcc00ff 40%, #e1af25ff 60%, #ffd24dff 100%)",
                  fontFamily: "'Cinzel', serif"
                }}
              >
                {kwh}
              </h2>

            <p className="text-xl uppercase tracking-widest text-slate-800 font-bold mt-2">
              Kilowatt Hours
            </p>
            <p className="text-slate-400 text-sm mt-1">(Renewable Energy)</p>
          </div>

          {/* AWARDED TO */}
          <div className="mt-10 text-center">
            <p className="text-slate-500 text-lg italic">Awarded to</p>

            <h2
              className="text-4xl font-bold mt-2 bg-clip-text text-transparent"
              style={{
                backgroundImage: "linear-gradient(135deg, #d4af37 0%, #ffcc00ff 40%, #e1af25ff 60%, #ffd24dff 100%)",
                fontFamily: "'Cinzel', serif"
              }}
            >
              {userName}
            </h2>
          </div>

          {/* IMPACT STORY BOX */}
          <div className="bg-white/80 border border-[#D4AF37]/30 p-8 max-w-xl shadow-sm mt-10 text-center">
            <p className="text-emerald-700 font-bold uppercase tracking-wide text-sm mb-2">
              Direct Impact
            </p>

            <h2 className="text-3xl text-slate-800 mb-4 text-center">
              {impact?.metric || `${Math.round(kwh / 0.18)} Hours of Study Light`}
            </h2>

            {/* Environmental Metric */}
            <div className="flex items-center justify-center gap-2 mb-4">
              <span className="text-2xl">🌱</span>
              <p className="text-emerald-600 font-semibold">
                {impact?.co2 || (kwh * 0.76).toFixed(2)} kg CO₂ Avoided
              </p>
            </div>

            {/* The SEA-LION Text */}
            <p className="text-xl italic text-slate-600 leading-relaxed text-center">
              "{aiText}"
            </p>
          </div>

          {/* FOOTER */}
          <div className="w-full flex justify-between items-end border-t border-[#D4AF37]/30 pt-8 mt-4">
            <div className="text-left">
              <p className="text-xs uppercase text-[#D4AF37] font-bold">Project</p>
              <p className="text-slate-800">SolarAid Grid Initiative</p>
            </div>
            
            {/* Mock Stamp/Seal */}
            <div className="w-24 h-24 border-4 border-[#D4AF37]/30 rounded-full flex items-center justify-center text-[#D4AF37]/50 font-bold uppercase text-[10px] tracking-widest rotate-[-15deg]">
              Verified
            </div>

            <div className="text-right">
              <p className="text-xs uppercase text-[#D4AF37] font-bold">Date</p>
              <p className="text-slate-800">{new Date().toLocaleDateString()}</p>

              {/* Certificate ID */}
              <p className="text-xs uppercase text-[#D4AF37] font-bold mt-2">Certificate ID</p>
              <p className="text-slate-800">{certificateId}</p>
            </div>
          </div>

        </div>

      </div>


      </div>

      {/* Close Button */}
      <button
        onClick={() => {
          if (historyData) {
            onClose();        // Close history popup
          } else {
            navigate("/home"); // Go home (normal flow)
          }
        }}
        className="fixed top-8 right-8 w-20 h-20 bg-white rounded-full shadow-lg 
                  flex items-center justify-center text-slate-600 
                  hover:bg-slate-100 transition z-50 text-3xl font-bold"
      >
        ✕
      </button>
    </div>
  );
}
