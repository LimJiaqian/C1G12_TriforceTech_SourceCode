export default function Leaderboard({ topUsers, myUser, personAhead, leftHeight, myKwh }) {

  return (
    <div className="w-full lg:w-[380px]">
      <div className="bg-white shadow-md rounded-xl p-6">

        {/* Title */}
        <div className="flex items-center gap-2 mb-6">
          <span className="text-2xl">🏆</span>
          <h3 className="text-2xl font-bold text-[#6C00FF]">Top Donors</h3>
        </div>

        {/* Top Donor List */}
        <div className="space-y-3">
            {topUsers.slice(0, 5).map((user, i) => (
            <div
              key={i}
              className="flex items-center justify-between bg-gray-100 rounded-lg p-3 hover:bg-gray-200 transition"
            >
              <div className="flex items-center gap-3">
                <img
                  src={user.User_Img}
                  alt={user.User_Name}
                  className="w-12 h-12 rounded-full object-cover shadow"
                />
                <div>
                  <p className="font-semibold">{user.User_Name}</p>
                  <p className="text-sm text-gray-500">{user.total_Donation_Amount_kWh} kWh</p>
                </div>
              </div>

              <span className="font-bold text-[#6C00FF]">#{i + 1}</span>
            </div>
          ))}

          {/* ... Separator */}
          <p className="text-center text-gray-400 font-semibold">...</p>

          {/* Person Ahead */}
          {personAhead && (
            <div className="flex items-center justify-between bg-purple-100 rounded-lg p-3">
              <div className="flex items-center gap-3">
                <img
                  src={personAhead.User_Img}
                  className="w-12 h-12 rounded-full object-cover"
                />
                <div>
                  <p className="font-semibold">{personAhead.User_Name}</p>
                  <p className="text-sm text-gray-500">{personAhead.total_Donation_Amount_kWh} kWh</p>
                </div>
              </div>
              <span className="font-bold text-purple-600">#{myUser.Rank - 1}</span>
            </div>
          )}

          {/* YOU */}
          {myUser && (
            <div className="flex items-center justify-between bg-purple-200 rounded-lg p-3">
              <div className="flex items-center gap-3">
                <img
                  src={myUser.User_Img.toString()}
                  className="w-12 h-12 rounded-full object-cover"
                />
                <div>
                  <p className="font-semibold">{myUser.User_Name}</p>
                  <p className="text-sm text-gray-500">{myUser.total_Donation_Amount_kWh} kWh</p>
                </div>
              </div>
              <span className="font-bold text-purple-700">#{myUser.Rank}</span>
            </div>
          )}

          {/* Encourage Donating */}
          {myUser && (
            <p className="text-sm font-bold text-[#6C00FF] text-center mt-2">
              Donate {myUser.kWh_needed_for_top_5} more kWh to reach Top 5 🚀
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
