import React from 'react';
import { Droplets, Wind, Waves, CloudRain, TrendingUp, TrendingDown, ArrowRight, CheckCircle, AlertTriangle, Eye, AlertOctagon, Calendar, Map, AlertCircle, BarChart3, Factory, Thermometer, Shield, Users, FileText, Leaf, Globe, Zap, MessageSquare } from 'lucide-react';
import Globe3D from '../components/Globe3D';
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';
import { useNavigate } from "react-router-dom";
import LogoImg from '../assets/logo.png';
import { Link } from "react-router-dom";

// Animation wrapper component
const AnimatedSection = ({ children, delay = 0 }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.8, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
};

const LandingPage = () => {
  const navigate = useNavigate();

  const newsItems = [
    { id: 1, 
      title: 'Before the electricity donations, our rural clinic struggled to store vaccines safely. Now, our cold storage is stable, and we can protect more children every day.', 
      date: '2025-10-20', 
      name: 'Anisah Rahman', 
      region: 'Sabah, Malaysia', 
      role: 'Nurse', 
      tagColor: 'bg-blue-100 text-blue-800', 
      borderColor: 'border-blue-300' },
    { 
      id: 2, 
      title: "With steady electricity, our students can finally attend evening classes. Computer lessons and exam prep continue even after sunset — something we never imagined before.", 
      date: '2025-10-19', 
      name: 'Syafiq Abdullah', 
      region: 'Kelantan, Malaysia', 
      role: 'School Teacher', 
      tagColor: 'bg-green-100 text-green-800', 
      borderColor: 'border-green-300' 
    },

    { 
      id: 3, 
      title: "Our community centre used to go dark during outages, leaving families unsafe at night. Now, with donated power, security lights stay on and the neighbourhood feels safer for everyone.", 
      date: '2025-10-18', 
      name: 'Nurul Hafizah', 
      region: 'Perak, Malaysia', 
      role: 'Community Leader', 
      tagColor: 'bg-yellow-100 text-yellow-800', 
      borderColor: 'border-yellow-300' 
    },

    { 
      id: 4, 
      title: "Before receiving support, we had to shut our fish refrigeration room during long outages, risking huge losses. Today, donated power keeps everything running smoothly and protects our livelihood.", 
      date: '2025-10-17', 
      name: 'Rahim bin Salleh', 
      region: 'Terengganu, Malaysia', 
      role: 'Fisherman', 
      tagColor: 'bg-purple-100 text-purple-800', 
      borderColor: 'border-purple-300' 
    }
   ];

  const featureCards = [
    {
      id: 1, 
      title: 'JARIAH CERTIFICATE', 
      subtitle: 'Official Donation Proof', 
      // Updated description below:
      description: 'Receive verifiable digital proof of your contributions. Ensure transparency and track the impact of your continuous charity.',
      icon: FileText,
      role: 'For Donors'
    },
    { 
    id: 2,
    title: 'DONATION PREDICTION',
    subtitle: 'Future Ranking Insight',
    description: 'AI forecasts the donation amount needed to reach the next ranking. Stay motivated with personalised progress targets.',
    icon: TrendingUp,
    action: 'View Prediction',
    role: 'For Donors'
  },
  { 
    id: 3, 
    title: 'AI CHATBOT', 
    subtitle: 'Instant Support', 
    description: 'Get answers to FAQs anytime. Receive quick help on donations, rankings, Jariah certificate, and platform navigation.',
    icon: MessageSquare,
    action: 'Ask Now',
    role: 'For All Users'
  }
  ];

  return (
    <div className="min-h-screen bg-white">
      
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gradient-to-r from-[#3BA0FF] via-[#5A32FF] to-[#6C00FF] backdrop-blur-md z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div >
              <img 
                src={LogoImg} 
                alt="Icon"
                className="w-8 h-8 object-contain"
              />
            </div>
            <span className="text-2xl font-bold text-gray-900">SolarAid</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#about" className="text-sm font-medium text-white transition-colors">About</a>
            <a href="#features" className="text-sm font-medium text-white transition-colors">Features</a>
            <a href="#news" className="text-sm font-medium text-white transition-colors">Journey</a>
            <a href="#contact" className="text-sm font-medium text-white transition-colors">Contact</a>
          </div>
        </div>
      </nav>

      {/* Hero Section - Side by Side with Globe */}
      <section className="py-24 px-6 bg-[#FCF6D9]/30">
        <div className="max-w-7xl mx-auto">
          <AnimatedSection>
            <div className="grid md:grid-cols-2 gap-16 items-center">
              {/* Left - Globe */}
              <div className="relative flex items-center justify-center order-2 md:order-1">
                <div className="relative w-full h-[600px]">
                  <Globe3D />
                </div>
                
                {/* Floating Data Cards - Dark Blue Theme */}
                <div className="absolute top-12 left-4 bg-white/90 backdrop-blur-sm px-5 py-4 rounded-lg shadow-lg hidden lg:block border border-gray-200 animate-float">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-[#3BA0FF]/10 rounded-lg flex items-center justify-center">
                      <Zap className="text-black" size={22} />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-500 font-medium uppercase tracking-wider mb-1">Electricity</p>
                      <p className="text-lg font-bold text-gray-900">Stable</p>
                    </div>
                  </div>
                </div>
                <div className="absolute bottom-12 right-4 bg-white/90 backdrop-blur-sm px-5 py-4 rounded-lg shadow-lg hidden lg:block border border-gray-200 animate-float-delayed">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-[#6C00FF]/10 rounded-lg flex items-center justify-center">
                      <TrendingUp className="text-black" size={22} />
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-500 font-medium uppercase tracking-wider mb-1">Impact to Society</p>
                      <p className="text-lg font-bold text-gray-900">83%</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Content */}
              <div className="space-y-6 order-1 md:order-2">
                <div className="inline-block">
                  <span className="text-xs font-bold text-[#5A32FF] tracking-widest uppercase">
                    SDG 7: Affordable & Clean Energy
                  </span>
                </div>
                <h1 className="text-5xl md:text-6xl font-bold text-[#6C00FF] leading-tight">
                  SolarAid
                </h1>
                <p className="text-lg text-[#5A32FF]/70 leading-relaxed">
                  SolarAid is a renewable-energy donation platform that helps Malaysians support communities in need with clean electricity. Users can view areas needing power, donate instantly, track their impact, receive JARIAH certificates, and climb donor rankings.
                </p>
                
                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row items-start gap-4 pt-4">
                  <Link
                    to="/login"
                    className="px-8 py-4 bg-[#5A32FF]/85 text-white rounded-full font-semibold 
                              hover:shadow-2xl hover:scale-105 transition-all inline-block"
                  >
                    Start Donating
                  </Link>
                </div>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* About Section - Full Width Banner */}
      <section 
        id="about"
        style={{
          backgroundImage: "linear-gradient(to bottom, #6C00FF, #5A32FF, #3BA0FF)",
        }}
        className="py-32 px-6"
      >


        <div className="max-w-7xl mx-auto relative z-10">
          <AnimatedSection>
            <div className="text-center space-y-6">
              <div className="inline-block px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
                <span className="text-sm font-bold text-white uppercase tracking-wider">About Us</span>
              </div>
              <h2 className="text-5xl md:text-6xl font-bold text-white leading-tight">
                Mission & Vision<br />
              </h2>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
                Mission: To enable every Malaysian to support clean, reliable energy access by transforming surplus solar power into meaningful community impact.
              </p>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
                Vision: A Malaysia where renewable energy empowers every home, school, and community to thrive sustainably.
              </p>
              <div className="pt-4">
                <button className="inline-flex items-center gap-3 px-10 py-4 bg-white text-slate-900 rounded-full font-bold hover:shadow-2xl hover:scale-105 transition-all">
                  Learn More <ArrowRight size={20} />
                </button>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Features Grid Section */}
      <section id="features" className="py-24 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <AnimatedSection>
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold text-[#6C00FF] mt-4 mb-6">
                Our Features
              </h2>
              <p className="text-lg text-[#5A32FF]/70 max-w-2xl mx-auto">
                System empowers users to donate confidently, track their impact and enjoy a seamless, rewarding giving experience.
              </p>
            </div>
          </AnimatedSection>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {featureCards.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <AnimatedSection key={feature.id} delay={index * 0.1}>
                  <div className="relative group h-[480px] rounded-2xl overflow-hidden cursor-pointer shadow-lg hover:shadow-2xl transition-all">
                    {/* Background with gradient overlay */}
                    <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"></div>
                    
                    {/* Pattern overlay */}
                    <div className="absolute inset-0 bg-[#5A32FF]">
                    </div>

                    {/* Content */}
                    <div className="relative h-full p-8 flex flex-col justify-between">
                      <div>
                        <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                          <Icon size={32} className="text-white" />
                        </div>
                        <div className="mb-4">
                          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">{feature.role}</span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-3 uppercase tracking-wide">{feature.title}</h3>
                        <p className="text-xl font-semibold text-slate-300 mb-3">{feature.subtitle}</p>
                        <p className="text-slate-300 text-s leading-relaxed">{feature.description}</p>
                      </div>
                    </div>
                  </div>
                </AnimatedSection>
              );
            })}
          </div>
        </div>
      </section>

      {/* News & Alerts */}
      <section id="news" className="py-24 px-6 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-7xl mx-auto">
          <AnimatedSection>
            <div className="text-center mb-16">
              <div className="inline-block mb-4">
                <span className="text-xs font-bold text-[#5A32FF]/90 tracking-widest uppercase bg-[#5A32FF]/10 px-4 py-2 rounded-full">
                  Latest Journey
                </span>
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-[#6C00FF] mb-4">How Your Energy Donation Helps</h2>
              <p className="text-[#5A32FF]/80 text-lg max-w-3xl mx-auto">See how clean energy donations create meaningful impact for families, schools, and villages.</p>
            </div>
          </AnimatedSection>
          
          <div className="grid md:grid-cols-4 gap-6">
            {newsItems.map((item, index) => (
              <AnimatedSection key={item.id} delay={index * 0.1}>
                <div className="bg-white rounded-xl p-6 border border-slate-200 hover:border-slate-300 hover:shadow-xl transition-all duration-300 cursor-pointer group h-full flex flex-col">
                  <div className="flex items-start justify-between mb-4">
                    <span className="px-3 py-1.5 rounded-md text-xs font-bold uppercase tracking-wider bg-[#3BA0FF]/15 text-[#2F58CD]">
                      {item.name}
                    </span>
                    <div className="text-xs text-[#2F58CD]/80 flex items-center gap-1">
                      <Calendar size={14} />
                      {new Date(item.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </div>
                  </div>
                  <h3 className="font-bold text-[#03346E]/80 mb-4 text-base leading-tight group-hover:text-slate-700 transition-colors flex-grow">
                    {item.title}
                  </h3>
                  <div className="space-y-3 pt-4 border-t border-slate-100 mt-auto">
                    <span className="flex items-center gap-2 text-xs text-[#2F58CD]/80 font-medium">
                      <Map size={14} className="text-[#2F58CD]/80" />
                      {item.region}
                    </span>
                    <span className="text-sm text-[#2F58CD]/90 font-medium block">Role: {item.role}</span>
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <section id="contact" className="py-12 px-6 bg-gray-100"></section>
      <footer
        className="text-black py-16 px-6"
        style={{
          backgroundImage: "linear-gradient(to bottom, #3BA0FF, #5A32FF, #6C00FF)",
        }}
      >
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div className="col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <img 
                  src={LogoImg} 
                  alt="Icon"
                  className="w-8 h-8 object-contain"
                />
                <span className="text-2xl font-bold text-black">SolarAid</span>
              </div>
              <p className="text-gray-800 leading-relaxed mb-4">
                SDG 7.1: Ensure universal access to affordable, reliable and modern energy services by 2030. <br />
              </p>
              <p className="text-black leading-relaxed mb-4">
                SDG 7.2: Increase substantially the share of renewable energy in the global energy mix by 2030. <br />
              </p>
            
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#about" className="hover:text-white text-gray-800 transition-colors">About Us</a></li>
                <li><a href="#features" className="hover:text-white text-gray-800 transition-colors">Features</a></li>
                <li><a href="#status" className="hover:text-white text-gray-800 transition-colors">Status</a></li>
                <li><a href="#news" className="hover:text-white text-gray-800 transition-colors">News</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-800">
                <li>Support</li>
                <li>Feedback</li>
                <li>Emergency</li>
                <li>Press</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-black text-sm">
            <p>&copy; 2025 SolarAid. All rights reserved. Supporting SDG 7.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
