// DonationHistory.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import PremiumCertificate from "../components/PremiumCertificate";

export default function DonationHistory() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCertificate, setSelectedCertificate] = useState(null); // <-- NEW

  const [userProfile, setUserProfile] = useState(null);
  const [userLoading, setUserLoading] = useState(true);

  const userId = localStorage.getItem("user_id");

  // --- SAFELY FORMAT SUPABASE TIMESTAMP ---
  function parseSupabaseTimestamp(ts) {
    if (!ts) return new Date();
    return new Date(ts.replace(" ", "T"));
  }

  // --- LOAD DATA FROM BACKEND ---
  useEffect(() => {
    async function loadTransactions() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/transactions/${userId}`);
        const data = await res.json();

        if (Array.isArray(data)) setTransactions(data);
        else setTransactions([]);
      } catch (err) {
        console.error("Transaction fetch error:", err);
      } finally {
        setLoading(false);
      }
    }

    loadTransactions();
  }, [userId]);

  // --- LOAD USER PROFILE FOR AVATAR + NAME ---
  useEffect(() => {
    async function loadUserProfile() {
      try {
        if (!userId) return;

        const res = await fetch(
          `http://127.0.0.1:5000/api/user-profile/${userId}`
        );
        const data = await res.json();

        if (res.ok) {
          setUserProfile(data);
        } else {
          console.error("User profile error:", data);
        }
      } catch (err) {
        console.error("User profile fetch error:", err);
      } finally {
        setUserLoading(false);
      }
    }

    loadUserProfile();
  }, [userId]);

  // --- VIEW CERTIFICATE HANDLER ---
  function handleViewCertificate(item) {
    setSelectedCertificate(item); // Pass entire row to PremiumCertificate
  }

  return (
    <div className="min-h-screen bg-gray-100">
      
      {/* Navigation Bar */}
      <div className="fixed top-0 left-0 w-full
                      bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
                      backdrop-blur-md shadow-sm z-[999]">
        <div className="w-full py-3 px-2 grid grid-cols-3 items-center">
          <button
            onClick={() => navigate("/home")}
            className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                        backdrop-blur hover:bg-white/30 transition justify-self-start"
          >
            ← Back
          </button>

          <div className="flex justify-center">
            <img
              src="/src/assets/logo.png"
              alt="Logo"
              className="w-10 h-10 drop-shadow"
            />
            <span className="text-3xl font-semibold text-black">SolarAid</span>
          </div>

          {/* Profile on right */}
          <div className="flex justify-end items-center pr-6">
            {!userLoading && userProfile ? (
              <div className="flex items-center gap-3 bg-black/10 px-3 py-1 rounded-full shadow-sm">
                <img
                  src={userProfile.User_Img}
                  className="w-10 h-10 rounded-full border border-black shadow"
                  alt={userProfile.User_Name}
                />
                <span className="font-semibold text-black text-lg">
                  {userProfile.User_Name}
                </span>
              </div>
            ) : (
              <div />
            )}
          </div>
        </div>
      </div>

      {/* CONTENT */}
      <div className="max-w-5xl mx-auto pt-24 px-6">
        <h2 className="text-3xl font-bold mb-4">Donation History</h2>

        {loading ? (
          <p className="text-gray-600">Loading...</p>
        ) : transactions.length === 0 ? (
          <p className="text-gray-600">No donations yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-xl shadow-md overflow-hidden">
              <thead className="text-white bg-gradient-to-b from-[#6C00FF] via-[#5A32FF] to-[#3BA0FF]">
                <tr>
                  <th className="py-3 px-4 text-left">Date</th>
                  <th className="py-3 px-4 text-left">Time</th>
                  <th className="py-3 px-4 text-left">Amount (kWh)</th>
                  <th className="py-3 px-4 text-left">Context</th>
                  <th className="py-3 px-4 text-left">Certificate ID</th>
                  <th className="py-3 px-4 text-left">View</th>
                </tr>
              </thead>

              <tbody>
                {transactions.map((item, index) => {
                  const dateObj = parseSupabaseTimestamp(item.Date_Time);

                  return (
                    <tr key={index} className="border-b last:border-none">
                      <td className="py-2 px-4">{dateObj.toLocaleDateString("en-MY")}</td>
                      <td className="py-2 px-4">
                        {dateObj.toLocaleTimeString("en-MY", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td className="py-2 px-4">{item.Donation_kwh}</td>
                      <td className="py-2 px-4">{item.Context}</td>
                      <td className="py-2 px-4">{item.Certificate_ID}</td>

                      <td className="py-2 px-4">
                        <button
                          onClick={() => handleViewCertificate(item)}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>

            </table>
          </div>
        )}
      </div>

      {/* === POPUP FOR VIEWING CERTIFICATE === */}
      {selectedCertificate && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] overflow-auto">
          <PremiumCertificate
            historyData={selectedCertificate} // pass saved data
            onClose={() => setSelectedCertificate(null)}
          />
        </div>
      )}
    </div>
  );
}
