import { type ReactNode, useEffect, useState } from "react";

const SIDEBAR_SECTIONS = [
  {
    label: "Getting Started",
    items: [
      { id: "how-it-works", href: "#how-it-works", label: "How It Works" },
      { id: "features", href: "#features", label: "Features" },
      { id: "behavior", href: "#behavior", label: "Bot Behavior" },
    ],
  },
  {
    label: "Self-Hosting",
    items: [{ id: "install", href: "#install", label: "Installation" }],
  },
  {
    label: "Resources",
    items: [
      {
        href: "https://github.com/wei/thread-it",
        label: "GitHub",
        external: true,
      },
      {
        href: "https://github.com/wei/thread-it/issues",
        label: "Issues",
        external: true,
      },
      {
        href: "https://github.com/wei/thread-it/blob/main/LICENSE",
        label: "MIT License",
        external: true,
      },
    ],
  },
];

const SECTION_IDS = ["how-it-works", "features", "behavior", "install"];

function useActiveSection(): string {
  const [active, setActive] = useState<string>(() => {
    if (typeof window === "undefined") return SECTION_IDS[0];
    const hash = window.location.hash.replace("#", "");
    return SECTION_IDS.includes(hash) ? hash : SECTION_IDS[0];
  });

  useEffect(() => {
    const targets = SECTION_IDS.map((id) => document.getElementById(id)).filter(
      (el): el is HTMLElement => el !== null
    );
    if (!targets.length) return;

    // Activation band sits just below viewport middle so a section only
    // becomes active once its top crosses ~55% from the top.
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) {
          setActive(visible[0].target.id);
        }
      },
      { rootMargin: "-55% 0px -40% 0px", threshold: 0 }
    );

    for (const t of targets) observer.observe(t);
    return () => observer.disconnect();
  }, []);

  return active;
}

export default function DocsLayout({ children }: { children: ReactNode }) {
  const active = useActiveSection();
  return (
    <div className="mx-auto grid w-full max-w-[1280px] grid-cols-1 md:grid-cols-[240px_1fr] lg:grid-cols-[280px_1fr]">
      <DocsSidebar active={active} />
      <main className="min-w-0 px-6 py-10 md:px-10 md:pt-12 md:pb-20">
        {children}
      </main>
    </div>
  );
}

function DocsSidebar({ active }: { active: string }) {
  return (
    <aside
      className="sticky top-0 hidden h-screen overflow-y-auto border-r border-border bg-surface-soft py-9 md:block"
      aria-label="Docs navigation"
    >
      {SIDEBAR_SECTIONS.map((section) => (
        <nav key={section.label} className="px-4 py-1.5">
          <p className="px-2 pt-3.5 pb-1 text-[11px] font-bold tracking-wider text-ink-3 uppercase">
            {section.label}
          </p>
          <ul>
            {section.items.map((item) => {
              const isActive = "id" in item && item.id === active;
              return (
                <li key={item.href}>
                  <a
                    href={item.href}
                    {...("external" in item && item.external
                      ? { target: "_blank", rel: "noopener noreferrer" }
                      : {})}
                    aria-current={isActive ? "page" : undefined}
                    className={
                      isActive
                        ? "flex min-h-11 items-center gap-2.5 rounded-[5px] bg-blurple/[0.14] px-2.5 py-2.5 text-sm font-medium text-ink-1"
                        : "flex min-h-11 items-center gap-2.5 rounded-[5px] px-2.5 py-2.5 text-sm font-medium text-ink-2 transition-colors hover:bg-surface hover:text-ink-1"
                    }
                  >
                    <span
                      className={
                        isActive
                          ? "size-[5px] shrink-0 rounded-full bg-blurple"
                          : "size-[5px] shrink-0 rounded-full bg-ink-3 opacity-50"
                      }
                      aria-hidden="true"
                    />
                    {item.label}
                  </a>
                </li>
              );
            })}
          </ul>
        </nav>
      ))}
    </aside>
  );
}
