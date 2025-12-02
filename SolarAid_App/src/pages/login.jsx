import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleLogin() {
    // No backend -> just redirect to /home
    navigate("/home");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF] px-4">
      <div className="bg-white/90 backdrop-blur-xl shadow-2xl rounded-2xl p-10 w-full max-w-md border border-white/30">
        
        {/* Logo */}
        <div className="flex justify-center mb-6">
          <img 
            src="/src/assets/logo.png" 
            alt="SolarAid Logo"
            className="w-16 h-16"
          />
        </div>

        {/* Title */}
        <h2 className="text-3xl font-bold text-center text-[#5A32FF] mb-1">
          Welcome Back
        </h2>
        <p className="text-center text-gray-600 mb-8">
          Log in to continue your solar donation journey
        </p>

        {/* Form */}
        <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
          {/* Email */}
          <div>
            <label className="text-gray-700 font-medium text-sm">Email</label>
            <input
              type="email"
              placeholder="example@gmail.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 px-4 py-3 rounded-xl border border-gray-300
                         focus:ring-2 focus:ring-[#5A32FF] focus:border-[#5A32FF] outline-none"
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-gray-700 font-medium text-sm">Password</label>
            <input
              type="password"
              placeholder="•••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-4 py-3 rounded-xl border border-gray-300
                         focus:ring-2 focus:ring-[#5A32FF] focus:border-[#5A32FF] outline-none"
            />
          </div>

          {/* Login Button */}
          <button
            type="button"
            onClick={handleLogin}
            className="w-full py-3 bg-[#6C00FF] text-white rounded-xl font-semibold 
                       hover:bg-[#5A32FF] transition-all shadow-md hover:shadow-xl"
          >
            Login
          </button>
        </form>

        {/* Divider */}
        <div className="flex items-center my-6">
          <div className="flex-1 h-px bg-gray-300"></div>
          <span className="px-3 text-gray-400 text-sm">or</span>
          <div className="flex-1 h-px bg-gray-300"></div>
        </div>

        {/* Sign up */}
        <p className="text-center text-gray-600">
          Don’t have an account?{" "}
          <Link to="/signup" className="text-[#5A32FF] font-semibold hover:underline">
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
}
