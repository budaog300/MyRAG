import { HeroSection } from '../components/sections/HeroSection';
import { ProblemSection } from '../components/sections/ProblemSection';
import { SolutionSection } from '../components/sections/SolutionSection';
import { RagDemoSection } from '../components/sections/RagDemoSection';
import { CapabilitiesSection } from '../components/sections/CapabilitiesSection';
// import { DocumentsSection } from '../components/sections/DocumentsSection';
import { HowItWorksSection } from '../components/sections/HowItWorksSection';
import { ScenariosSection } from '../components/sections/ScenariosSection';
import { ArchitectureSection } from '../components/sections/ArchitectureSection';
import { DeploymentSection } from '../components/sections/DeploymentSection';
import { PilotSection } from '../components/sections/PilotSection';
import { FaqSection, FaqSchema } from '../components/sections/FaqSection';
import { FinalCtaSection } from '../components/sections/FinalCtaSection';
import { ContactSection } from '../components/sections/ContactSection';

export function LandingPage() {
  return (
    <>
      <HeroSection />
      <ProblemSection />
      <SolutionSection />
      <RagDemoSection />
      <CapabilitiesSection />
      <HowItWorksSection />
      <ScenariosSection />
      <ArchitectureSection />
      <DeploymentSection />
      <PilotSection />
      <FaqSection />
      <FinalCtaSection />
      <ContactSection />
      <FaqSchema />
    </>
  );
}
