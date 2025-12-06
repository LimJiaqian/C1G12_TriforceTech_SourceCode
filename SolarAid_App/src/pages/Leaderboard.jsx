export default function Leaderboard({ topUsers, myUser, personAhead }) {

  return (
    <div className="w-full lg:w-[380px]">
      <div className="bg-white shadow-md rounded-xl p-6">

        {/* Title */}
        <div className="flex items-center gap-2 mb-6">
          <span className="text-2xl">🏆</span>
          <h3 className="text-2xl font-bold text-[#6C00FF]">Top Donors</h3>
        </div>

        {/* Top 5 */}
        <div className="space-y-3">
          {topUsers.slice(0, 5).map((user, i) => (
            <div
              key={i}
              className={`flex items-center justify-between rounded-lg p-3 transition ${user.User_ID === myUser?.User_ID
                ? "bg-purple-200"             // highlight "YOU"
                : user.User_ID === personAhead?.User_ID
                  ? "bg-purple-100"             // highlight "person ahead"
                  : "bg-gray-100 hover:bg-gray-200"  // normal top users
                }`}
            >
              <div className="flex items-center gap-3">
                <img
                  src={user.User_Img}
                  alt={user.User_Name}
                  className="w-12 h-12 rounded-full object-cover shadow"
                />
                <div>
                  <p className="font-semibold">{user.User_Name}</p>
                  <p className="text-sm text-gray-500">{user.Donate_Amount} kWh</p>
                </div>
              </div>

              <span
                className={`font-bold ${user.User_ID === myUser?.User_ID ? "text-purple-700" : "text-[#6C00FF]"
                  }`}
              >
                #{i + 1}
              </span>
            </div>
          ))}

          {/* If USER is NOT top 5 → show both sections below */}
          {!topUsers.slice(0, 5).some(u => u.User_ID === myUser?.User_ID) && (
            <>

              {/* Show PERSON AHEAD only if they exist AND they are also NOT top 5 */}
              {personAhead &&
                !topUsers.slice(0, 5).some(u => u.User_ID === personAhead.User_ID) && (
                  <div className="flex items-center justify-between bg-purple-100 rounded-lg p-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={personAhead.User_Img}
                        className="w-12 h-12 rounded-full object-cover"
                      />
                      <div>
                        <p className="font-semibold">{personAhead.User_Name}</p>
                        <p className="text-sm text-gray-500">{personAhead.Donate_Amount} kWh</p>
                      </div>
                    </div>
                    <span className="font-bold text-purple-600">#{myUser.Rank - 1}</span>
                  </div>
                )
              }

              {/* Show USER (always, since user is NOT top 5) */}
              {myUser && (
                <div className="flex items-center justify-between bg-purple-200 rounded-lg p-3">
                  <div className="flex items-center gap-3">
                    <img
                      src={myUser.User_Img}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div>
                      <p className="font-semibold">{myUser.User_Name}</p>
                      <p className="text-sm text-gray-500">{myUser.Donate_Amount} kWh</p>
                    </div>
                  </div>

                  <span className="font-bold text-purple-700">#{myUser.Rank}</span>
                </div>
              )}
            </>
          )}

        </div>

        {/* Encourage */}
        {myUser && (
          <p className="text-sm font-bold text-[#6C00FF] text-center mt-6">
            {myUser.kWh_needed_for_top_5 > 0
              ? `Donate ${myUser.kWh_needed_for_top_5} more kWh to reach the Top 5 🚀`
              : "🎉 Congratulations! You're already in the Top 5 — Keep it up!!"}
          </p>
        )}

      </div>
    </div>
  );
}
