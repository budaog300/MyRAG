import { finalCtaContent } from '../../data/landing';
import { Button } from '../ui/Button';
import { Reveal } from '../ui/Reveal';
import { Section } from '../ui/Section';

export function FinalCtaSection() {
  return (
    <Section
      tone="dark"
      aria-labelledby="final-cta-heading"
      className="relative overflow-hidden"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_90%_at_50%_120%,rgba(34,169,142,0.16),transparent)]"
      />
      <div className="relative mx-auto max-w-3xl text-center">
        <Reveal>
          <p className="text-xs font-semibold tracking-[0.2em] text-accent-300 uppercase">
            {finalCtaContent.eyebrow}
          </p>
          <h2
            id="final-cta-heading"
            className="mt-4 text-balance text-3xl font-bold tracking-tight text-white sm:text-4xl"
          >
            {finalCtaContent.title}
          </h2>
          <p className="mt-5 text-base leading-relaxed text-slate-400 sm:text-lg">
            {finalCtaContent.description}
          </p>
          <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button href={finalCtaContent.primaryCta.href} size="lg" variant="dark">
              {finalCtaContent.primaryCta.label}
            </Button>
            <Button href={finalCtaContent.secondaryCta.href} variant="ghost" size="lg" className="text-slate-300 hover:bg-white/10 hover:text-white">
              {finalCtaContent.secondaryCta.label}
            </Button>
          </div>
          <p className="mt-6 text-xs text-slate-500">{finalCtaContent.note}</p>
        </Reveal>
      </div>
    </Section>
  );
}
