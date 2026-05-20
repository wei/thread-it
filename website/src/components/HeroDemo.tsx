import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

/*
 * HeroDemo — animated Discord channel that loops through 11 phases over ~19s.
 * Matches the actual bot behavior in `bot.py`: detect reply → delete original →
 * create thread on parent message → send auto-deleting notification.
 *
 * Two parallel conversations (Alice/Carol parents, Bob/Dan replies) get
 * reorganized into their respective threads, with each thread creation
 * staggered so each is clearly visible (red flash for delete, green flash
 * for thread creation).
 *
 * Phase | t (s)        | Event
 * ------|--------------|------------------------------------------------
 *   1   |  0.0– 1.4    | Alice posts Message 1
 *   2   |  1.4– 3.0    | Carol posts Message 2
 *   3   |  3.0– 4.4    | Bob replies to Alice
 *   4   |  4.4– 6.1    | Dan replies to Carol (all 4 visible)
 *   5   |  6.1– 6.8    | Bob's reply red-flash deletes
 *   6   |  6.8– 8.3    | Thread 1 appears on Alice with green flash
 *   7   |  8.3– 9.0    | Dan's reply red-flash deletes
 *   8   |  9.0–10.5    | Thread 2 appears on Carol with green flash
 *   9   | 10.5–15.0    | Bot notifications appear
 *  10   | 15.0–18.5    | Notifications auto-delete, final state holds
 *   0   | 18.5–19.0    | Reset
 *
 * Animation uses transform (scaleY) + opacity + backgroundColor only.
 * No layout properties (height, padding, margin) are animated — the
 * card holds a stable min-height to avoid layout thrash.
 */

const PHASE_DURATIONS_MS = [
  400, // → phase 1 (Alice at 0.4s)
  1000, // → phase 2 (Carol at 1.4s)
  1600, // → phase 3 (Bob at 3.0s)
  1400, // → phase 4 (Dan at 4.4s, all 4 visible)
  1700, // → phase 5 (Bob deletion at 6.1s)
  700, // → phase 6 (Thread 1 created at 6.8s, green flash)
  1500, // → phase 7 (Dan deletion at 8.3s)
  700, // → phase 8 (Thread 2 created at 9.0s, green flash)
  1500, // → phase 9 (notifications at 10.5s)
  4500, // → phase 10 (notifications collapse at 15.0s)
  3500, // → phase 0 (reset at 18.5s)
];

const RED_FLASH_DURATION = 0.6; // s

function useLocalTime(): string {
  const [time, setTime] = useState("--:--");
  useEffect(() => {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    setTime(`${hh}:${mm}`);
  }, []);
  return time;
}

const STEP_LABELS = [
  "00 · idle",
  "01 · message 1",
  "02 · message 2",
  "03 · reply to msg 1",
  "04 · reply to msg 2",
  "05 · deleting reply 1",
  "06 · thread 1 created",
  "07 · deleting reply 2",
  "08 · thread 2 created",
  "09 · notifying users",
  "10 · cleaned up",
];

function Avatar({
  color,
  letter,
  size = 36,
}: {
  color: string;
  letter: string;
  size?: number;
}) {
  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-full font-bold text-white"
      style={{
        width: size,
        height: size,
        background: color,
        fontSize: size * 0.42,
      }}
      aria-hidden="true"
    >
      {letter}
    </div>
  );
}

function ReplyContext({
  fromColor,
  fromLetter,
  fromName,
  preview,
}: {
  fromColor: string;
  fromLetter: string;
  fromName: string;
  preview: string;
}) {
  return (
    <div className="mb-px flex items-center gap-1.5 text-[12.5px] leading-tight text-ink-3">
      <span
        className="-mb-0.5 mr-0.5 size-[14px] shrink-0 border-t-2 border-l-2 border-reply-hook"
        style={{ borderTopLeftRadius: 6, height: 8, width: 14 }}
        aria-hidden="true"
      />
      <Avatar color={fromColor} letter={fromLetter} size={14} />
      <span className="font-medium text-ink-2">{fromName}</span>
      <span className="max-w-[200px] truncate text-ink-3">{preview}</span>
    </div>
  );
}

function ThreadFooter({ title }: { title: string }) {
  return (
    <div className="inline-flex w-fit items-center gap-2 rounded-md border border-blurple/30 bg-blurple/[0.06] px-2.5 py-1.5 text-[12.5px] leading-tight text-ink-2">
      <ThreadFooterContent title={title} />
    </div>
  );
}

