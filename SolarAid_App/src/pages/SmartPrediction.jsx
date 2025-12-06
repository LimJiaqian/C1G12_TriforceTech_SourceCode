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
  const validPercentage = Math.min(100, Math.max(0, percentage));
  const strokeDashoffset =
    validPercentage !== 0
      ? circumference - (validPercentage / 100) * circumference
      : circumference;

  return (
    <div className="flex flex-col items-center p-2">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#e0e7ff" strokeWidth="15" />
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
            {validPercentage}<span className="text-lg">%</span>
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
  if (trend > 0.1) {
    text = "Rising";
    color = "text-green-600";
    arrow = "↑";
    barClass = "bg-green-400 w-full";
    insight = "Great progress! Keep this upward momentum.";
  } else if (trend < -0.1) {
    text = "Declining";
    color = "text-red-600";
    arrow = "↓";
    barClass = "bg-red-400 w-1/3";
    insight = "Your trend dipped slightly. Focus on the tips below.";
  } else {
    text = "Stable";
    color = "text-gray-500";
    arrow = "→";
    barClass = "bg-gray-400 w-2/3";
    insight = "You're maintaining a steady level.";
  }

  return (
    <div className="p-1">
      <p className="text-gray-700 text-sm font-medium">Your Donation Momentum</p>
      <div className={`text-2xl font-bold mt-1 flex items-center ${color}`}>
        {text}<span className="text-5xl ml-2">{arrow}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2 mt-2 overflow-hidden">
        <div className={`h-2 rounded-full transition-all duration-700 ${barClass}`} />
      </div>
      <p className="text-sm text-gray-600 mt-2">{insight}</p>
    </div>
  );
};

