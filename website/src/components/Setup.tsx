import {
  Code,
  Download,
  ExternalLink,
  Play,
  Settings,
  Shield,
  Terminal,
} from "lucide-react";

const setupSteps = [
  {
    icon: Download,
    title: "Clone Repository",
    description:
      "Clone the Thread It repository and set up your development environment.",
    code: "git clone https://github.com/wei/thread-it.git\ncd thread-it",
    link: null,
  },
  {
    icon: Terminal,
    title: "Install Dependencies",
    description:
      "Set up a virtual environment and install the required Python packages.",
    code: "python -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\npip install -r requirements.txt",
    link: null,
  },
  {
    icon: Settings,
    title: "Create Discord Bot",
    description:
      "Create a new Discord application and bot in the Discord Developer Portal.",
    code: null,
    link: "https://discord.com/developers/applications",
  },
  {
    icon: Shield,
    title: "Configure Bot Permissions",
    description:
      "Enable the Message Content Intent and set up the required permissions.",
    code: "Required Permissions:\n• View Channels\n• Send Messages\n• Send Messages in Threads\n• Create Public Threads\n• Manage Messages\n• Read Message History\n\nRequired Intents:\n• Message Content Intent (Privileged)",
    link: null,
  },
  {
    icon: Code,
    title: "Set Environment Variables",
    description: "Copy the example environment file and add your bot token.",
    code: "cp .env.example .env\n# Edit .env with your bot token:\n# DISCORD_TOKEN=your_bot_token_here\n# LOG_LEVEL=INFO",
    link: null,
  },
  {
    icon: Play,
    title: "Run the Bot",
    description: "Start the bot and invite it to your Discord server.",
    code: "python bot.py",
    link: "https://discord.com/oauth2/authorize?client_id=1386888801229734018",
  },
];

export default function Setup() {
  return (
    <section
      id="setup"
      className="py-24 bg-gradient-to-br from-indigo-50 to-purple-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            🚀 Installation
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get Thread It running in your Discord server with this step-by-step
            installation guide. Perfect for developers who want to host their
            own instance.
          </p>
        </div>

        <div className="space-y-6">
          {setupSteps.map((step) => (
            <div
              key={step.title}
              className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow duration-300"
            >
              <div className="flex items-start gap-6">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center">
                    <step.icon className="w-8 h-8 text-white" />
                  </div>
                </div>

                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {step.title}
                  </h3>

                  <p className="text-gray-600 leading-relaxed mb-4">
                    {step.description}
                  </p>

                  {step.code && (
                    <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm overflow-x-auto mb-4 whitespace-pre-line">
                      {step.code}
                    </div>
                  )}

                  {step.link && (
                    <a
                      href={step.link}
                      target="_blank"
                      className="inline-flex items-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105"
                    >
                      {step.title.includes("Discord")
                        ? "Open Developer Portal"
                        : "Invite Bot to Server"}
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Invite Option */}
        <div className="mt-16 text-center">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 shadow-lg text-white max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold mb-4">Just Want to Use It?</h3>
            <p className="mb-6 opacity-90">
              Skip the installation and use our hosted version. Just invite the
              bot to your server and start organizing conversations immediately.
            </p>
            <a
              href="https://discord.com/oauth2/authorize?client_id=1386888801229734018"
              target="_blank"
              className="inline-flex items-center gap-2 bg-white text-blue-600 px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105"
              rel="noopener"
            >
              Add to Discord (Hosted Version)
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Support Section */}
        <div className="mt-16 text-center">
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-100 max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Need Help?
            </h3>
            <p className="text-gray-600 mb-6">
              Check out the comprehensive documentation on GitHub or report
              issues if you encounter any problems during installation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://github.com/wei/thread-it#readme"
                target="_blank"
                className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2"
                rel="noopener"
              >
                View Documentation
                <ExternalLink className="w-4 h-4" />
              </a>
              <a
                href="https://github.com/wei/thread-it/issues"
                target="_blank"
                className="bg-gray-100 text-gray-700 px-8 py-3 rounded-xl font-semibold hover:bg-gray-200 transition-colors duration-300 flex items-center justify-center gap-2"
                rel="noopener"
              >
                Report Issues
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
