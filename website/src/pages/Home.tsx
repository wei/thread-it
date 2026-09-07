import DocsFooter from "../components/DocsFooter";
import DocsLayout from "../components/DocsLayout";
import Features from "../components/Features";
import Hero from "../components/Hero";
import HowItWorks from "../components/HowItWorks";
import PrivacyPolicy from "../components/PrivacyPolicy";
import Setup from "../components/Setup";

export default function Home() {
  return (
    <>
      <Hero />
      <DocsLayout>
        <div className="space-y-18">
          <HowItWorks />
          <Features />
          <Setup />
          <PrivacyPolicy />
        </div>
        <DocsFooter />
      </DocsLayout>
    </>
  );
}
