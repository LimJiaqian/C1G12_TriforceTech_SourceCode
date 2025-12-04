import { useEffect, useState } from "react";

// Indigo/Purple Palette
const ACCENT_COLOR_HEX = "#4f46e5";
const ACCENT_COLOR = "text-indigo-600";
const SECTION_BG = "bg-indigo-50";

/* ----------------------------------------------------
   Donut Chart Component
---------------------------------------------------- */
const DonutChart = ({ percentage, color, textColor, label, insight }) => {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;

  const strokeDashoffset =
    percentage !== 0
      ? circumference - (percentage / 100) * circumference
      : circumference;

  return (
    <div className="flex flex-col items-center p-2">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke="#e0e7ff"
            strokeWidth="15"
          />
          <circle
            cx="60"
            cy="60"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="15"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            style={{ strokeLinecap: "round" }}
          />
        </svg>

        <div className="absolute inset-0 flex items-center justify-center">
          <p className={`text-2xl font-bold`} style={{ color: textColor }}>
            {percentage}
            <span className="text-lg">%</span>
          </p>
        </div>
      </div>

      <p className="text-sm font-medium text-gray-700 mt-2">{label}</p>
      <p className="text-xs text-gray-500 text-center mt-1">{insight}</p>
    </div>
  );
};

/* ----------------------------------------------------
   Trend Indicator
---------------------------------------------------- */
const TrendIndicator = ({ trend }) => {
  let text, color, arrow, barClass, insight;

  if (trend > 0) {
    text = "Rising";
    color = "text-green-600";
    arrow = "↑";
    barClass = "bg-green-400 w-full";
    insight = "Great progress! Keep this upward momentum to secure your rank.";
  } else if (trend < 0) {
    text = "Declining";
    color = "text-red-600";
    arrow = "↓";
    barClass = "bg-red-400 w-1/3";
    insight =
      "Your trend dipped slightly. Focus on one 'Tip' below to get back on track.";
  } else {
    text = "Neutral";
    color = "text-gray-500";
    arrow = "→";
    barClass = "bg-gray-400 w-2/3";
    insight =
      "You're maintaining a steady level. A small push is needed to climb the ranks.";
  }

  return (
    <div className="p-1">
      <p className="text-gray-700 text-sm font-medium">Your Donation Momentum</p>

      <div className={`text-2xl font-bold mt-1 flex items-center ${color}`}>
        {text}
        <span className="text-5xl ml-2">{arrow}</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-2 mt-2 overflow-hidden">
        <div className={`h-2 rounded-full transition-all duration-700 ${barClass}`} />
      </div>

      <p className="text-sm text-gray-600 mt-2">{insight}</p>
    </div>
  );
};

/* ----------------------------------------------------
   Goal Comparison Card (Fixed Broken JSX)
---------------------------------------------------- */
const GoalComparisonCard = ({ savedKwh, minRequired, maxNeeded, rank, remaining }) => {
  const isBehind = remaining > minRequired;

  return (
    <div
      className={`mt-6 p-5 rounded-xl border-2 shadow-lg bg-white ${isBehind ? "border-[#6C00FF]" : "border-green-300"
        }`}
    >
      <p className="text-lg font-bold">
        {isBehind ? (
          <>
            You need to save about{" "}
            <span className="text-3xl font-extrabold text-[#6C00FF] m-2">
              {(maxNeeded + minRequired) / 2} kWh
            </span>{" "}
            to surpass Rank #{rank} next month
          </>
        ) : (
          <>You're ahead of the minimum goal for Rank #{rank}!</>
        )}
      </p>

      <p className="text-sm mt-2 text-gray-600">
        Minimum Required: <strong>{minRequired} kWh</strong>
        <br />
        <span style={{ fontSize: "10px" }}>This is the minimum threshold to secure the next rank.</span>
        <br /><br />
        Current Balance: <strong>{remaining} kWh</strong>
        <br /><br />

        Maximum Target (Safe Zone): <strong>{maxNeeded} kWh</strong>
        <br />
        <span style={{ fontSize: "10px" }}>This is the ideal range. Reaching this ensures you have a buffer and remain safe even if trends fluctuate.</span>
        <br /><br />
      </p>
    </div>
  );
};

/* ----------------------------------------------------
   DataBox Wrapper
---------------------------------------------------- */
const DataBox = ({ children }) => (
  <div className="bg-white rounded-xl p-4 shadow-md border border-indigo-100 transition-all duration-200 transform hover:shadow-lg hover:bg-indigo-50">
    {children}
  </div>
);

/* ----------------------------------------------------
   Splash Screen
---------------------------------------------------- */
const SplashScreen = () => (
  <div className="w-full h-80 flex flex-col items-center justify-center bg-white rounded-xl shadow-2xl animate-pulse">
    <div className={`text-4xl font-extrabold ${ACCENT_COLOR}`}>Smart Prediction</div>
    <div className="text-lg text-gray-500 mt-3">Analyzing your ranking data...</div>
  </div>
);