function ThreadFooterContent({ title }: { title: string }) {
  return (
    <>
      <span className="text-[13px] text-blurple">🧵</span>
      <span className="font-medium text-ink-1">{title}</span>
      <span className="text-[11.5px] text-ink-3">· 1 message</span>
      <span className="ml-0.5 text-[11px] text-ink-3">›</span>
    </>
  );
}

function AnimatedThreadFooter({ title }: { title: string }) {
  return (
    <motion.div
      className="inline-flex w-fit items-center gap-2 rounded-md border px-2.5 py-1.5 text-[12.5px] leading-tight text-ink-2"
      style={{ originY: 0 }}
      initial={THREAD_FLASH.initial}
      animate={THREAD_FLASH.animate}
      exit={THREAD_FLASH.exit}
    >
      <ThreadFooterContent title={title} />
    </motion.div>
  );
}

function Message({
  letter,
  color,
  name,
  time,
  children,
  replyContext,
  threadFooter,
}: {
  letter: string;
  color: string;
  name: string;
  time: string;
  children: React.ReactNode;
  replyContext?: React.ReactNode;
  threadFooter?: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-[40px_1fr] gap-3 py-[3px]">
      <Avatar color={color} letter={letter} />
      <div className="min-w-0">
        {replyContext}
        <div className="text-[14.5px] font-medium text-ink-1">
          {name}
          <span className="ml-2 text-[11.5px] font-normal text-ink-3">
            {time}
          </span>
        </div>
        <div className="mt-px text-[14.5px] leading-[1.5] text-ink-1">
          {children}
        </div>
        {threadFooter}
      </div>
    </div>
  );
}

function BotNotification({
  mention,
  channelRef,
  time,
}: {
  mention: string;
  channelRef: string;
  time: string;
}) {
  return (
    <div className="grid grid-cols-[40px_1fr] gap-3 py-[3px]">
      <div className="flex size-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blurple to-fuchsia">
        <img
          src="/thread-it-icon.png"
          alt=""
          width={34}
          height={34}
          loading="lazy"
          decoding="async"
          className="size-[34px] rounded-full"
          aria-hidden="true"
        />
      </div>
      <div className="min-w-0">
        <div className="text-[14.5px] font-medium text-ink-1">
          Thread It
          <span className="ml-1.5 inline-flex items-center rounded-[3px] bg-blurple px-1.5 py-px align-middle text-[9.5px] font-bold tracking-wider text-white">
            APP
          </span>
          <span className="ml-2 text-[11.5px] font-normal text-ink-3">
            {time}
          </span>
        </div>
        <div className="mt-px text-[14px] leading-[1.45] text-ink-2">
          <span className="rounded-[3px] bg-blurple/[0.18] px-[3px] font-medium text-mention-text">
            {mention}
          </span>
          , please continue your conversation in{" "}
          <span className="rounded-[3px] bg-blurple/[0.18] px-1 font-medium text-mention-text">
            <span className="text-xs">🧵 </span>
            {channelRef}
          </span>
          .
        </div>
      </div>
    </div>
  );
}

const ENTER = {
  initial: { opacity: 0, scaleY: 0 },
  animate: { opacity: 1, scaleY: 1 },
  exit: { opacity: 0, scaleY: 0 },
};

// Thread footer green-flash on creation, settling to its normal blurple tint.
// The chip itself fades + scales in once and STAYS. The background + border
// independently flash green then settle. Separate per-property transitions
// so the flash doesn't drag the chip's scale/opacity along with it.
const FLASH_BG_KEYFRAMES = [
  "rgba(63, 187, 110, 0.50)",
  "rgba(63, 187, 110, 0.32)",
  "rgba(63, 187, 110, 0.12)",
  "rgba(88, 101, 242, 0.06)",
];
const FLASH_BORDER_KEYFRAMES = [
  "rgba(63, 187, 110, 0.85)",
  "rgba(63, 187, 110, 0.55)",
  "rgba(63, 187, 110, 0.25)",
  "rgba(88, 101, 242, 0.28)",
];
const FLASH_TIMES = [0, 0.25, 0.55, 1];

const THREAD_FLASH = {
  initial: {
    opacity: 0,
    scaleY: 0.7,
    marginTop: 6,
    backgroundColor: FLASH_BG_KEYFRAMES[0],
    borderColor: FLASH_BORDER_KEYFRAMES[0],
  },
  animate: {
    opacity: 1,
    scaleY: 1,
    marginTop: 6,
    backgroundColor: FLASH_BG_KEYFRAMES,
    borderColor: FLASH_BORDER_KEYFRAMES,
    transition: {
      // Opacity + scale: snap in fast and stay
      opacity: { duration: 0.3, ease: [0.16, 1, 0.3, 1] },
      scaleY: { duration: 0.3, ease: [0.16, 1, 0.3, 1] },
      marginTop: { duration: 0.3 },
      // Color flash: longer, decays through 4 keyframes
      backgroundColor: {
        duration: 1.1,
        times: FLASH_TIMES,
        ease: "easeOut",
      },
      borderColor: {
        duration: 1.1,
        times: FLASH_TIMES,
        ease: "easeOut",
      },
    },
  },
  exit: {
    opacity: 0,
    scaleY: 0,
    marginTop: 0,
    transition: { duration: 0.25 },
  },
};

