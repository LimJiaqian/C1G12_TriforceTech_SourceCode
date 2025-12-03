import React, { useEffect, useState } from 'react';
import html2canvas from 'html2canvas';
import { useNavigate } from "react-router-dom";

/**
 * Premium Sadaqah Jariah Certificate Component
 * Royal/Jariah aesthetic with pure CSS (no image templates)
 * 
 * Props:
 * - finalAmount: kWh donated (from parent component)
 * - recipientType: 'clinic', 'school', 'disaster', or 'home'
 * - onClose: callback to close the certificate viewer
 */
export default function PremiumCertificate({ finalAmount, recipientType = 'home', onClose }) {
  const navigate = useNavigate();
  const kwh = finalAmount || 50;
  const [impact, setImpact] = useState(null);
  const [aiText, setAiText] = useState("Weaving your impact story...");
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [certificateId, setCertificateId] = useState("");

  useEffect(() => {
    async function fetchCertificateData() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/certificate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ kwh, recipient_type: recipientType })
        });
        
        const data = await res.json();
        
        console.log("CERTIFICATE API RESPONSE:", data);  
        
        setImpact({
          metric: data.impact_metric,
          co2: data.co2_kg
        });
        setAiText(data.ai_text || "Your generous gift brings cahaya and harapan to our community.");
        setCertificateId(data.certificate_id);
      } catch (err) {
        console.error('Certificate fetch error:', err);
        setAiText("Your generous contribution lights up lives and spreads warmth to those in need.");
        setImpact({
          metric: `${Math.round(kwh / 0.18)} Hours of Study Light`,
          co2: (kwh * 0.76).toFixed(2)
        });
        setCertificateId(`LOCAL-${Date.now()}`);
      } finally {
        setIsLoading(false);
      }
    }

    fetchCertificateData();
  }, [kwh, recipientType]);

  // Helper function to generate image blob (reusable for download & share)
  const generateImageBlob = async () => {
    const element = document.getElementById('certificate-node');
    const canvas = await html2canvas(element, {
      scale: 3,
      backgroundColor: '#FFFCF5',
      logging: false,
      useCORS: true
    });
    
    return new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/png');
    });
  };

  // Download handler using html2canvas
  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const blob = await generateImageBlob();
      const link = document.createElement('a');
      link.download = `Sadaqah-Jariah-Certificate-${kwh}kWh.png`;
      link.href = URL.createObjectURL(blob);
      link.click();
      URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download certificate. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  // Native Share handler (Mobile System Menu - works on iOS/Android)
  const handleNativeShare = async () => {
    setIsSharing(true);

    try {
      // Step A: Snapshot the certificate
      const element = document.getElementById('certificate-node');
      const canvas = await html2canvas(element, {
        scale: 3, // High quality
        backgroundColor: '#FFFCF5',
        useCORS: true,
        logging: false
      });

      // Step B: Convert to a File object
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
      const file = new File([blob], "Jariah-Certificate.png", { type: "image/png" });

      // Step C: Define the text caption
      const impactStory = impact?.metric || `${Math.round(kwh / 0.18)} Hours of Study Light`;
      const shareData = {
        title: 'My Sadaqah Jariah Contribution',
        text: `Alhamdulillah, I just contributed ${kwh} kWh of clean energy! ⚡️ Impact: ${impactStory}. #SolarAid #SadaqahJariah #CleanEnergy`,
        files: [file], // <--- This attaches the image!
      };

      // Step D: Trigger the Mobile System Menu
      if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
        await navigator.share(shareData);
      } else {
        // Fallback for Desktop (where navigator.share often fails)
        alert("📱 Native sharing works best on Mobile!\n\n💻 On Desktop: Downloading image instead...");
        const link = document.createElement('a');
        link.download = `Sadaqah-Jariah-Certificate-${kwh}kWh.png`;
        link.href = canvas.toDataURL();
        link.click();
        
        // Also copy caption for convenience
        const caption = `Alhamdulillah, I just contributed ${kwh} kWh of clean energy! ⚡️ Impact: ${impactStory}. #SolarAid #SadaqahJariah #CleanEnergy`;
        try {
          await navigator.clipboard.writeText(caption);
          setTimeout(() => {
            alert('📋 Caption copied to clipboard!\n\nYou can paste it when sharing manually.');
          }, 300);
        } catch (e) {
          console.log('Clipboard failed:', e);
        }
      }

    } catch (err) {
      console.error("Error sharing:", err);
      alert("Failed to share. Please try the download button instead.");
    }
    
    setIsSharing(false);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#D4AF37] mx-auto mb-4"></div>
          <p className="text-slate-600">Crafting your Jariah certificate...</p>
        </div>
      </div>
    );
  }

  return (
    // 1. OUTER CONTAINER (Simulates the Paper)
    <div className="flex flex-col items-center py-10 bg-gray-100 min-h-screen">
      
      {/* --- ACTION BUTTONS (Above Certificate) --- */}
      <div className="mb-8 flex flex-col items-center gap-4">
        {/* Download Button */}
        <button 
          onClick={handleDownload}
          disabled={isDownloading || isSharing}
          className="px-8 py-3 bg-[#D4AF37] text-white font-bold rounded-full shadow-lg hover:bg-[#c5a028] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isDownloading ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Printing Certificate...</span>
            </>
          ) : (
            <>
              <span>📥</span>
              <span>Download Certificate</span>
            </>
          )}
        </button>

        {/* Native Share Button (Mobile System Menu) */}
        <button 
          onClick={handleNativeShare}
          disabled={isSharing || isDownloading}
          className="flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold rounded-full shadow-xl hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {isSharing ? (
            <span>Generating...</span>
          ) : (
            <>
              {/* Universal Share Icon */}
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
              </svg>
              <span>Share to WhatsApp / Instagram</span>
            </>
          )}
        </button>
      </div>
      
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
          <div className="py-8">
            <p className="text-slate-500 italic mb-2">This certifies the generation of</p>
            <div className="text-[120px] leading-none font-bold text-[#D4AF37]" style={{ fontFamily: "'Cinzel', serif" }}>
              {kwh}
            </div>
            <p className="text-xl uppercase tracking-widest text-slate-800 font-bold mt-2">
              Kilowatt Hours
            </p>
            <p className="text-slate-400 text-sm mt-1">(Renewable Energy)</p>
          </div>

          {/* IMPACT STORY BOX */}
          <div className="bg-white/80 border border-[#D4AF37]/30 p-8 max-w-xl shadow-sm">
            <p className="text-emerald-700 font-bold uppercase tracking-wide text-sm mb-2">
              Direct Impact
            </p>
            <h2 className="text-3xl text-slate-800 mb-4">
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
            <p className="text-xl italic text-slate-600 leading-relaxed">
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

      {/* Close Button (Floating) */}
      <button
        onClick={() => navigate("/home")}
        className="fixed top-8 right-8 w-20 h-20 bg-white rounded-full shadow-lg 
                  flex items-center justify-center text-slate-600 
                  hover:bg-slate-100 transition z-50 text-3xl font-bold"
      >
        ✕
      </button>


    </div>
  );
}
