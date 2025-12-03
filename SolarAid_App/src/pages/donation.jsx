import React, { useEffect, useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { useNavigate } from "react-router-dom";

// MAP ICON
const purpleIcon = new L.Icon({
  iconUrl: "https://upload.wikimedia.org/wikipedia/commons/e/ec/RedDot.svg",
  iconSize: [18, 18],
});

// SMART GEO-CODER
async function geocode(name, state, district, area) {
  const queries = [
    `${district}, ${state}, Malaysia`,
    `${area}, ${state}, Malaysia`,
    `${name}, ${state}, Malaysia`,
    `${state}, Malaysia`,
  ];

  for (let query of queries) {
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
        query
      )}`;
      const res = await axios.get(url);

      if (res.data.length > 0) {
        return {
          lat: parseFloat(res.data[0].lat),
          lon: parseFloat(res.data[0].lon),
        };
      }
    } catch (err) {
      console.error("Geocode error:", err);
    }
  }

  return { lat: 4.2105, lon: 101.9758 }; // fallback Malaysia
}

export default function DonationPage() {
  const navigate = useNavigate();

  const [topFive, setTopFive] = useState([]);
  const [loading, setLoading] = useState(true);

  const [myUser, setMyUser] = useState(null);
  const [userLoading, setUserLoading] = useState(true);

  // LOAD TOP 5 LOCATIONS
  useEffect(() => {
    async function loadTop5() {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/top5");
        let data = res.data;

        if (!Array.isArray(data)) {
          console.error("❌ Backend returned non-array:", data);
          return;
        }

        const enriched = await Promise.all(
          data.map(async (loc) => {
            const coords = await geocode(
              loc.Name,
              loc.State,
              loc.District,
              loc.Area
            );
            return { ...loc, latitude: coords.lat, longitude: coords.lon };
          })
        );

        setTopFive(enriched);

      } catch (err) {
        console.error("❌ Error fetching top5:", err);
      } finally {
        setLoading(false);
      }
    }

    loadTop5();
  }, []);

  // LOAD USER PROFILE (AVATAR + NAME)
  useEffect(() => {
    async function loadUser() {
      const uid = localStorage.getItem("user_id");
      if (!uid) {
        console.error("❌ No user_id in localStorage");
        return;
      }

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
    <div className="min-h-screen bg-white">

      {/* NAVBAR */}
      <div
        className="
          fixed top-0 left-0 w-full
          bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]
          backdrop-blur-md shadow-sm z-[999]
        "
      >
        <div className="w-full py-3 px-2 grid grid-cols-3 items-center">
          
          {/* Back Button */}
          <button
            onClick={() => navigate("/home")}
            className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                      backdrop-blur hover:bg-white/30 transition justify-self-start"
          >
            ← Back
          </button>

          {/* Center Logo */}
          <div className="flex justify-center">
            <img src="/src/assets/logo.png" alt="Logo" className="w-10 h-10" />
            <span className="text-3xl font-semibold text-black">SolarAid</span>
          </div>

          {/* Right Profile */}
          <div className="flex justify-end items-center pr-6">
            {!userLoading && myUser ? (
              <div className="flex items-center gap-3 bg-black/10 px-3 py-1 rounded-full shadow-sm">
                <img
                  src={myUser.User_Img}
                  alt="avatar"
                  className="w-10 h-10 rounded-full border border-black shadow"
                />
                <span className="font-semibold text-black text-lg">
                  {myUser.User_Name}
                </span>
              </div>
            ) : (
              <div></div>
            )}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="w-full flex justify-center bg-white">
        <div className="w-[90%] grid grid-cols-1 md:grid-cols-[40%_60%] gap-8 pt-32 pb-12">

          {/* LEFT: MAP */}
          <div className="sticky top-28 h-[75vh]">
            <div className="w-full h-full p-1.5 rounded-2xl bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF] shadow-xl">
              <div className="w-full h-full bg-white rounded-xl overflow-hidden shadow-lg border border-gray-200">
                <MapContainer
                  center={[4.2105, 101.9758]}
                  zoom={6}
                  style={{ width: "100%", height: "100%" }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution="© OpenStreetMap contributors"
                  />

                  {topFive.map((loc) => (
                    <Marker
                      key={loc.id}
                      position={[loc.latitude, loc.longitude]}
                      icon={purpleIcon}
                    >
                      <Popup>
                        <strong>#{loc.Rank} — {loc.Name}</strong><br />
                        Type: {loc.LocationType}<br />
                        Area: {loc.Area}<br />
                        District: {loc.District}<br />
                        State: {loc.State}
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          </div>

          {/* RIGHT: SCROLLABLE LIST */}
          <div className="
            h-[75vh] overflow-y-auto rounded-2xl shadow-lg
            bg-gradient-to-r from-[#6C00FF] via-[#5A32FF] to-[#3BA0FF]
            border border-[#D5C4FF] p-0 relative
          ">

            <div className="sticky top-0 z-20 bg-gradient-to-r from-[#6C00FF] via-[#5A32FF] to-[#3BA0FF] px-6 pt-5 pb-4 border-b border-[#D5C4FF]/50">
              <h1 className="text-3xl font-extrabold text-white">
                Top 5 Areas Needing Electricity Donations
              </h1>
            </div>

            <div className="px-6 pt-4 pb-6 space-y-6">
              
              {loading && (
                <div className="text-white text-lg font-medium py-4">
                  Fetching AI data…
                </div>
              )}

              {!loading &&
                topFive.map((item) => (
                  <div
                    key={item.id}
                    className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md"
                  >
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-bold text-[#5A32FF]">
                        {item.Name}
                      </h2>

                      <span className="px-4 py-1 bg-[#5A32FF]/15 text-[#5A32FF] text-xl rounded-full">
                        {item.State}
                      </span>
                    </div>

                    <p className="mt-3 text-[#5A32FF] text-xl italic">
                      Location Type: {item.LocationType}
                    </p>

                    <p className="mt-3 text-[#5A32FF]/80 text-sm">
                      {item.Reasoning}
                    </p>

                    <button
                      onClick={() => {
                        const selectedAmount = parseFloat(
                          localStorage.getItem("selectedDonationAmount") || "50"
                        );
                        const donationData = {
                          kwh: selectedAmount,
                          recipient_type: item.LocationType,
                          location: item.Name,
                          state: item.State,
                        };
                        localStorage.setItem("donationData", JSON.stringify(donationData));
                        navigate("/donation_complete");
                      }}
                      className="mt-4 w-full py-3 bg-[#6C00FF] text-white rounded-full font-semibold hover:bg-[#5A32FF] transition"
                    >
                      Donate Electricity
                    </button>
                  </div>
                ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
