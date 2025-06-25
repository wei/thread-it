import { ExternalLink, Github, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-500 rounded-xl flex items-center justify-center">
                <img
                  src="/thread-it-icon.png"
                  alt="Thread It logo"
                  className="w-6 h-6"
                />
              </div>
              <span className="text-2xl font-bold">Thread It</span>
            </div>
            <p className="text-gray-400 leading-relaxed max-w-md">
              The smart Discord bot that automatically organizes your
              conversations by converting replies into clean, contextual
              threads.
            </p>
            <div className="flex gap-4 mt-6">
              <a
                href="https://github.com/wei/thread-it"
                target="_blank"
                className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-colors"
                rel="noopener"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://discord.com/oauth2/authorize?client_id=1386888801229734018"
                target="_blank"
                className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-gray-700 transition-colors"
                rel="noopener"
              >
                <ExternalLink className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Product</h3>
            <ul className="space-y-3 text-gray-400">
              <li>
                <a
                  href="#features"
                  className="hover:text-white transition-colors"
                >
                  Features
                </a>
              </li>
              <li>
                <a
                  href="#how-it-works"
                  className="hover:text-white transition-colors"
                >
                  How It Works
                </a>
              </li>
              <li>
                <a href="#setup" className="hover:text-white transition-colors">
                  Setup Guide
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/wei/thread-it"
                  target="_blank"
                  className="hover:text-white transition-colors flex items-center gap-1"
                  rel="noopener"
                >
                  Source Code <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Support</h3>
            <ul className="space-y-3 text-gray-400">
              <li>
                <a
                  href="https://github.com/wei/thread-it#readme"
                  target="_blank"
                  className="hover:text-white transition-colors flex items-center gap-1"
                  rel="noopener"
                >
                  Documentation <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/wei/thread-it/issues"
                  target="_blank"
                  className="hover:text-white transition-colors flex items-center gap-1"
                  rel="noopener"
                >
                  Bug Reports <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/wei/thread-it/issues"
                  target="_blank"
                  className="hover:text-white transition-colors flex items-center gap-1"
                  rel="noopener"
                >
                  Feature Requests <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://discord.com/oauth2/authorize?client_id=1386888801229734018"
                  target="_blank"
                  className="hover:text-white transition-colors flex items-center gap-1"
                  rel="noopener"
                >
                  Add to Server <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col sm:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            Made with <Heart className="w-4 h-4 inline text-red-500" /> by{" "}
            <a href="https://wei.me" class="hover:text-white">
              @wei
            </a>
            .
          </p>
          <div className="flex gap-6 mt-4 sm:mt-0">
            <a
              href="https://github.com/wei/thread-it/blob/main/LICENSE"
              target="_blank"
              className="text-gray-400 hover:text-white text-sm transition-colors"
              rel="noopener"
            >
              MIT License
            </a>
            <a
              href="https://github.com/wei/thread-it"
              target="_blank"
              className="text-gray-400 hover:text-white text-sm transition-colors"
              rel="noopener"
            >
              GitHub
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
