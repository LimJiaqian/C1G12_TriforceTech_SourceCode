import React, { useEffect, useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { useNavigate } from "react-router-dom";

const purpleIcon = new L.Icon({
  iconUrl:
    "https://upload.wikimedia.org/wikipedia/commons/e/ec/RedDot.svg",
  iconSize: [18, 18],
});

async function geocode(name, state) {
  const query = encodeURIComponent(`${name} ${state} Malaysia`);
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${query}`;

  try {
    const res = await axios.get(url);
    if (res.data.length === 0) return null;

    return {
      lat: parseFloat(res.data[0].lat),
      lon: parseFloat(res.data[0].lon),
    };
  } catch (err) {
    console.error("Geocode error:", err);
    return null;
  }
}

export default function DonationPage() {
  const navigate = useNavigate();

  const [topFive, setTopFive] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTop5() {
      try {
        // 🔥 Fetch from Flask backend
        const res = await axios.get("http://127.0.0.1:5000/api/top5");
        let data = res.data;

        console.log("🔥 Received from backend:", data);

        // Check if data is an error object or invalid
        if (!Array.isArray(data)) {
          console.error("Backend returned non-array data:", data);
          setTopFive([]);
          return;
        }

        // 🔵 Add coordinates to each location
        const enriched = await Promise.all(
          data.map(async (loc) => {
            const coords = await geocode(loc.Name, loc.State);

            return {
              ...loc,
              latitude: coords?.lat || 2.5, // fallback center of MY
              longitude: coords?.lon || 112.5,
            };
          })
        );

        console.log("📌 Geocoded Locations:", enriched);

        setTopFive(enriched);
      } catch (err) {
        console.error("Error fetching AI results:", err);
      } finally {
        setLoading(false);
      }
    }

    loadTop5();
  }, []);

  return (
    <div className="min-h-screen bg-white">
      <div
          className="
            fixed top-0 left-0 w-full
            bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
            backdrop-blur-md shadow-sm z-[999]
          "
        >
          <div className="w-full py-3 px-2 grid grid-cols-3 items-center">
            
            {/* LEFT — Landing Page Button */}
            <button
              onClick={() => navigate("/home")}
              className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                        backdrop-blur hover:bg-white/30 transition justify-self-start"
            >
              ← Back
            </button>

            {/* CENTER — SolarAid Brand */}
            <div className="flex justify-center">
                      <img
                        src="/src/assets/logo.png"
                        alt="Logo"
                        className="w-10 h-10 drop-shadow"
                      />
                      <span className="text-3xl font-semibold text-black">SolarAid</span>
                    </div>

            {/* RIGHT — Spacer to keep center perfectly centered */}
            <div></div>
          </div>
        </div>

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10 pt-28 px-6">

        {/* LEFT — INTERACTIVE MAP */}
        <div className="w-full h-[500px]">
          <MapContainer
            center={[2.5, 112.5]}
            zoom={6}
            style={{ width: "100%", height: "100%" }}
            className="rounded-2xl shadow-lg"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="© OpenStreetMap contributors"
            />

            {/* 🔥 Pins for all locations */}
            {topFive.map((loc) => (
              <Marker
                key={loc.id}
                position={[loc.latitude, loc.longitude]}
                icon={purpleIcon}
              >
                <Popup>
                  <strong>#{loc.Rank} — {loc.Name}</strong>
                  <br />
                  State: {loc.State}
                  <br />
                  Type: {loc.LocationType}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* RIGHT — Donation Cards */}
        <div className="space-y-6">
          <h1 className="text-3xl font-bold text-[#5A32FF]">
            Top 5 Areas Needing Electricity Donations
          </h1>

          {loading && (
            <p className="text-gray-500">Fetching AI results…</p>
          )}

          {!loading &&
            topFive.map((item) => (
              <div
                key={item.id}
                className="border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition"
              >
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-[#5A32FF]">
                    {item.Name}
                  </h2>

                  <span className="text-sm bg-[#5A32FF]/20 text-[#5A32FF] px-3 py-1 rounded-full">
                    {item.State}
                  </span>
                </div>

                <p className="text-xl text-[#5A32FF] mt-2">
                  {item.LocationType}
                </p>

                <p className="mt-3 text-[#5A32FF]/80 text-sm leading-relaxed">
                  {item.Reasoning}
                </p>

                <button
      onClick={() => {
        // Get the selected amount from Overview page (or default to 50)
        const selectedAmount = parseFloat(localStorage.getItem('selectedDonationAmount') || '50');
        
        // Save donation data for certificate generation
        const donationData = {
          kwh: selectedAmount, // Use the ACTUAL amount from the slider
          recipient_type: item.LocationType.toLowerCase().includes('clinic') ? 'clinic' :
                         item.LocationType.toLowerCase().includes('school') ? 'school' :
                         item.LocationType.toLowerCase().includes('disaster') ? 'disaster' : 'home',
          location: item.Name,
          state: item.State
        };
        localStorage.setItem('donationData', JSON.stringify(donationData));
        navigate("/donation_complete");
      }}
      className="mt-4 px-6 py-2 bg-[#6C00FF] text-white rounded-full font-semibold hover:bg-[#5A32FF] transition"
    >
      Donate Electricity
    </button>
              </div>
            ))}
        </div>

      </div>
    </div>
  );
}
