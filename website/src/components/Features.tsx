import {
  FileText,
  MessageSquare,
  Settings,
  Shield,
  Users,
  Zap,
} from "lucide-react";

const features = [
  {
    icon: MessageSquare,
    title: "Automatic Thread Creation",
    description:
      "Converts message replies into organized public threads, keeping your channels clean and conversations contextual.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Zap,
    title: "Seamless Operation",
    description:
      "Works in the background without requiring manual commands. No setup complexity - just invite and go.",
    color: "from-yellow-500 to-orange-500",
  },
  {
    icon: Shield,
    title: "Smart Thread Naming",
    description:
      "Automatically generates meaningful thread names from original message content with smart formatting.",
    color: "from-green-500 to-emerald-500",
  },
  {
    icon: Settings,
    title: "Content Preservation",
    description:
      "Maintains all reply content including text, attachments, embeds, and formatting when moving to threads.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: Users,
    title: "Permission Validation",
    description:
      "Ensures proper bot permissions before attempting operations, with graceful error handling.",
    color: "from-indigo-500 to-purple-500",
  },
  {
    icon: FileText,
    title: "Comprehensive Logging",
    description:
      "Detailed logging for monitoring and debugging, with robust error handling and graceful fallbacks.",
    color: "from-rose-500 to-pink-500",
  },
];

export default function Features() {
  return (
    <section
      id="features"
      className="py-24 bg-gray-50 relative overflow-hidden"
    >
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-purple-50 opacity-50"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            ✨ Features
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Designed to work seamlessly in the background, Thread It transforms
            how your Discord community handles conversations without disrupting
            natural user behavior.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border border-gray-100"
            >
              <div
                className={`w-16 h-16 bg-gradient-to-r ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
              >
                <feature.icon className="w-8 h-8 text-white" />
              </div>

              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {feature.title}
              </h3>

              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
