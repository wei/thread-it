const FEATURES = [
  {
    name: "Automatic Thread Creation",
    desc: "Converts message replies into organized public threads, keeping your channels clean and conversations contextual.",
  },
  {
    name: "Seamless Operation",
    desc: "Works in the background without requiring manual commands. No setup complexity, just invite and go.",
  },
  {
    name: "Smart Thread Naming",
    desc: "Automatically generates meaningful thread names from original message content with smart formatting.",
  },
  {
    name: "Content Preservation",
    desc: "Maintains all reply content including text, attachments, embeds, and formatting when moving to threads.",
  },
  {
    name: "Permission Validation",
    desc: "Ensures proper bot permissions before attempting operations, with graceful error handling.",
  },
  {
    name: "Comprehensive Logging",
    desc: "Detailed logging for monitoring and debugging, with robust error handling and graceful fallbacks.",
  },
];

export default function Features() {
  return (
    <section id="features" aria-labelledby="features-heading">
      <h2
        id="features-heading"
        className="mb-3.5 text-[30px] font-bold tracking-tight"
      >
        Features
      </h2>
      <p className="mb-3 text-ink-2">
        Six capabilities ship in the box. All on by default.
      </p>

      <div className="mt-3 overflow-hidden rounded-lg border border-border">
        {FEATURES.map((f, i) => (
          <article
            key={f.name}
            className={[
              "grid gap-1.5 px-4 py-3.5 sm:grid-cols-[220px_1fr] sm:gap-6 sm:px-5.5 sm:py-4",
              i !== FEATURES.length - 1 ? "border-b border-border" : "",
              i % 2 === 0 ? "bg-white/[0.02]" : "",
            ].join(" ")}
          >
            <h3 className="flex items-center gap-2 text-[14.5px] font-semibold text-ink-1">
              <span
                className="size-[5px] rounded-full bg-blurple"
                aria-hidden="true"
              />
              {f.name}
            </h3>
            <p className="text-[13.5px] leading-[1.55] text-ink-2">{f.desc}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
