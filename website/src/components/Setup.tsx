import { ExternalLink } from "lucide-react";

const INVITE_URL =
  "https://discord.com/oauth2/authorize?client_id=1386888801229734018";

const BEHAVIOR = [
  { title: "Ignores bot messages", desc: "Prevents infinite loops" },
  { title: "Only processes replies", desc: "Regular messages untouched" },
  { title: "Skips existing threads", desc: "No threads inside threads" },
  { title: "Validates permissions", desc: "Checks perms before acting" },
  { title: "Help command", desc: "!thread-it", monoDesc: true },
  { title: "Helpful notifications", desc: "Auto-delete after 8s" },
];

// Matches README's bot permissions table.
// `bot.py` enforces the first six (`required_permissions`),
// adds `attach_files` when the reply has attachments,
// and treats `manage_messages` as optional but recommended.
const REQUIRED_PERMS = [
  ["View Channels", "Read messages in channels"],
  ["Send Messages", "Send messages in main channels"],
  ["Send Messages in Threads", "Send messages in created threads"],
  ["Create Public Threads", "Create threads on messages"],
  ["Read Message History", "Access message history for context"],
  ["Embed Links", "Post reply content as embeds in threads"],
  ["Attach Files", "Re-upload reply attachments into threads"],
] as const;

const RECOMMENDED_PERMS = [
  ["Manage Messages", "Delete original reply messages after threading"],
] as const;

export default function Setup() {
  return (
    <>
      {/* Bot Behavior */}
      <section id="behavior" aria-labelledby="behavior-heading">
        <h2
          id="behavior-heading"
          className="mb-3.5 text-[30px] font-bold tracking-tight"
        >
          Bot Behavior
        </h2>
        <p className="mb-3 text-ink-2">What Thread It will and won't touch:</p>

        <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
          {BEHAVIOR.map((b) => (
            <article
              key={b.title}
              className="flex gap-2.5 rounded-md border border-border bg-surface px-3.5 py-3"
            >
              <span className="font-bold text-green" aria-hidden="true">
                ✓
              </span>
              <div>
                <h3 className="text-[13.5px] font-semibold text-ink-1">
                  {b.title}
                </h3>
                <p className="text-xs text-ink-3">
                  {b.monoDesc ? (
                    <code className="rounded-[3px] border border-border bg-input px-1.5 py-px font-mono text-[12.5px] text-code-name">
                      {b.desc}
                    </code>
                  ) : (
                    b.desc
                  )}
                </p>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Self-Host Installation */}
      <section id="install" aria-labelledby="install-heading">
        <h2
          id="install-heading"
          className="mb-3.5 text-[30px] font-bold tracking-tight"
        >
          Self-Host: Installation
        </h2>
        <p className="mb-6 max-w-[64ch] text-lg text-pretty text-ink-2">
          Prefer to run your own instance? Six steps from clone to running bot.
        </p>

        <Step number={1} title="Clone Repository">
          <CodeBlock>
            <Comment># Clone</Comment>
            {"\ngit clone https://github.com/wei/thread-it.git\ncd thread-it"}
          </CodeBlock>
        </Step>

        <Step number={2} title="Install Dependencies">
          <CodeBlock>
            {"python -m venv venv\nsource venv/bin/activate  "}
            <Comment># Windows: venv\\Scripts\\activate</Comment>
            {"\npip install -r requirements.txt"}
          </CodeBlock>
        </Step>

        <Step number={3} title="Create a Discord Bot">
          <p className="text-ink-2">
            Create a new Discord application and bot in the{" "}
            <a
              href="https://discord.com/developers/applications"
              target="_blank"
              rel="noopener noreferrer"
              className="text-link hover:underline"
            >
              Discord Developer Portal
            </a>
            .
          </p>
        </Step>

        <Step number={4} title="Configure Bot Permissions">
          <p className="mb-3 text-ink-2">
            Grant the required permissions and enable the privileged Message
            Content Intent.
          </p>
          <div className="overflow-hidden rounded-md border border-border">
            <PermSection label="Required" perms={REQUIRED_PERMS} />
            <PermSection
              label="Recommended"
              note="Optional — without this, threads still get created; original replies just won't be cleaned up."
              perms={RECOMMENDED_PERMS}
            />
            <div className="border-t border-border bg-white/[0.02] px-4 py-3">
              <h3 className="mb-1 text-[12px] font-bold tracking-wider text-ink-3 uppercase">
                Gateway Intents
              </h3>
              <ul className="text-[13.5px] text-ink-2">
                <li className="flex items-center gap-2">
                  <span className="font-mono text-xs text-code-name">
                    MESSAGE_CONTENT
                  </span>
                  <span className="text-xs text-ink-3">(privileged)</span>
                </li>
              </ul>
            </div>
          </div>
        </Step>

        <Step number={5} title="Set Environment Variables">
          <CodeBlock>
            {"cp .env.example .env\n"}
            <Comment># Edit .env</Comment>
            {"\nDISCORD_TOKEN="}
            <Str>your_bot_token_here</Str>
            {"\nLOG_LEVEL="}
            <Str>INFO</Str>
          </CodeBlock>
        </Step>

        <Step number={6} title="Run the Bot">
          <CodeBlock>python bot.py</CodeBlock>
        </Step>

        {/* Hosted-version callout — full border + tint, no side stripe */}
        <aside
          className="mt-9 rounded-lg border border-green/30 bg-green/[0.08] px-5 py-4"
          role="note"
        >
          <h3 className="mb-1 text-[12.5px] font-bold tracking-wider text-green uppercase">
            Skip the self-host
          </h3>
          <p className="text-sm text-ink-2">
            The hosted version is free, MIT licensed, and runs the same code.{" "}
            <a
              href={INVITE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-link hover:underline"
            >
              Invite it
              <ExternalLink className="size-3.5" aria-hidden="true" />
            </a>
          </p>
        </aside>
      </section>
    </>
  );
}

function Step({
  number,
  title,
  children,
}: {
  number: number;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <h3 className="mt-7 mb-2 text-[17px] font-semibold text-ink-1">
        {number} · {title}
      </h3>
      {children}
    </div>
  );
}

function PermSection({
  label,
  perms,
  note,
}: {
  label: string;
  perms: readonly (readonly [string, string])[];
  note?: string;
}) {
  return (
    <div className="border-b border-border last:border-b-0">
      <div className="bg-white/[0.02] px-4 pt-3 pb-1.5">
        <h3 className="text-[12px] font-bold tracking-wider text-ink-3 uppercase">
          {label}
        </h3>
        {note && <p className="mt-1 text-[12.5px] text-ink-3">{note}</p>}
      </div>
      <ul className="divide-y divide-border">
        {perms.map(([name, purpose]) => (
          <li
            key={name}
            className="flex flex-col gap-0.5 px-4 py-2.5 text-[13.5px] sm:grid sm:grid-cols-[220px_1fr] sm:gap-4"
          >
            <span className="font-medium text-ink-1">{name}</span>
            <span className="text-ink-2">{purpose}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function CodeBlock({ children }: { children: React.ReactNode }) {
  return (
    <pre className="max-w-full overflow-x-auto rounded-md border border-border bg-input px-4 py-3.5 font-mono text-[13px] leading-[1.65] text-ink-1">
      {children}
    </pre>
  );
}

function Comment({ children }: { children: React.ReactNode }) {
  return <span className="text-ink-3">{children}</span>;
}

function Str({ children }: { children: React.ReactNode }) {
  return <span className="text-code-str">{children}</span>;
}
