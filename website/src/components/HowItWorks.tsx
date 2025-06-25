import { MessageCircle, Plus, Trash2, Users } from "lucide-react";

const steps = [
  {
    step: 1,
    title: "User Posts Message",
    description: "A user posts a message in a Discord channel.",
    icon: MessageCircle,
    color: "from-blue-500 to-cyan-500",
  },
  {
    step: 2,
    title: "Another User Replies",
    description:
      "Another user replies to that message using Discord's built-in reply feature.",
    icon: Users,
    color: "from-green-500 to-emerald-500",
  },
  {
    step: 3,
    title: "Thread It Detects Reply",
    description:
      "Thread It automatically detects the reply and creates a public thread on the original message.",
    icon: Plus,
    color: "from-purple-500 to-pink-500",
  },
  {
    step: 4,
    title: "Content Moved & Cleaned",
    description:
      "The reply content is moved into the new thread and the original reply is removed from the main channel.",
    icon: Trash2,
    color: "from-red-500 to-rose-500",
  },
];

export default function HowItWorks() {
  return (
    <section
      id="how-it-works"
      className="py-24 bg-white relative overflow-hidden"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            🔄 How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Thread It operates completely automatically, requiring zero input
            from users or moderators. Here's the magic behind the scenes:
          </p>
        </div>

        <div className="relative">
          {/* Connection lines */}
          <div className="hidden lg:block absolute top-24 left-1/2 transform -translate-x-1/2 w-full max-w-4xl">
            <div className="flex justify-between items-center px-16">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="w-32 h-0.5 bg-gradient-to-r from-gray-300 to-gray-400"
                ></div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
            {steps.map((step) => (
              <div key={step.title} className="text-center group">
                <div className="relative mb-8">
                  <div
                    className={`w-20 h-20 bg-gradient-to-r ${step.color} rounded-full flex items-center justify-center mx-auto shadow-2xl group-hover:scale-110 transition-transform duration-300`}
                  >
                    <step.icon className="w-10 h-10 text-white" />
                  </div>
                </div>

                <h3 className="text-2xl font-bold text-gray-900 mb-4">
                  {step.title}
                </h3>

                <p className="text-gray-600 leading-relaxed">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Example Workflow from README */}
        <div className="mt-20 bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl p-8 shadow-2xl">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-white mb-2">
              Example Workflow
            </h3>
            <p className="text-gray-400">
              See how Thread It transforms your conversations
            </p>
          </div>

          <div className="bg-gray-800 rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-gray-400 text-sm ml-2">#general</span>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                  A
                </div>
                <div className="flex-1">
                  <div className="text-white font-semibold mb-1">Alice</div>
                  <div className="bg-gray-700 rounded-lg p-3 text-gray-300">
                    "What's everyone's favorite Python library?"
                  </div>
                </div>
              </div>

              <div className="ml-8 opacity-75">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    B
                  </div>
                  <div className="flex-1">
                    <div className="text-gray-300 font-semibold mb-1 text-sm">
                      Bob (replying to Alice)
                    </div>
                    <div className="bg-gray-600 rounded-lg p-2 text-gray-300 text-sm border-l-4 border-blue-500">
                      "I love requests for HTTP calls!"
                    </div>
                  </div>
                </div>
              </div>

              <div className="ml-8">
                <div className="text-yellow-400 text-sm mb-2">
                  🧵 Thread created automatically
                </div>
                <div className="bg-gray-700/50 rounded-lg p-3 text-gray-400 text-sm border-l-4 border-purple-500">
                  <div className="font-semibold text-purple-400 mb-1">
                    Thread: "What's everyone's favorite Python library?"
                  </div>
                  <div className="text-gray-300">
                    Bob: "I love requests for HTTP calls!"
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center text-gray-400">
            <p className="text-sm">
              <strong>Result:</strong> Clean main channels with organized
              discussions in dedicated threads!
            </p>
          </div>
        </div>

        {/* Bot Behavior Section */}
        <div className="mt-16 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Bot Behavior
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Ignores bot messages
                  </div>
                  <div className="text-gray-600 text-sm">
                    Prevents infinite loops
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Only processes replies
                  </div>
                  <div className="text-gray-600 text-sm">
                    Regular messages are left untouched
                  </div>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Skips existing threads
                  </div>
                  <div className="text-gray-600 text-sm">
                    Won't create threads within threads
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Validates permissions
                  </div>
                  <div className="text-gray-600 text-sm">
                    Checks required permissions before acting
                  </div>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Helpful notifications
                  </div>
                  <div className="text-gray-600 text-sm">
                    Briefly notifies users (auto-deletes after 8 seconds)
                  </div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-green-500 text-xl">✓</span>
                <div>
                  <div className="font-semibold text-gray-900">
                    Handles errors gracefully
                  </div>
                  <div className="text-gray-600 text-sm">
                    Logs issues without crashing
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
