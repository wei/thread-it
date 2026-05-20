import { ArrowRight, Play, Star } from "lucide-react";
import { HeroDemo } from "./HeroDemo";

const INVITE_URL =
  "https://discord.com/oauth2/authorize?client_id=1386888801229734018";

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden border-b border-border">
      <div
        className="pointer-events-none absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 20% 20%, rgba(88,101,242,0.18), transparent 60%), radial-gradient(ellipse 50% 50% at 90% 80%, rgba(235,69,158,0.12), transparent 60%)",
        }}
        aria-hidden="true"
      />

      {/* Animated thread weave — paint-only animation (stroke-dashoffset) */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 overflow-hidden opacity-55"
        style={{
          maskImage:
            "radial-gradient(ellipse 90% 80% at 50% 50%, black 30%, transparent 90%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 90% 80% at 50% 50%, black 30%, transparent 90%)",
        }}
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 1440 900"
          preserveAspectRatio="xMidYMid slice"
          className="block size-full"
          role="presentation"
        >
          <path
            className="thread-path"
            d="M -50,200 Q 200,100 500,250 T 1000,180 T 1500,260"
            stroke="#5865F2"
            style={{ animationDelay: "0s" }}
          />
          <path
            className="thread-path"
            d="M -50,380 Q 300,280 600,420 T 1200,360 T 1500,440"
            stroke="#818CF8"
            style={{ animationDelay: "1.2s" }}
          />
          <path
            className="thread-path"
            d="M -50,560 Q 250,460 550,600 T 1100,540 T 1500,620"
            stroke="#EB459E"
            style={{ animationDelay: "2.4s", opacity: 0.6 }}
          />
          <path
            className="thread-path"
            d="M -50,720 Q 350,620 700,760 T 1300,700 T 1500,780"
            stroke="#C084FC"
            style={{ animationDelay: "3.6s", opacity: 0.7 }}
          />
          <path
            className="thread-path"
            d="M -50,80 Q 400,180 800,40 T 1500,140"
            stroke="#5865F2"
            style={{ animationDelay: "4.8s", opacity: 0.5 }}
          />
          <path
            className="thread-path"
            d="M -50,840 Q 450,740 900,880 T 1500,800"
            stroke="#F472B6"
            style={{ animationDelay: "6s", opacity: 0.5 }}
          />
        </svg>
      </div>

      <div className="relative z-10 mx-auto flex max-w-[1280px] items-center justify-between px-6 py-5 md:px-10">
        <a
          href="/"
          className="flex min-h-11 items-center gap-2.5 rounded-md px-1 text-base font-bold"
          aria-label="Thread It — home"
        >
          <img
            src="/thread-it-icon.png"
            alt=""
            width={28}
            height={28}
            className="size-7 rounded-md"
            aria-hidden="true"
          />
          <span>Thread It</span>
        </a>

        <nav className="hidden gap-1 sm:flex" aria-label="Primary">
          <a
            href="#how-it-works"
            className="inline-flex min-h-11 items-center rounded-md px-3.5 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1"
          >
            How it works
          </a>
          <a
            href="#features"
            className="inline-flex min-h-11 items-center rounded-md px-3.5 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1"
          >
            Features
          </a>
          <a
            href="#install"
            className="inline-flex min-h-11 items-center rounded-md px-3.5 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1"
          >
            Install
          </a>
          <a
            href="https://github.com/wei/thread-it"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-11 items-center rounded-md px-3.5 py-2 text-sm font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1"
          >
            GitHub
          </a>
        </nav>

        <div className="flex items-center gap-2.5">
          <a
            href="https://github.com/wei/thread-it"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden min-h-11 items-center gap-1.5 rounded-md px-3.5 py-2 text-[13.5px] font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1 sm:inline-flex"
          >
            <Star className="size-4" aria-hidden="true" />
            Star
          </a>
          <a
            href={INVITE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-11 items-center gap-2 rounded-md bg-blurple-deep px-4 py-2 text-[13.5px] font-semibold text-white transition-colors hover:bg-blurple"
          >
            Add to Discord
          </a>
        </div>
      </div>

      <div className="relative z-10 mx-auto grid max-w-[1280px] grid-cols-1 items-center gap-10 px-6 py-14 md:gap-16 md:px-10 lg:grid-cols-[1fr_1.05fr] lg:py-20">
        <div className="min-w-0">
          <span className="mb-7 inline-flex items-center gap-1.5 rounded-full border border-green/30 bg-green/10 px-3 py-[5px] text-xs font-semibold text-green">
            <span
              className="size-1.5 rounded-full bg-green shadow-[0_0_8px_var(--color-green)]"
              style={{ animation: "pulse-dot 2s ease-in-out infinite" }}
              aria-hidden="true"
            />
            Live · Free forever · Open source
          </span>

          <h1 className="mb-5 text-[clamp(46px,5.8vw,80px)] leading-[0.96] font-extrabold tracking-[-0.038em] text-balance">
            Every reply,
            <br />
            woven into a{" "}
            <span
              className="italic"
              style={{
                background:
                  "linear-gradient(110deg, #818cf8 10%, #c084fc 50%, #f472b6 90%)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                color: "transparent",
              }}
            >
              thread.
            </span>
          </h1>

          <p className="mb-9 max-w-[48ch] text-lg leading-[1.55] text-pretty text-ink-2">
            A Discord bot that keeps channels clean by converting replies into
            threads. Zero commands, zero config. Invite it, grant the
            permissions, walk away.
          </p>

          <div className="mb-9 flex flex-wrap items-center gap-3">
            <a
              href={INVITE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md bg-blurple-deep px-5 py-3 text-[15px] font-semibold text-white transition-colors hover:bg-blurple"
            >
              + Add to Discord
              <ArrowRight className="size-4" aria-hidden="true" />
            </a>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 rounded-md border border-white/10 bg-white/[0.06] px-5 py-3 text-[15px] font-semibold text-ink-1 transition-colors hover:bg-white/10"
            >
              Read the docs
            </a>
            <a
              href="https://x.com/weicodes/status/1939404324704264689"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-md px-3 py-3 text-[15px] font-medium text-ink-2 transition-colors hover:bg-white/[0.06] hover:text-ink-1"
            >
              <Play className="size-4 fill-current" aria-hidden="true" />
              Watch demo
            </a>
          </div>

          <dl className="grid grid-cols-2 gap-x-7 gap-y-[18px] border-t border-border pt-6 md:flex md:flex-row md:gap-0 md:pt-6">
            <Stat label="Setup" value="Zero config" />
            <Stat label="Runtime" value="Python 3.13" />
            <Stat label="Commands" value="Auto" />
            <Stat label="License" value="MIT" />
          </dl>
        </div>

        <div className="relative min-w-0">
          <p className="sr-only">
            Animated demonstration: when Bob replies to Alice and Dan replies to
            Carol in a Discord channel, Thread It creates a thread on each
            original message and removes the replies from the main channel.
          </p>
          <HeroDemo />
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-1 flex-col md:not-last:border-r md:not-last:border-border md:not-first:pl-6 md:not-last:pr-6">
      <dt className="text-[11px] font-bold tracking-wider text-ink-3 uppercase">
        {label}
      </dt>
      <dd className="text-[17px] font-bold tracking-tight text-ink-1">
        {value}
      </dd>
    </div>
  );
}
