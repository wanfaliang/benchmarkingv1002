import React from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BarChart3, PieChart, Newspaper, Database, Wrench, ArrowRight, Sparkles, CheckCircle2, Zap, Shield, Clock, LucideIcon } from 'lucide-react';

/**
 * Homepage.tsx - Professional Landing Page (Light Hero Version)
 *
 * Features:
 * - Modern gradient hero section with light theme
 * - Feature modules grid with hover effects
 * - Key benefits section
 * - Professional styling with Tailwind CSS
 */

function cls(...classes: (string | boolean | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}

interface Module {
  icon: LucideIcon;
  title: string;
  description: string;
  color: string;
  lightBg: string;
  textColor: string;
}

interface Benefit {
  icon: LucideIcon;
  title: string;
  description: string;
}

const Homepage: React.FC = () => {
  const navigate = useNavigate();

  const modules: Module[] = [
    {
      icon: TrendingUp,
      title: 'Financial Analysis',
      description: 'Comprehensive equity research with 20+ analysis modules covering financials, valuation, and risk',
      color: 'bg-blue-500',
      lightBg: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    {
      icon: BarChart3,
      title: 'Quantitative Trading',
      description: 'Strategy backtesting and algorithmic trading research with real-time market data',
      color: 'bg-purple-500',
      lightBg: 'bg-purple-50',
      textColor: 'text-purple-600'
    },
    {
      icon: PieChart,
      title: 'Portfolio Optimization',
      description: 'Risk-return analysis and portfolio construction with modern portfolio theory',
      color: 'bg-emerald-500',
      lightBg: 'bg-emerald-50',
      textColor: 'text-emerald-600'
    },
    {
      icon: Newspaper,
      title: 'News & Research',
      description: 'Aggregated insights from multiple sources with sentiment analysis',
      color: 'bg-amber-500',
      lightBg: 'bg-amber-50',
      textColor: 'text-amber-600'
    },
    {
      icon: Database,
      title: 'Data Platform',
      description: 'Financial, market, and alternative data access with flexible filtering',
      color: 'bg-pink-500',
      lightBg: 'bg-pink-50',
      textColor: 'text-pink-600'
    },
    {
      icon: Wrench,
      title: 'Tools & Utilities',
      description: 'Financial calculators and analysis tools for investment decisions',
      color: 'bg-indigo-500',
      lightBg: 'bg-indigo-50',
      textColor: 'text-indigo-600'
    }
  ];

  const benefits: Benefit[] = [
    {
      icon: Zap,
      title: 'Real-time Updates',
      description: 'WebSocket-powered live data and progress tracking'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'Bank-grade encryption and data protection'
    },
    {
      icon: Clock,
      title: 'Save Time',
      description: 'Automated analysis reduces research time by 90%'
    },
    {
      icon: CheckCircle2,
      title: 'Professional Quality',
      description: 'Institutional-grade analysis and reporting'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section - LIGHT VERSION */}
      <div className="relative bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-40">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, rgb(148 163 184) 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }}></div>
        </div>

        {/* Gradient Orbs */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-200/40 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-200/40 rounded-full blur-3xl"></div>

        {/* Content */}
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-slate-200 shadow-sm text-slate-700 text-sm font-medium mb-8">
              <Sparkles className="w-4 h-4 text-blue-500" />
              Professional Financial Intelligence
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 tracking-tight">
              Transform Your
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Financial Analysis
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-xl sm:text-2xl text-slate-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Comprehensive data analysis, quantitative trading, and portfolio management tools for investment professionals
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => navigate('/register')}
                className="group px-8 py-4 bg-slate-900 text-white rounded-xl font-semibold text-lg hover:bg-slate-800 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 inline-flex items-center gap-2"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/login')}
                className="px-8 py-4 bg-white text-slate-700 border-2 border-slate-300 rounded-xl font-semibold text-lg hover:bg-slate-50 hover:border-slate-400 transition-all inline-flex items-center gap-2 shadow-sm"
              >
                View Demo
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="mt-16 flex flex-wrap justify-center gap-8 text-slate-600 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>20+ Analysis Modules</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Real-time Data</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>Enterprise Security</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="py-16 bg-white border-y border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-slate-900 text-white mb-4">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-slate-600 text-sm">
                    {benefit.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Modules Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Powerful Modules
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Everything you need for professional financial analysis and research
            </p>
          </div>

          {/* Modules Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module, index) => {
              const Icon = module.icon;
              return (
                <div
                  key={index}
                  className="group relative rounded-2xl border border-slate-200 bg-white p-8 hover:shadow-xl hover:border-slate-300 transition-all duration-300 cursor-pointer hover:-translate-y-1"
                >
                  {/* Icon */}
                  <div className={cls(
                    "inline-flex items-center justify-center w-14 h-14 rounded-xl mb-6 transition-transform group-hover:scale-110",
                    module.lightBg
                  )}>
                    <Icon className={cls("w-7 h-7", module.textColor)} />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-slate-900 mb-3">
                    {module.title}
                  </h3>
                  <p className="text-slate-600 leading-relaxed">
                    {module.description}
                  </p>

                  {/* Hover Indicator */}
                  <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity">
                    <ArrowRight className={cls("w-5 h-5", module.textColor)} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-slate-300 mb-10">
            Join professionals who trust our platform for their financial analysis needs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/register')}
              className="group px-8 py-4 bg-white text-slate-900 rounded-xl font-semibold text-lg hover:bg-slate-100 transition-all shadow-lg hover:shadow-xl inline-flex items-center justify-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white border-2 border-white/30 rounded-xl font-semibold text-lg hover:bg-white/20 transition-all"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <span className="text-xl font-bold text-white">FinExus</span>
            </div>
            <p className="text-slate-400 text-sm">
              © 2025 FinExus. Professional Financial Intelligence Platform.
            </p>
            <p className="text-slate-500 text-xs mt-2">
              Enterprise-grade analysis tools for investment professionals
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Homepage;
