import { heroContent } from '../../data/landing';
import { HeroDemoMockup } from '../demo/HeroDemoMockup';
import { Button } from '../ui/Button';
import { Container } from '../ui/Container';
import { Reveal } from '../ui/Reveal';

export function HeroSection() {
  return (
    <section
      id="top"
      aria-labelledby="hero-heading"
      className="relative overflow-hidden bg-white pt-32 pb-20 sm:pt-40 sm:pb-24 lg:pt-44 lg:pb-28"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 [background-image:linear-gradient(to_right,rgba(15,23,42,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(15,23,42,0.04)_1px,transparent_1px)] [background-size:56px_56px] [mask-image:radial-gradient(ellipse_70%_60%_at_50%_0%,black,transparent)]"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-accent-50/80 to-transparent"
      />

      <Container className="relative">
        <div className="grid items-center gap-12 lg:grid-cols-[minmax(0,11fr)_minmax(0,10fr)] lg:gap-16">
          <Reveal>
            <p className="inline-flex items-center gap-2 rounded-full border border-accent-200 bg-accent-50 px-3.5 py-1.5 text-xs font-semibold tracking-wide text-accent-700">
              <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-accent-500" aria-hidden="true" />
              {heroContent.eyebrow}
            </p>
            <h1
              id="hero-heading"
              className="mt-6 text-balance text-4xl leading-[1.08] font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-[3.4rem]"
            >
              {heroContent.title}
            </h1>
            <p className="mt-6 max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
              {heroContent.description}
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button href={heroContent.primaryCta.href} size="lg">
                {heroContent.primaryCta.label}
              </Button>
              <Button href={heroContent.secondaryCta.href} variant="secondary" size="lg">
                {heroContent.secondaryCta.label}
              </Button>
            </div>
            <p className="mt-8 text-xs font-medium tracking-wide text-slate-400 sm:text-[13px]">
              {heroContent.formatsLine}
            </p>
          </Reveal>

          <Reveal delay={120} className="min-w-0">
            <HeroDemoMockup />
          </Reveal>
        </div>
      </Container>
    </section>
  );
}
