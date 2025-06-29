import { ArrowRight, Github } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          {/* Logo with thread image */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className="size-20 rounded-2xl shadow-2xl scale-125 overflow-hidden">
                <img
                  src="/thread-it-icon.png"
                  alt="Thread It logo"
                  className="size-20"
                />
              </div>
            </div>
          </div>

          {/* Main heading */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
            Thread It
            <span className="block text-3xl sm:text-4xl lg:text-5xl bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mt-2">
              Discord Bot
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl sm:text-2xl text-gray-300 mb-12 max-w-4xl mx-auto leading-relaxed">
            A Discord bot that keeps channels clean by converting replies into
            threads.
          </p>

          {/* Video Demo Badge */}
          <div className="mb-8">
            <a
              className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-full border border-white/20"
              href="https://x.com/weicodes/status/1939404324704264689"
              target="_blank"
              rel="noopener"
            >
              <span className="text-sm font-medium">🎦 Video Demo</span>
            </a>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <a
              href="https://discord.com/oauth2/authorize?client_id=1386888801229734018"
              target="_blank"
              className="group bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105 flex items-center gap-2"
              rel="noopener"
            >
              Add to Discord
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </a>
            <a
              href="https://github.com/wei/thread-it"
              target="_blank"
              className="bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-semibold text-lg border border-white/20 hover:bg-white/20 transition-all duration-300 flex items-center gap-2"
              rel="noopener"
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </a>
          </div>

          {/* Tech Stack Badges */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            <div className="bg-blue-500/20 backdrop-blur-sm text-blue-200 px-4 py-2 rounded-full border border-blue-400/30">
              <span className="text-sm font-medium">Python</span>
            </div>
            <div className="bg-purple-500/20 backdrop-blur-sm text-purple-200 px-4 py-2 rounded-full border border-purple-400/30">
              <span className="text-sm font-medium">Discord.py</span>
            </div>
            <div className="bg-green-500/20 backdrop-blur-sm text-green-200 px-4 py-2 rounded-full border border-green-400/30">
              <span className="text-sm font-medium">MIT License</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-md mx-auto">
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">Open</div>
              <div className="text-gray-400">Source</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">Zero</div>
              <div className="text-gray-400">Config</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white mb-2">Auto</div>
              <div className="text-gray-400">Threading</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