/* ----------------------------------------------------
   Goal Comparison Card
---------------------------------------------------- */
const GoalComparisonCard = ({ minRequired, maxNeeded, currentGap, mode, rank, summary }) => {
  const isAttack = mode === 'attack';
  const isSafe = !isAttack ? (currentGap > 10) : (currentGap <= 0);
  const safeGap = Math.abs(currentGap).toFixed(2);
  const overtakeAmount = (Math.abs(currentGap) + 1).toFixed(2);

  return (
    <div
      className={`mt-6 p-5 rounded-xl border-2 shadow-lg bg-white ${!isSafe ? "border-[#6C00FF]" : "border-green-300"}`}
    >
      <p className="text-sm font-bold">
        <span className="text-lg">{summary}</span> <br />

        {isAttack ? (
          <>
            <br />
            Save <span className="text-2xl font-extrabold text-[#6C00FF] m-2">{minRequired} kWh</span> more.
          </>
        ) : (
          <>
            Maintain a buffer of <span className="text-2xl font-extrabold text-green-600 m-2">{minRequired} kWh</span>
            to stay ahead of the chaser.
          </>
        )}
      </p>

      <p className="text-sm mt-2 text-gray-600 leading-relaxed">
        <br />
        Current {isAttack ? "Gap" : "Lead"}: <strong>{safeGap} kWh</strong>
        <br />
        <span className="text-[10px] text-gray-500 block mt-1">
          {isAttack
            ? `Donate ${overtakeAmount} kWh now to achieve the target!`
            : `You are ahead by ${safeGap} kWh. Maintain your lead!`}
        </span>
        <br />
        Minimum Target: <strong>{minRequired} kWh</strong>
        <br />
        <span className="text-[10px] text-gray-500 block mt-1">
          {isAttack
            ? "This is the minimum energy needed to close the gap."
            : "This is the minimum buffer to avoid being overtaken."}
        </span>
        <br />
        Maximum Target: <strong>{maxNeeded} kWh</strong>
        <br />
        <span className="text-[10px] text-gray-500 block mt-1">
          {isAttack
            ? "Reaching this safely secures the higher rank."
            : "Reaching this completely blocks the chaser from catching up."}
        </span>
        <br />
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
   Splash Screen (Refined with Visuals)
---------------------------------------------------- */
const AIProcessingVisual = ({ progress }) => {
  // Determine visual stage
  const isAnalyzing = progress > 30 && progress < 100;
  const isFinalizing = progress == 80;

  return (
    <div className="relative w-32 h-32 mb-6">
      {/* Outer Pulse Rings */}
      <div className="absolute inset-0 border-4 border-indigo-100 rounded-full animate-[ping_3s_linear_infinite]"></div>
      <div className="absolute inset-0 border-4 border-indigo-50 rounded-full animate-[ping_3s_linear_infinite_1.5s]"></div>

      {/* Central Hub */}
      <div className="absolute inset-0 flex items-center justify-center bg-white rounded-full shadow-lg border-2 border-indigo-100 z-10">
        {/* Dynamic Icon based on stage */}
        {!isFinalizing ? (
          // Neural Network Icon
          <svg className={`w-16 h-16 text-indigo-600 ${isAnalyzing ? 'animate-pulse' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            {/* Central Node */}
            <circle cx="12" cy="12" r="3" fill="#e0e7ff" />

            {/* Satellite Nodes */}
            <circle cx="6" cy="6" r="2" />
            <circle cx="18" cy="6" r="2" />
            <circle cx="6" cy="18" r="2" />
            <circle cx="18" cy="18" r="2" />

            {/* Connections */}
            <path d="M10 10L7.5 7.5M14 10L16.5 7.5M10 14L7.5 16.5M14 14L16.5 16.5" strokeLinecap="round" />
          </svg>
        ) : (
          <svg className="w-14 h-14 text-green-500 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {/* Check/Success Icon */}
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
      </div>

      {/* REMOVED: Orbiting particles (Three dots on circle) */}
    </div>
  );
};

const SplashScreen = ({ predictionStatus, localProgress = 0 }) => (
  <div className="w-full h-96 flex flex-col items-center justify-center bg-white rounded-xl shadow-2xl overflow-hidden relative">
    {/* Background Grid Pattern */}
    <div className="absolute inset-0 opacity-5"
      style={{ backgroundImage: 'radial-gradient(#4f46e5 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
    </div>

    <div className="z-10 flex flex-col items-center">
      <h2 className={`text-3xl font-extrabold ${ACCENT_COLOR} mb-1 tracking-tight`}>Smart Prediction</h2>
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-8">Powered by Cloudflare Workers AI</p>

      {/* Visual Animation */}
      <AIProcessingVisual progress={localProgress} />

      {/* Status Text */}
      <div className="h-6 mb-3">
        <span className="text-sm font-medium text-gray-600 animate-pulse">
          {predictionStatus || "Initializing Neural Network..."}
        </span>
      </div>

      {/* Enhanced Progress Bar */}
      <div className="w-72 relative">
        <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden shadow-inner border border-gray-200">
          <div
            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-full transition-all duration-500 ease-out relative"
            style={{ width: `${localProgress}%`, backgroundSize: '200% 100%' }}
          >
            {/* Shimmer Effect */}
            <div className="absolute inset-0 w-full h-full bg-white opacity-20 animate-[shimmer_2s_infinite]"
              style={{ backgroundImage: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)' }}>
            </div>
          </div>
        </div>
        <div className="flex justify-between mt-2 px-1">
          <span className="text-[10px] text-gray-400">Data</span>
          <span className="text-[10px] text-gray-400 font-bold">{localProgress}%</span>
          <span className="text-[10px] text-gray-400">Analysis</span>
        </div>
      </div>
    </div>
  </div>
);

/* ----------------------------------------------------
   Main Component
---------------------------------------------------- */
export default function SmartPrediction({ myUser, analysis: propAnalysis, predictionStatus, predictionProgress }) {
  const [analysis, setAnalysis] = useState(propAnalysis || null);
  const [isMounted, setIsMounted] = useState(false);
  const [activeTab, setActiveTab] = useState("attack");
  const [localProgress, setLocalProgress] = useState(0);

  // Keep local progress synced, but never let it decrease
  useEffect(() => {
    if (predictionProgress > localProgress) {
      setLocalProgress(predictionProgress);
    }
  }, [predictionProgress, localProgress]);

  // Update analysis when prop changes and trigger fade-in
  useEffect(() => {
    if (propAnalysis && predictionProgress == 100) {
      setAnalysis(propAnalysis);
      // Keep progress at 100% during transition
      setLocalProgress(100);

      // Wait 500ms before showing analysis (let progress bar complete)
      const analysisTimer = setTimeout(() => {
        setAnalysis(propAnalysis);

        // Then trigger fade-in animation after another small delay
        const fadeTimer = setTimeout(() => setIsMounted(true), 100);

        // Default to 'defend' if user is #1, otherwise 'attack'
        if (propAnalysis.position?.isTopRanked) {
          setActiveTab("defend");
        }

        return () => clearTimeout(fadeTimer);
      }, 500);


      return () => clearTimeout(analysisTimer);
    }
  }, [propAnalysis]);

  if (!analysis) return <SplashScreen predictionStatus={predictionStatus} localProgress={localProgress} />;

  // Destructure Data
  const { catchUp, defense, position } = analysis;
  const isTopRanked = position?.isTopRanked || false;
  const isBottomRanked = position?.isBottomRanked || false;
  const isAttackMode = activeTab === "attack";
  const primaryMetric = isAttackMode ? catchUp : defense;

  const probabilityLabel = isAttackMode ? "Probability of Overtaking" : "Risk of Overtake";
  const probabilityValue = isAttackMode ? primaryMetric.overtakeProbability : primaryMetric.overtakeRisk;
  const probabilityColor = isAttackMode ? ACCENT_COLOR_HEX : "#ef4444";
  const opponentMomentumLabel = isAttackMode ? "Competitor's Momentum" : "Chaser's Momentum";
  const opponentMomentumValue = isAttackMode ? primaryMetric.competitorMomentum : primaryMetric.chaserMomentum;
  const minReq = isAttackMode ? primaryMetric.minRequired : primaryMetric.bufferRecommended;
  const maxNeed = isAttackMode ? primaryMetric.maxNeeded : (primaryMetric.bufferRecommended * 1.5).toFixed(2);
  const currentGapOrBuffer = isAttackMode ? primaryMetric.currentGap : primaryMetric.currentBuffer;
  const summary = primaryMetric.summary

  return (
    <div
      className={`w-full bg-white rounded-xl p-6 shadow-2xl transition-all duration-700 ${isMounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
    >
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className={`text-xl font-bold ${ACCENT_COLOR}`}>Smart Prediction</h3>
          <div className="mt-1 flex items-center gap-2">
            <span className="text-gray-600 text-sm">You are currently</span>
            <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-md">
              Rank #{myUser?.Rank || "?"}
            </span>
          </div>

          {/* Mini Status bar if refreshing in background */}
          {predictionStatus && predictionStatus !== "Complete" && (
            <div className="mt-2 text-[10px] text-gray-400 flex items-center gap-2">
              <span className="animate-pulse">●</span> Updating live data...
            </div>
          )}
        </div>

        {/* TAB SWITCHER */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab("attack")}
            className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all ${activeTab === "attack" ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500 hover:text-gray-700"
              }`}
          >
            Climb Rank
          </button>
          {!isBottomRanked && (
            <button
              onClick={() => setActiveTab("defend")}
              className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all ${activeTab === "defend" ? "bg-white text-red-500 shadow-sm" : "text-gray-500 hover:text-gray-700"
                }`}
            >
              Secure Spot
            </button>
          )}
        </div>
      </div>

      {/* Insights Area */}
      <div className={`${SECTION_BG} mt-5 rounded-xl p-6`}>
        <h4 className="text-lg font-bold text-gray-900 mb-4">
          {isAttackMode
            ? `Strategy to ${isTopRanked ? "Exceed Your Record" : 'Overtake Rank #' + (myUser?.Rank - 1)}`
            : `Defensive Strategy vs. Rank #${isBottomRanked ? "None" : myUser?.Rank + 1}`
          }
        </h4>

        <GoalComparisonCard
          minRequired={minReq}
          maxNeeded={maxNeed}
          currentGap={currentGapOrBuffer}
          mode={activeTab}
          rank={myUser?.Rank - 1}
          summary={summary}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-2">{isAttackMode ? "Chance to Climb" : "Defense Status"}</h5>
            <DonutChart
              percentage={probabilityValue}
              color={probabilityColor}
              textColor={probabilityColor}
              label={probabilityLabel}
              insight={!isAttackMode ? `Current risk of being overtaken is ${probabilityValue}%.` : `You have a ${probabilityValue}% probability of ranking up.`}
            />
          </DataBox>
          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-2">Opponent Activity</h5>
            <DonutChart
              percentage={opponentMomentumValue}
              color="#f97316"
              textColor={ACCENT_COLOR_HEX}
              label={opponentMomentumLabel}
              insight={opponentMomentumValue > 70 ? "High activity detected! They are donating frequently." : "Opponent activity is low. Good chance to make a move."}
            />
          </DataBox>
          <DataBox>
            <h5 className="text-lg font-bold text-gray-900 mb-10">Your Trajectory</h5>
            <TrendIndicator trend={catchUp.userTrend} />
          </DataBox>
        </div>

        <div className="mt-8 bg-white rounded-xl p-4 flex items-center gap-2 text-gray-700 border-l-4 border-indigo-400 shadow-inner">
          <span className={`text-xl ${ACCENT_COLOR}`}>💡</span>
          <p className="text-sm">
            {isAttackMode
              ? `Aim for ${maxNeed} kWh to guarantee you overtake the competitor.`
              : `Keeping a buffer of ${maxNeed} kWh ensures you are safe from sudden spikes.`}
          </p>
        </div>

        <h4 className="text-lg font-bold text-gray-900 mt-4">
          {isAttackMode ? "Overtake Plan: Energy Saving Tips" : "Defense Plan: Sustainability Habits"}
        </h4>

        <div className="space-y-3 mt-4">
          {primaryMetric.tips?.map((tip, i) => (
            <div key={i} className="bg-white rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center gap-3 text-gray-700 shadow-sm border border-indigo-50">
              <div className="flex items-center gap-3 flex-1">
                <span className={`text-lg font-bold ${ACCENT_COLOR}`}>{i + 1}.</span>
                <div>
                  <p className="text-sm font-semibold leading-relaxed">{tip.action}</p>
                  <p className="text-xs text-gray-500 mt-1">Impact: <span className="font-bold text-green-600">+{tip.estimated_kwh} kWh</span></p>
                </div>
              </div>
              <span className={`px-2 py-1 text-xs font-bold uppercase rounded-md whitespace-nowrap ${tip.priority === 'high' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'}`}>
                {tip.priority} Priority
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}