import { Heart } from "lucide-react";
import GithubIcon from "./icons/GithubIcon";

export default function DocsFooter() {
  return (
    <footer className="mt-16 flex flex-col items-start justify-between gap-3 border-t border-border pt-7 text-[13px] text-ink-3 sm:flex-row sm:items-center">
      <p className="flex items-center gap-1.5">
        Made with
        <Heart className="size-3.5 fill-red text-red" aria-label="love" />
        by{" "}
        <a
          href="https://wei.me"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ink-2 hover:text-ink-1"
        >
          @wei
        </a>
        <span aria-hidden="true">·</span>
        <a
          href="https://github.com/wei/thread-it/blob/main/LICENSE"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ink-2 hover:text-ink-1"
        >
          MIT License
        </a>
      </p>
      <div className="flex items-center gap-4">
        <a
          href="https://github.com/wei/thread-it"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-ink-2 hover:text-ink-1"
        >
          <GithubIcon className="size-4" />
          GitHub
        </a>
        <a
          href="https://github.com/wei/thread-it/issues"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ink-2 hover:text-ink-1"
        >
          Issues
        </a>
        <a
          href="https://github.com/wei/thread-it#readme"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ink-2 hover:text-ink-1"
        >
          README
        </a>
      </div>
    </footer>
  );
}
