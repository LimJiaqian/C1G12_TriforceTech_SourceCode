import { useState, useEffect } from "react";
import { Zap, Leaf } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Overview({ myUser }) {
  const navigate = useNavigate();

  const [capacity, setCapacity] = useState(null);
  const [monthlyDonation, setMonthlyDonation] = useState(null);
  const [remaining, setRemaining] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastDonation, setLastDonation] = useState(null);
  const [txnLoading, setTxnLoading] = useState(true);


  // Load electricity data from backend API
  useEffect(() => {
    if (!myUser) return;

    async function loadAll() {
      try {
        // --- Load electricity summary ---
        const elecRes = await fetch(
          `http://127.0.0.1:5000/api/user-electricity/${myUser.User_ID}`
        );
        const elecData = await elecRes.json();

        if (elecRes.ok) {
          setCapacity(elecData.capacity);
          setMonthlyDonation(elecData.donated);
          setRemaining(elecData.remaining);
        } else {
          console.error("Electricity API error:", elecData);
        }

        // --- Load last donation ---
        const txnRes = await fetch(
          `http://127.0.0.1:5000/api/transactions/${myUser.User_ID}`
        );
        const txnData = await txnRes.json();

        if (Array.isArray(txnData) && txnData.length > 0) {
          setLastDonation(txnData[0]);   // newest transaction
        }

      } catch (err) {
        console.error("Overview API error:", err);
      } finally {
        setLoading(false);
        setTxnLoading(false);
      }
    }

    loadAll();
  }, [myUser]);


  // Impact calculator
  const calcImpact = (kwh) => {
    if (!capacity) return { hours: 0, co2: 0, trees: 0 };

    const hours = Math.round((kwh / capacity) * 262);
    const co2 = Math.round((kwh / capacity) * 700.8);
    const trees = Math.round(co2 / 21);

    return { hours, co2, trees };
  };

  const [donateAmount, setDonateAmount] = useState(50);

  if (!myUser || loading || capacity === null) {
    return (
      <div className="bg-white shadow-md rounded-xl p-6 w-full text-center">
        Loading your energy overview...
      </div>
    );
  }

  const impact = calcImpact(donateAmount);
  const totalImpact = calcImpact(monthlyDonation); // Correct: use Supabase monthly donation

  return (
    <div className="space-y-8">
      <div className="bg-white shadow-md rounded-xl p-6 w-full">

        {/* Title */}
        <div className="flex items-center gap-2 mb-4">
          <Zap className="text-yellow-400" />
          <h3 className="font-bold text-3xl">Your Energy Overview</h3>
        </div>

        {/* Electricity Capacity */}
        <div className="mb-6">
          <div className="flex justify-between text-blue-500 font-semibold mb-1">
            <span>Electricity Capacity</span>
            <span>{capacity} kWh</span>
          </div>

          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-blue-500 w-full"></div>
          </div>
        </div>

        {/* Remaining This Month */}
        <div className="mb-6">
          <div className="flex justify-between text-purple-600 font-semibold mb-1">
            <span>Remaining This Month</span>
            <span>{remaining} kWh</span>
          </div>

          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500"
              style={{ width: `${(remaining / capacity) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Total Donated */}
        <div className="mb-6">
          <div className="flex justify-between text-[#6C00FF] font-semibold mb-1">
            <span>Total Donated</span>
            <span>{monthlyDonation} kWh</span> {/* FIXED */}
          </div>

          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-[#6C00FF]"
              style={{
                width: `${(monthlyDonation / capacity) * 100}%`,
              }}
            ></div>
          </div>
        </div>

        {/* Carbon Offset + Trees Saved */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">

          <div className="p-4 bg-green-50 rounded-xl flex items-center gap-2">
            <Leaf className="text-green-600 text-2xl" />
            <div>
              <p className="text-gray-500 text-sm">Carbon Offset</p>
              <p className="font-bold text-green-700 text-xl">
                {totalImpact.co2} kg CO₂
              </p>
            </div>
          </div>

          <div className="p-4 bg-yellow-50 rounded-xl flex items-center gap-2">
            <span className="text-2xl">🌳</span>
            <div>
              <p className="text-gray-500 text-sm">Trees Saved</p>
              <p className="font-bold text-yellow-700 text-xl">
                {totalImpact.trees} trees
              </p>
            </div>
          </div>

        </div>

        {/* Slider */}
        <div className="mb-6">
          <p className="font-semibold mb-2 text-gray-800">
            Select Donation Amount: <span className="text-[#3f4cc6ff]">{donateAmount} kWh</span>
          </p>

          <input
            type="range"
            min={0}
            max={remaining}
            value={donateAmount}
            onChange={(e) => setDonateAmount(Number(e.target.value))}
            className="
              w-full
              h-3
              rounded-full
              bg-gray-300
              appearance-none
              cursor-pointer
              accent-purple-600
              relative
            "
            style={{
              background: `linear-gradient(to right, #3f4cc6ff ${(donateAmount/remaining)*100}%, #E5E7EB ${(donateAmount/remaining)*100}%)`,
              borderRadius: "50px"
            }}
          />

          <style>{`
            input[type="range"]::-webkit-slider-thumb {
              -webkit-appearance: none;
              appearance: none;
              width: 22px;
              height: 22px;
              border-radius: 50%;
              background: #3f4cc6ff;
              border: 3px solid white;
              box-shadow: 0 0 6px rgba(0,0,0,0.2);
              cursor: pointer;
            }
            input[type="range"]::-moz-range-thumb {
              width: 22px;
              height: 22px;
              border-radius: 50%;
              background: #6C00FF;
              border: 3px solid white;
              box-shadow: 0 0 6px rgba(0,0,0,0.2);
              cursor: pointer;
            }
          `}</style>
        </div>


        {/* Estimated Impact */}
        <div className="p-4 bg-purple-50 rounded-xl mb-6">
          <h4 className="text-purple-700 font-bold mb-2">Estimated Impact:</h4>
          <ul className="text-gray-700 text-sm list-disc ml-4">
            <li>Powers equipment for ~{impact.hours} hours</li>
            <li>Saves {impact.co2} kg CO₂</li>
            <li>JARIAH certificate provided</li>
          </ul>
        </div>

        {/* Donate Button */}
        <button
          onClick={() => {
            localStorage.setItem(
              "selectedDonationAmount",
              donateAmount.toString()
            );
            navigate("/donate");
          }}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-500 via-purple-600 to-[#6C00FF] text-white font-bold text-lg flex justify-center items-center gap-2"
        >
          <Zap />
          Donate Now
        </button>

      {/* --- Separate Recent Donation / History Box --- */}
          <div className="bg-[#3f4cc6ff]/20 shadow-md rounded-xl p-6 w-full mt-8">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-bold text-2xl text-blue-700">Recent Donation</h4>
              <button
                onClick={() => navigate("/donation_history", { state: { myUser } })}
                className=" px-4 py-2 rounded-lg border border-blue-600 text-blue-600 font-semibold hover:bg-blue-500 hover:text-white transitiontext-sm"
              >
                View Full History
              </button>
            </div>

            {/* Recent donation line */}
            <p className="text-gray-700 text-sm pl-5">
              {txnLoading ? (
                "Loading recent donation..."
              ) : lastDonation ? (
                <p className="text-gray-700 text-lg pl-5">
                  Last donation: 
                  <span className="font-bold text-[#3f4cc6ff] ml-1">
                    {lastDonation.Donation_kwh} kWh
                  </span>
                  <span className="mx-2 text-gray-400">•</span>
                  <span className="text-gray-600">
                    {new Date(lastDonation.Date_Time.replace(" ", "T")).toLocaleDateString("en-MY")}
                  </span>
                </p>
              ) : (
                "You haven't made any donations yet."
              )}
            </p>
          </div>
      </div>
    </div>
  );
}
