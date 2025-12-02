import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("anisahrahman@gmail.com");
  const [password, setPassword] = useState("anisah*rahman1");
  const [showPassword, setShowPassword] = useState(false);

  // =============================
  // LOGIN FUNCTION
  // =============================
  async function handleLogin() {
    try {
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("token", data.token);
        localStorage.setItem("user_id", data.user_id);
        navigate("/home");
      } else {
        alert(data.error || "Invalid login");
      }
    } catch (err) {
      alert("Cannot connect to server");
    }
  }

  const demoAccounts = [
    { email: "syafiqabdullah@gmail.com", password: "syafiq*abdullah2" },
    { email: "nurulhafizah@gmail.com", password: "nurul*hafizah" },
    { email: "rahimsalleh@gmail.com", password: "ahimbin*salleh4" },
  ];

  function autofillAccount(acct) {
    setEmail(acct.email);
    setPassword(acct.password);
  }

  return (
    <div className="min-h-screen flex items-center justify-center gap-10 px-6 bg-gradient-to-br from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF]">

      {/* LEFT SIDE — LOGIN FORM */}
      <div className="flex items-center justify-center p-10">
        <div className="bg-white/90 backdrop-blur-xl shadow-2xl rounded-2xl p-10 w-full max-w-md border border-white/30">

          {/* Logo */}
          <div className="flex justify-center mb-6">
            <img src="/src/assets/logo.png" alt="SolarAid Logo" className="w-16 h-16" />
          </div>

          <h2 className="text-3xl font-bold text-center text-[#5A32FF] mb-1">
            Welcome Back
          </h2>
          <p className="text-center text-gray-600 mb-8">
            Log in to continue your solar donation journey
          </p>

          <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
            
            {/* Email */}
            <div>
              <label className="text-gray-700 font-medium text-sm">Email</label>
              <input
                type="email"
                placeholder="example@gmail.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full mt-1 px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#5A32FF] outline-none"
              />
            </div>

            {/* Password */}
            <div>
              <label className="text-gray-700 font-medium text-sm">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="•••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full mt-1 px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#5A32FF] outline-none"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 bg-gray-100 border border-gray-300 p-1.5 rounded-md hover:bg-gray-200 shadow-sm"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <button
              type="button"
              onClick={handleLogin}
              className="w-full py-3 bg-[#6C00FF] text-white rounded-xl font-semibold hover:bg-[#5A32FF] shadow-md hover:shadow-xl transition"
            >
              Login
            </button>
          </form>

          {/* Sign Up */}
          <p className="text-center mt-6 text-gray-600">
            Don’t have an account?{" "}
            <Link to="/signup" className="text-[#5A32FF] font-semibold hover:underline">
              Sign Up
            </Link>
          </p>
        </div>
      </div>

      {/* RIGHT SIDE — GLASS DEMO ACCOUNTS */}
      <div className="hidden md:flex items-center justify-center p-10">
        <div className="bg-white/20 backdrop-blur-xl border border-white/30 rounded-2xl shadow-xl p-8 w-80">
          <h3 className="text-white text-xl font-bold mb-4">Demo Admin Accounts</h3>
          
          <div className="space-y-4">
            {demoAccounts.map((acct, i) => (
              <div
                key={i}
                onClick={() => autofillAccount(acct)}
                className="p-4 bg-white/30 hover:bg-white/40 cursor-pointer rounded-xl text-white transition shadow-md"
              >
                <p className="font-semibold">{acct.email}</p>
                <p className="text-sm opacity-75">Password: {acct.password}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
