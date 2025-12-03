// DonationHistory.jsx
import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

export default function DonationHistory() {
  const navigate = useNavigate();
  const location = useLocation();
  const myUser = location.state?.myUser;

  // Mock donation history data
  const donationHistory = myUser?.donations || [
    { id: "CERT001", date: "2025-11-01", amount: 50 },
    { id: "CERT002", date: "2025-11-10", amount: 30 },
    { id: "CERT003", date: "2025-11-15", amount: 40 },
  ];

  const downloadCertificate = (id) => {
    // Example: mock download
    alert(`Downloading certificate ${id}`);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation Bar */}
      <div className="fixed top-0 left-0 w-full
                      bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
                      backdrop-blur-md shadow-sm z-[999]">
        <div className="w-full py-3 px-2 grid grid-cols-3 items-center">
          {/* Back button */}
          <button
            onClick={() => navigate("/home")}
            className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                        backdrop-blur hover:bg-white/30 transition justify-self-start"
          >
            ← Back
          </button>

          {/* Center Brand */}
          <div className="flex justify-center">
            <img
              src="/src/assets/logo.png"
              alt="Logo"
              className="w-10 h-10 drop-shadow"
            />
            <span className="text-3xl font-semibold text-black">SolarAid</span>
          </div>

          <div></div> {/* Empty spacer */}
        </div>
      </div>

      <div className="max-w-5xl mx-auto pt-24 px-6">
        <h2 className="text-3xl font-bold mb-4">Donation History</h2>

        {!donationHistory || donationHistory.length === 0 ? (
          <p className="text-gray-600">No donations yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-xl shadow-md overflow-hidden">
              <thead className="text-white bg-gradient-to-b from-[#6C00FF] via-[#5A32FF] to-[#3BA0FF]">
                <tr>
                  <th className="py-3 px-4 text-left">Date</th>
                  <th className="py-3 px-4 text-left">Amount (kWh)</th>
                  <th className="py-3 px-4 text-left">Certificate ID</th>
                  <th className="py-3 px-4 text-left">Download</th>
                </tr>
              </thead>
              <tbody>
                {donationHistory.map((donation) => (
                  <tr key={donation.id} className="border-b last:border-none">
                    <td className="py-2 px-4">{new Date(donation.date).toLocaleDateString()}</td>
                    <td className="py-2 px-4">{donation.amount}</td>
                    <td className="py-2 px-4">{donation.id}</td>
                    <td className="py-2 px-4">
                      <button
                        onClick={() => downloadCertificate(donation.id)}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        Download
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
