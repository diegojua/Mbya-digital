import React from 'react';

interface HeroProps {
  headline: string;
  subheadline: string;
  ctaText: string;
  whatsappLink: string;
}

export const HeroSection: React.FC<HeroProps> = ({ headline, subheadline, ctaText, whatsappLink }) => {
  return (
    <section className="relative min-h-[85vh] flex items-center bg-slate-950 px-6 py-16 md:px-12">
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7 flex flex-col items-start space-y-6 text-left">
          <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-2xl">
            {headline}
          </h1>
          <p className="text-lg md:text-xl text-slate-400 font-medium leading-relaxed max-w-xl">
            {subheadline}
          </p>
          <a
            href="{whatsappLink}"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-slate-950 bg-rose-500 hover:bg-rose-400 rounded-xl transition-all duration-200 transform hover:scale-[1.02] shadow-lg shadow-rose-500/20"
          >
            {ctaText}
          </a>
        </div>
        <div className="lg:col-span-5 w-full flex justify-center">
          <div className="relative w-full max-w-md aspect-square rounded-2xl bg-gradient-to-tr from-slate-900 to-slate-800 border border-slate-800 shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-slate-950/40 mix-blend-overlay" />
          </div>
        </div>
      </div>
    </section>
  );
};
