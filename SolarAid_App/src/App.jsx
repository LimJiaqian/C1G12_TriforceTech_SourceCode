import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./landingpages/LandingPage.jsx";
import DonationPage from "./pages/donation.jsx";
import DonationComplete from "./pages/donation_done.jsx";
import Login from "./pages/login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import DonationHistory from "./pages/DonationHistory.jsx";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<Dashboard />} />
        <Route path="/donate" element={<DonationPage />} />
        <Route path="/donation_complete" element={<DonationComplete />} />
        <Route path="/login" element={<Login />} />
        <Route path="/donation_history" element={<DonationHistory />} />
      </Routes>
    </Router>
  );
}
