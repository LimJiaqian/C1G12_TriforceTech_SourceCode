import { useEffect, useState } from "react";

export default function SmartPrediction({ myUser }) {
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      if (!myUser) return;

      try {
        const res = await fetch(
          `http://127.0.0.1:5000/user/${myUser.User_ID}/ai-analysis`
        );

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const data = await res.json();
        setAnalysis(data.ai_analysis);
      } catch (err) {
        console.error("Error fetching AI analysis data:", err);
        setError(err.message);
      }
    }

    fetchData();
  }, [myUser]);

  if (!analysis) {
    return (
      <div className="w-full bg-[#F4EEFF] rounded-xl p-6 shadow-md text-center">
        {error ? (
          <p className="text-red-500">Error: {error}</p>
        ) : (
          <p className="text-gray-500">Loading Smart Prediction...</p>
        )}
      </div>
    );
  }

  return (
    <div className="w-full bg-[#F4EEFF] rounded-xl p-6 shadow-md">
      <h3 className="text-xl font-bold text-[#6C00FF]">Smart Prediction</h3>
      <p className="mt-1 text-gray-700">
        Save{" "}
        <span className="font-semibold text-[#6C00FF]">
          {analysis.savedKwh} kWh
        </span>{" "}
        next month to climb the leaderboard!
      </p>

      <div className="mt-5 bg-[#EAE2FF] rounded-xl p-6">
        <h4 className="text-lg font-bold text-gray-900 mb-4">
          To Reach Next Donor Level (Rank #{myUser.Rank - 1})
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-[#E2D9FF] rounded-xl p-4">
            <p className="text-gray-700 text-sm">Minimum Required</p>
            <p className="text-2xl font-bold mt-1">
              {analysis.minRequired} kWh
            </p>
            <p className="text-sm text-gray-600 mt-1">
              If rank #{myUser.Rank - 1} doesn't donate more this month
            </p>
          </div>

          <div className="bg-[#E2D9FF] rounded-xl p-4">
            <p className="text-gray-700 text-sm">Maximum Needed</p>
            <p className="text-2xl font-bold mt-1">
              {analysis.maxNeeded} kWh
            </p>
            <p className="text-sm text-gray-600 mt-1">
              If rank #{myUser.Rank - 1} also donates ~{analysis.savedKwh} kWh
              more
            </p>
          </div>
        </div>

        <div className="mt-4 bg-[#EFE8FF] rounded-xl p-4 flex items-start gap-2 text-gray-700">
          <span className="text-xl">💡</span>
          <p className="text-sm">
            Pro Tip: Aim for <strong>{analysis.maxNeeded} kWh</strong> to secure
            your spot — top donors often increase contributions near month-end!
          </p>
        </div>
      </div>
    </div>
  );
}