/* ----------------------------------------------------
   Main Component
---------------------------------------------------- */
export default function SmartPrediction({ myUser, analysis, remaining }) {
  const [error, setError] = useState(null);
  const [showSplash, setShowSplash] = useState(true);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!showSplash && analysis) setIsMounted(true);
  }, [showSplash, analysis]);

  if (showSplash) return <SplashScreen />;

  if (!analysis)
    return (
      <div className="w-full bg-white rounded-xl p-6 shadow-md text-center">
        {error ? <p className="text-red-500">Error: {error}</p> : <p className="text-gray-500">Loading Smart Prediction...</p>}
      </div>
    );

  return (
    <div
      className={`w-full bg-white rounded-xl p-6 shadow-2xl transition-all duration-700 ${isMounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
    >
      {/* Header */}
      <h3 className={`text-xl font-bold ${ACCENT_COLOR}`}>Smart Prediction</h3>

      <p className="mt-1 text-gray-700 border-b border-indigo-200 pb-4 flex items-center gap-2">
        You are currently
        <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-md">
          Rank #{myUser.Rank}
        </span>
        Donate{" "}
        <span className={`font-semibold ${ACCENT_COLOR}`}>
          {analysis.savedKwh} kWh
        </span>{" "}
        now to climb!
      </p>

      {/* Insights Area */}
      <div className={`${SECTION_BG} mt-5 rounded-xl p-6`}>
        <h4 className="text-lg font-bold text-gray-900 mb-4">
          Actionable Insights to Reach Rank #{myUser.Rank - 1}
        </h4>

        <GoalComparisonCard
          savedKwh={analysis.savedKwh}
          minRequired={analysis.minRequired}
          maxNeeded={analysis.maxNeeded}
          rank={myUser.Rank - 1}
          remaining={remaining}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-2">
              Your Chance to Climb Rank
            </h5>
            <DonutChart
              percentage={analysis.rankProbability}
              color={ACCENT_COLOR_HEX}
              textColor="#f97316"
              label="Probability of Overtaking"
              insight={`Based on your current trend, you have a ${analysis.rankProbability}% chance of reaching rank #${myUser.Rank - 1
                } next month.`}
            />
            <span style={{ fontSize: "10px", fontWeight: "bold" }}>Actionable Tip:</span>
            <ul style={{ fontSize: "8px" }}>
              {analysis.rankProbability > 70 ? (
                // --- IF Probability is ABOVE 70% (High Confidence) ---
                <>
                  <li>1. <b>Secure Rank:</b> You are highly likely to succeed! Focus on consistently exceeding the Maximum Target of {analysis.maxNeeded} kWh to lock in the rank.</li>
                  <li>2. <b>Sustain Pace:</b> Maintain your current high upward momentum to prevent any last-minute counter-effort from competitors.</li>
                </>
              ) : (
                // --- ELSE Probability is 70% or BELOW (Needs Active Improvement) ---
                <>
                  <li>1. <b>Prioritize Target:</b> To significantly improve your odds, consistently aim for the Maximum Target of {analysis.maxNeeded} kWh.</li>
                  <li>2. <b>Consistency is Key:</b> Implement regular monitoring and maintain consistent contributions to actively increase your probability.</li>
                </>
              )}
            </ul>
          </DataBox>

          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-2">
              Competitor's Focus Level
            </h5>
            <DonutChart
              percentage={analysis.competitorMomentum}
              color="#f97316"
              textColor={ACCENT_COLOR_HEX}
              label={`Rank #${myUser.Rank - 1} Momentum`}
              // --- Conditional Insight Implementation ---
              insight={analysis.competitorMomentum > 70
                ? "High momentum means your competitor is likely to donate again. Plan for the Maximum Target."
                : "Lower momentum suggests the competitor is less active. Focus on maintaining your own consistency to easily increase the gap."
              }
              percentageColor={ACCENT_COLOR_HEX}
            />
            <span style={{ fontSize: "10px", fontWeight: "bold" }}>Actionable Tip:</span>
            <ul style={{ fontSize: "8px" }}>
              {analysis.competitorMomentum > 70 ? (
                // --- IF Competitor Momentum is ABOVE 70% (High Threat) ---
                <>
                  <li>1. <b>Mandatory Minimum:</b> You must hit or exceed the Maximum Target of {analysis.maxNeeded} kWh to avoid being surpassed.</li>
                  <li>2. <b>Immediate Response:</b> Counter every competitor contribution instantly to prevent their momentum from building.</li>
                </>
              ) : (
                // --- ELSE Competitor Momentum is 70% or BELOW (Standard Effort) ---
                <>
                  <li>1. <b>Sustained Effort:</b> Focus on consistent, daily contributions to easily surpass the Maximum Target of {analysis.maxNeeded} kWh.</li>
                  <li>2. <b>Maintain Trajectory:</b> Regularly monitor your own probability and ensure your Donation Momentum remains **Rising** to secure the lead.</li>
                </>
              )}
            </ul>
          </DataBox>

          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-10">
              Is Your Trajectory Correct?
            </h5>
            <TrendIndicator trend={analysis.userTrend} />
          </DataBox>
        </div>

        {/* Pro Tip */}
        <div className="mt-8 bg-white rounded-xl p-4 flex items-center gap-2 text-gray-700 border-l-4 border-indigo-400 shadow-inner">
          <span className={`text-xl ${ACCENT_COLOR}`}>💡</span>
          <p className="text-sm">
            Aim for <strong>{analysis.maxNeeded} kWh</strong> to secure your spot.
            Top donors often increase contributions near month end.
          </p>
        </div>

        {/* Tips List */}
        <h4 className="text-lg font-bold text-gray-900 mt-4">
          Tips to Save More Energy
        </h4>

        <div className="space-y-3 mt-4">
          {analysis.tips?.map((tip, i) => (
            <div
              key={i}
              className="bg-white rounded-xl p-4 flex items-center gap-3 text-gray-700 shadow-sm border border-indigo-50"
            >
              <span className={`text-lg font-bold ${ACCENT_COLOR}`}>{i + 1}.</span>
              <p className="text-sm leading-relaxed">{tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
