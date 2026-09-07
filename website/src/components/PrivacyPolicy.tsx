export default function PrivacyPolicy() {
  return (
    <section id="privacy" aria-labelledby="privacy-heading">
      <h2
        id="privacy-heading"
        className="mb-3.5 text-[30px] font-bold tracking-tight"
      >
        Privacy Policy
      </h2>
      <p className="mb-6 max-w-[64ch] text-sm text-ink-3">
        Last updated: September 7, 2026
      </p>

      <div className="max-w-[72ch] space-y-6 text-[15px] leading-relaxed text-ink-2">
        <div>
          <h3 className="mb-2 text-lg font-semibold text-ink-1">
            Messages are not stored
          </h3>
          <p>
            Thread It does <strong className="text-ink-1">not</strong> store
            messages or attachments in a database. It temporarily processes
            message data through Discord&apos;s API to create a thread and
            repost a reply, then does not retain the message content or
            attachment files.
          </p>
          <p className="mt-3">
            Messages and attachments may continue to exist in Discord according
            to Discord&apos;s policies and the settings of your server.
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-lg font-semibold text-ink-1">
            Information processed
          </h3>
          <p>
            To provide its features, Thread It may receive message content,
            replies, embeds, attachments, Discord IDs, and server and channel
            permissions. It does not sell this information or use it for
            advertising.
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-lg font-semibold text-ink-1">
            Logs and third parties
          </h3>
          <p>
            Operational logs may contain limited metadata, such as IDs, counts,
            error details, and timing information. Message content is not
            intentionally written to logs. Thread It uses Discord&apos;s API;
            Discord&apos;s handling of information is governed by{" "}
            <a
              href="https://discord.com/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-link hover:underline"
            >
              Discord&apos;s Privacy Policy
            </a>
            .
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-lg font-semibold text-ink-1">
            Self-hosting and contact
          </h3>
          <p>
            If you run your own instance, you are responsible for its deployment
            environment, logs, and any data it retains. Questions can be raised
            through the{" "}
            <a
              href="https://github.com/wei/thread-it/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="text-link hover:underline"
            >
              Thread It issue tracker
            </a>
            .
          </p>
        </div>
      </div>
    </section>
  );
}
