import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../api/authApi';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import bgImage from '../assets/images/login-bg.png';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loginUser({ email, password });
      
      if (response.message === "not implemented") {
         setError("Login not yet functional (Backend returned 'not implemented')");
         return;
      }
      
      if (response.access_token && response.role) {
        login(response.access_token, response.role);
        if (response.role === 'doctor') {
          navigate('/doctor-dashboard');
        } else {
          navigate('/patient-dashboard');
        }
      } else {
        // Fallback for missing fields in success response
        setError("Login successful, but received an unexpected response format from the server.");
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during login.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full relative flex flex-col font-sans">
      {/* Background Image with Dark Blue Overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat z-0" 
        style={{ backgroundImage: `url(${bgImage})` }}
      >
        <div className="absolute inset-0 bg-[#0A192F]/70 mix-blend-multiply"></div>
      </div>

      {/* Main Content Wrapper */}
      <div className="relative z-10 flex flex-col min-h-screen w-full">
        {/* Transparent Top Navbar */}
        <nav className="flex justify-between items-center p-6 md:px-12 w-full animate-fade-in">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
            <span className="text-white font-semibold text-xl tracking-wide">LDP</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-10">
            <Link to="/" className="text-white/80 hover:text-white transition-colors duration-200">Home</Link>
            <Link to="/about" className="text-white/80 hover:text-white transition-colors duration-200">About</Link>
            <Link to="/contact" className="text-white/80 hover:text-white transition-colors duration-200">Contact</Link>
          </div>

          <Link 
            to="/login" 
            className="border border-white/50 text-white px-6 py-2 rounded-full hover:bg-white/10 transition-all duration-300 backdrop-blur-sm"
          >
            Login
          </Link>
        </nav>

        {/* Form Container */}
        <main className="flex-grow flex items-center justify-center p-4">
          {/* Glassmorphism Card */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-[32px] shadow-2xl p-8 md:p-12 w-full max-w-[420px] transition-all duration-500 animate-slide-up hover:shadow-[0_0_40px_rgba(255,255,255,0.1)]">
            <div className="text-center mb-8">
              <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight mb-2">Login</h2>
              <p className="text-white/70">Sign in to access your dashboard.</p>
            </div>
          
            {error && (
              <div className="bg-red-500/20 border border-red-500/50 text-red-100 p-3 rounded-xl mb-6 text-sm text-center animate-shake" role="alert">
                {error}
              </div>
            )}
          
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Field */}
              <div className="relative group">
                <Mail className="absolute left-0 top-3 text-white/50 w-5 h-5 group-focus-within:text-white transition-colors duration-300" />
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email address"
                  className="w-full bg-transparent border-b border-white/30 text-white px-8 py-3 focus:outline-none focus:border-white transition-all duration-300 placeholder:text-white/50"
                  required
                />
              </div>

              {/* Password Field */}
              <div className="relative group">
                <Lock className="absolute left-0 top-3 text-white/50 w-5 h-5 group-focus-within:text-white transition-colors duration-300" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full bg-transparent border-b border-white/30 text-white px-8 py-3 focus:outline-none focus:border-white transition-all duration-300 placeholder:text-white/50"
                  required
                />
                <button
                  type="button"
                  className="absolute right-0 top-3 text-white/50 hover:text-white transition-colors duration-200"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>

              {/* Form Options */}
              <div className="flex justify-between items-center text-sm pt-2">
                <label className="flex items-center space-x-2 cursor-pointer group">
                  <input type="checkbox" className="w-4 h-4 rounded border-white/30 bg-transparent text-[#0A192F] focus:ring-white/50 focus:ring-offset-0 cursor-pointer" />
                  <span className="text-white/70 group-hover:text-white transition-colors duration-200">Remember me</span>
                </label>
                <a href="#" className="text-white/70 hover:text-white transition-colors duration-200">
                  Forgot Password?
                </a>
              </div>
            
              {/* Submit Button */}
              <button 
                type="submit" 
                className="w-full bg-[#0A192F] text-white rounded-full py-4 mt-8 font-semibold text-lg hover:bg-[#112240] transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1 active:translate-y-0 disabled:opacity-70 disabled:hover:translate-y-0 flex items-center justify-center"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Signing in...
                  </span>
                ) : (
                  'Login'
                )}
              </button>
            </form>
          
            {/* Footer */}
            <div className="mt-8 text-center text-sm text-white/70">
              Don't have an account?{' '}
              <Link to="/register" className="text-white hover:underline font-semibold transition-all">
                Register
              </Link>
            </div>
          </div>
        </main>
      </div>

      {/* Tailwind Animations & Utilities (Injected via style tag to ensure they work without modifying config) */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          50% { transform: translateX(5px); }
          75% { transform: translateX(-5px); }
        }
        .animate-fade-in { animation: fadeIn 0.8s ease-out; }
        .animate-slide-up { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1); }
        .animate-shake { animation: shake 0.4s ease-in-out; }
      `}</style>
    </div>
  );
};

export default Login;