const REPLY_ENTER_EXIT = {
  initial: { opacity: 0, scaleY: 0, backgroundColor: "rgba(242,63,67,0)" },
  animate: { opacity: 1, scaleY: 1, backgroundColor: "rgba(242,63,67,0)" },
  // Red flash → fade. Background animation happens via custom variant.
  exit: {
    opacity: [1, 1, 1, 0.5, 0],
    backgroundColor: [
      "rgba(242,63,67,0)",
      "rgba(242,63,67,0.32)",
      "rgba(242,63,67,0.22)",
      "rgba(242,63,67,0.10)",
      "rgba(242,63,67,0)",
    ],
    scaleY: [1, 1, 1, 1, 0],
    transition: {
      duration: RED_FLASH_DURATION,
      times: [0, 0.2, 0.45, 0.75, 1],
    },
  },
};

const ENTER_TRANSITION = {
  duration: 0.35,
  ease: [0.16, 1, 0.3, 1], // ease-out-quart-ish
};

export function HeroDemoStatic() {
  const time = useLocalTime();
  return (
    <DemoFrame phaseLabel="08 · cleaned up">
      <Message
        letter="A"
        color="var(--color-user-a)"
        name="Alice"
        time={time}
        threadFooter={
          <div className="mt-1.5">
            <ThreadFooter title="What's everyone's favorite Python library?" />
          </div>
        }
      >
        What&apos;s everyone&apos;s favorite Python library?
      </Message>
      <Message
        letter="C"
        color="var(--color-user-c)"
        name="Carol"
        time={time}
        threadFooter={
          <div className="mt-1.5">
            <ThreadFooter title="Anyone tried the new Discord activities?" />
          </div>
        }
      >
        Anyone tried the new Discord activities?
      </Message>
    </DemoFrame>
  );
}

function DemoFrame({
  phaseLabel,
  children,
}: {
  phaseLabel: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="relative isolate overflow-hidden rounded-[14px] border border-border bg-surface shadow-[0_32px_80px_rgba(0,0,0,0.6)]"
      aria-hidden="true"
    >
      <div
        className="pointer-events-none absolute -inset-px -z-10 rounded-[15px] opacity-60"
        style={{
          background:
            "linear-gradient(135deg, rgba(88,101,242,0.55), transparent 50%, rgba(235,69,158,0.3))",
        }}
      />
      <div className="flex items-center gap-2.5 border-b border-border bg-black/[0.35] px-4 py-3 text-[13.5px]">
        <span className="text-lg font-semibold text-ink-3">#</span>
        <span className="font-semibold">general</span>
        <span className="ml-auto inline-flex items-center gap-1.5 rounded-full border border-border bg-white/[0.04] px-2.5 py-[3px] font-mono text-[11px] text-ink-3">
          <span className="size-[5px] rounded-full bg-green shadow-[0_0_6px_var(--color-green)]" />
          <span>{phaseLabel}</span>
        </span>
      </div>
      <div className="min-h-[460px] space-y-1 px-5 py-[22px]">{children}</div>
    </div>
  );
}

