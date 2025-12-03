import { useEffect, useState } from "react";

export default function SmartPrediction({ myUser, analysis }) {
  const [error, setError] = useState(null);

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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="bg-[#E2D9FF] rounded-xl p-4">
            <p className="text-gray-700 text-sm">Your Trend</p>
            <p className="text-2xl font-bold mt-1">

              {analysis?.userTrend > 0 ? (
                <span style={{ color: "green" }}> Rising &#8599;</span>  // Rising arrow
              ) : analysis?.userTrend < 0 ? (
                <span style={{ color: "red" }}> Declining &#8601;</span>    // Declining arrow
              ) : (
                <span style={{ color: "gray" }}>Normal &#8594;</span>   // Neutral
              )}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Keep going.
            </p>
          </div>

          <div className="bg-[#E2D9FF] rounded-xl p-4">
            <p className="text-gray-700 text-sm">Rank Probability</p>
            <p className="text-2xl font-bold mt-1">
              {analysis.rankProbability} %
            </p>
            <p className="text-sm text-gray-600 mt-1">
              likely you can catch up #{myUser.Rank - 1} next month
            </p>
          </div>

          <div className="bg-[#E2D9FF] rounded-xl p-4">
            <p className="text-gray-700 text-sm">Competitor Momentum</p>
            <p className="text-2xl font-bold mt-1">
              {analysis.competitorMomentum} %
            </p>
            <p className="text-sm text-gray-600 mt-1">
              likely the #{myUser.Rank - 1} will donate next month
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
        <h4 className="text-lg font-bold text-gray-900 m-4">
          Tips
        </h4>
        {analysis?.tips?.map((tip, i) => (
          <div className="mt-4 bg-[#EFE8FF] rounded-xl p-4 flex items-start gap-2 text-gray-700">
            <p className="text-sm">
              <span key={i}>
                {i + 1}. {tip}
                <br />
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
