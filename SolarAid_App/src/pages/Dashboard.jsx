import { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MessageCircle } from "lucide-react";
import Overview from "./Overview";
import Leaderboard from "./Leaderboard";
import SmartPrediction from "./SmartPrediction";
import ChatPanel from "./ChatPanel";

export default function Dashboard() {
  const navigate = useNavigate();
  const leftRef = useRef(null);
  const [leftHeight, setLeftHeight] = useState(0);
  const [showChat, setShowChat] = useState(false);
  const [topUsers, setTopUsers] = useState([]);
  const [myUser, setMyUser] = useState(null);
  const [personAhead, setPersonAhead] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [capacity, setCapacity] = useState(null);
  const [monthlyDonation, setMonthlyDonation] = useState(null);
  const [remaining, setRemaining] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (leftRef.current) setLeftHeight(leftRef.current.offsetHeight);
  }, []);

  // Load smart prediction data from backend API
  useEffect(() => {
    async function fetchAIPrediction() {
      if (!myUser) return;

      try {
        const res = await fetch(
          `http://127.0.0.1:5000/predict/${myUser.User_ID}`
        );

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const data = await res.json();
        setAnalysis(data);
      } catch (err) {
        console.error("Error fetching AI prediction data:", err);
        setError(err.message);
      }
    }

    fetchAIPrediction();
  }, [myUser]);

  // Load electricity data from backend API
  useEffect(() => {
    async function loadElectricity() {
      if (!myUser) return;

      const res = await fetch(
        `http://127.0.0.1:5000/api/user-electricity/${myUser.User_ID}`
      );
      const data = await res.json();

      if (res.ok) {
        setCapacity(data.capacity);
        setMonthlyDonation(data.donated);
        setRemaining(data.remaining); // <-- capacity - donation (CALCULATED)
      } else {
        console.error("Backend error:", data);
      }

      setLoading(false);
    }

    loadElectricity();
  }, [myUser]);

  // Load leaderboard, user, person ahead info from backend API
  useEffect(() => {
    async function fetchAll() {

      const MY_USER_ID = parseInt(localStorage.getItem("user_id"));
      if (!MY_USER_ID) {
        console.error("Missing user_id in localStorage!");
        return;
      }

      try {
        // 1. Leaderboard
        let res = await fetch(`http://127.0.0.1:5000/api/leaderboard?user_id=${MY_USER_ID}`);
        let data = await res.json();
        setTopUsers(data.leaderboard);

        // 2. User info
        res = await fetch(`http://127.0.0.1:5000/user/${MY_USER_ID}/position`);
        let myData = await res.json();
        setMyUser(myData);

        // 3. Person ahead info
        const resPrev = await fetch(`http://127.0.0.1:5000/user/${MY_USER_ID}/previous`);
        if (resPrev.ok) {
          setPersonAhead(await resPrev.json());
        }
      } catch (err) {
        console.error(err);
      }
    }

    fetchAll();
  }, []);

  return (

    <div className={`transition-all duration-300 ${showChat ? "w-[70%]" : "w-full"}`}>
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
            onClick={() => navigate("/")}
            className="ml-[20px] px-4 py-2 rounded-full bg-black/10 text-black font-medium 
                        backdrop-blur hover:bg-white/30 transition justify-self-start"
          >
            ← Log Out
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

          {/* RIGHT — User Info */}
          <div className="flex justify-end items-center pr-6">

            {myUser && (
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
            )}

          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-24 px-6">
        <h2 className="text-4xl font-bold">Your Impact Dashboard</h2>
        <p className="text-gray-600">Track your contributions and see your impact grow</p>

        <div className="flex gap-8 mt-6 items-start flex-col lg:flex-row">

          {/* LEFT */}
          <div ref={leftRef} className="flex-1 w-full">
            <Overview myUser={myUser} analysis={analysis} capacity={capacity} monthlyDonation={monthlyDonation} remaining={remaining} loading={loading} />
          </div>

          {/* RIGHT */}
          <Leaderboard
            topUsers={topUsers}
            myUser={myUser}
            personAhead={personAhead}
            leftHeight={leftHeight}
          />
        </div>
        
        <div style={{ marginTop: "2rem" }}>
          <div className="mb-20">
            <SmartPrediction myUser={myUser} analysis={analysis} remaining={remaining} />
          </div>
        </div>
      </div>

      {/* Floating Chat Button */}
      {!showChat && (
        <button
          onClick={() => setShowChat(true)}
          className="fixed bottom-6 right-6 bg-[#6C00FF] text-white p-4 rounded-full shadow-xl
                    hover:bg-[#5A32FF] transition flex items-center justify-center gap-2 z-[99999]"
        >
          <MessageCircle size={22} />
          <span>Chat Now</span>
        </button>
      )}
      {showChat && <ChatPanel onClose={() => setShowChat(false)} />}

    </div>
  );
}