export function HeroDemo() {
  const reduce = useReducedMotion();
  const time = useLocalTime();
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    if (reduce) return;
    const timeouts: ReturnType<typeof setTimeout>[] = [];
    let cancelled = false;

    function startCycle() {
      let cumulative = 0;
      for (let i = 0; i < PHASE_DURATIONS_MS.length; i++) {
        cumulative += PHASE_DURATIONS_MS[i];
        const targetPhase = (i + 1) % PHASE_DURATIONS_MS.length;
        const id = setTimeout(() => {
          if (cancelled) return;
          if (document.visibilityState !== "visible") return;
          setPhase(targetPhase);
          if (targetPhase === 0) startCycle();
        }, cumulative);
        timeouts.push(id);
      }
    }

    function clearScheduled() {
      timeouts.forEach(clearTimeout);
      timeouts.length = 0;
    }

    function onVisibilityChange() {
      if (document.visibilityState === "visible") {
        startCycle();
      } else {
        clearScheduled();
      }
    }

    startCycle();
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      cancelled = true;
      clearScheduled();
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, [reduce]);

  if (reduce) {
    return <HeroDemoStatic />;
  }

  // Visibility windows. Deletion (phase 5/7) and thread creation (phase 6/8)
  // are now distinct so each event is clearly seen.
  const alice = phase >= 1;
  const carol = phase >= 2;
  const bob = phase >= 3 && phase < 5; // exits during phase 5 (red flash)
  const dan = phase >= 4 && phase < 7; // exits during phase 7 (red flash)
  const thread1 = phase >= 6; // mounts at phase 6 with green flash
  const thread2 = phase >= 8; // mounts at phase 8 with green flash
  const notif1 = phase >= 9 && phase < 10;
  const notif2 = phase >= 9 && phase < 10;

  return (
    <DemoFrame phaseLabel={STEP_LABELS[phase]}>
      <AnimatePresence initial={false}>
        {alice && (
          <motion.div
            key="alice"
            style={{ originY: 0 }}
            initial={ENTER.initial}
            animate={ENTER.animate}
            exit={ENTER.exit}
            transition={ENTER_TRANSITION}
          >
            <Message
              letter="A"
              color="var(--color-user-a)"
              name="Alice"
              time={time}
              threadFooter={
                <AnimatePresence initial={false}>
                  {thread1 && (
                    <AnimatedThreadFooter
                      key="thread1"
                      title="What's everyone's favorite Python library?"
                    />
                  )}
                </AnimatePresence>
              }
            >
              What&apos;s everyone&apos;s favorite Python library?
            </Message>
          </motion.div>
        )}

        {carol && (
          <motion.div
            key="carol"
            style={{ originY: 0 }}
            initial={ENTER.initial}
            animate={ENTER.animate}
            exit={ENTER.exit}
            transition={ENTER_TRANSITION}
          >
            <Message
              letter="C"
              color="var(--color-user-c)"
              name="Carol"
              time={time}
              threadFooter={
                <AnimatePresence initial={false}>
                  {thread2 && (
                    <AnimatedThreadFooter
                      key="thread2"
                      title="Anyone tried the new Discord activities?"
                    />
                  )}
                </AnimatePresence>
              }
            >
              Anyone tried the new Discord activities?
            </Message>
          </motion.div>
        )}

        {bob && (
          <motion.div
            key="bob"
            className="-mx-2 overflow-hidden rounded-[4px] px-2"
            style={{ originY: 0 }}
            initial={REPLY_ENTER_EXIT.initial}
            animate={REPLY_ENTER_EXIT.animate}
            exit={REPLY_ENTER_EXIT.exit}
            transition={ENTER_TRANSITION}
          >
            <Message
              letter="B"
              color="var(--color-user-b)"
              name="Bob"
              time={time}
              replyContext={
                <ReplyContext
                  fromColor="var(--color-user-a)"
                  fromLetter="A"
                  fromName="Alice"
                  preview="What's everyone's favorite Python library?"
                />
              }
            >
              I love <strong>requests</strong> for HTTP calls!
            </Message>
          </motion.div>
        )}

        {dan && (
          <motion.div
            key="dan"
            className="-mx-2 overflow-hidden rounded-[4px] px-2"
            style={{ originY: 0 }}
            initial={REPLY_ENTER_EXIT.initial}
            animate={REPLY_ENTER_EXIT.animate}
            exit={REPLY_ENTER_EXIT.exit}
            transition={ENTER_TRANSITION}
          >
            <Message
              letter="D"
              color="var(--color-user-d)"
              name="Dan"
              time={time}
              replyContext={
                <ReplyContext
                  fromColor="var(--color-user-c)"
                  fromLetter="C"
                  fromName="Carol"
                  preview="Anyone tried the new Discord activities?"
                />
              }
            >
              Yeah, Watch Together is great for movie nights!
            </Message>
          </motion.div>
        )}

        {notif1 && (
          <motion.div
            key="notif1"
            style={{ originY: 0 }}
            initial={ENTER.initial}
            animate={ENTER.animate}
            exit={ENTER.exit}
            transition={ENTER_TRANSITION}
          >
            <BotNotification
              mention="@Bob"
              channelRef="whats-everyones-favorite-python-library"
              time={time}
            />
          </motion.div>
        )}

        {notif2 && (
          <motion.div
            key="notif2"
            style={{ originY: 0 }}
            initial={ENTER.initial}
            animate={ENTER.animate}
            exit={ENTER.exit}
            transition={ENTER_TRANSITION}
          >
            <BotNotification
              mention="@Dan"
              channelRef="anyone-tried-the-new-discord-activities"
              time={time}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </DemoFrame>
  );
}
