const STEPS = [
  {
    title: "User posts a message",
    body: "A user posts a message in a Discord channel.",
  },
  {
    title: "Another user replies",
    body: "Another user replies to that message using Discord's built-in reply feature.",
  },
  {
    title: "Thread It detects the reply",
    body: "Thread It automatically creates a public thread on the original message.",
  },
  {
    title: "Content moved & cleaned",
    body: "The reply is moved into the thread; the original is removed from the main channel.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" aria-labelledby="how-it-works-heading">
      <h2
        id="how-it-works-heading"
        className="mb-3.5 text-[30px] font-bold tracking-tight"
      >
        How It Works
      </h2>
      <p className="mb-6 max-w-[64ch] text-lg text-pretty text-ink-2">
        Thread It operates completely automatically. Once invited, every reply
        in a channel is captured and re-homed into a dedicated thread on the
        original message.
      </p>

      <ol className="grid gap-0">
        {STEPS.map((s, i) => (
          <li
            key={s.title}
            className="grid grid-cols-[40px_1fr] gap-4 border-b border-border py-[18px] last:border-b-0"
          >
            <span
              className="flex size-[30px] items-center justify-center rounded-full border border-blurple/40 bg-blurple/15 text-[13px] font-bold text-blurple"
              aria-hidden="true"
            >
              {i + 1}
            </span>
            <div>
              <h3 className="mb-1 text-base font-semibold text-ink-1">
                {s.title}
              </h3>
              <p className="text-sm text-ink-2">{s.body}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
