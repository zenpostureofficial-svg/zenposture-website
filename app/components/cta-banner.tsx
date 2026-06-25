'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Shield, Truck, BadgeCheck, Flame, Package } from 'lucide-react';

function useCountdown(hours = 3) {
  const [timeLeft, setTimeLeft] = useState({ h: hours, m: 0, s: 0 });
  useEffect(() => {
    const end = Date.now() + hours * 3600 * 1000;
    const tick = () => {
      const diff = Math.max(0, end - Date.now());
      setTimeLeft({
        h: Math.floor(diff / 3600000),
        m: Math.floor((diff % 3600000) / 60000),
        s: Math.floor((diff % 60000) / 1000),
      });
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [hours]);
  return timeLeft;
}

export default function CtaBanner() {
  const { h, m, s } = useCountdown(3);
  const pad = (n: number) => String(n).padStart(2, '0');

  return (
    <section className="py-20 lg:py-28 bg-gradient-dark text-white relative overflow-hidden">
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 relative text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          {/* Urgency badge */}
          <div className="inline-flex items-center gap-2 bg-red-500/20 text-red-300 px-4 py-1.5 rounded-full text-sm font-semibold mb-6 border border-red-500/30 animate-pulse-soft">
            <Flame className="w-4 h-4" />
            <span>Flash Sale — Offer Expires In</span>
            <span className="font-mono font-bold bg-red-500/30 px-2 py-0.5 rounded">
              {pad(h)}:{pad(m)}:{pad(s)}
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display leading-tight">
            Don&apos;t Let Bad Posture
            <br />
            <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Hold You Back
            </span>
          </h2>

          <p className="mt-6 text-lg text-white/70 max-w-2xl mx-auto">
            Join 10,000+ Indians who have transformed their posture and health.
            Premium products starting at just ₹499 with free shipping across India.
          </p>

          {/* Stock warning */}
          <div className="mt-6 inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/20 text-amber-300 text-sm px-4 py-2 rounded-full">
            <Package className="w-4 h-4" />
            <span className="font-medium">Only 47 units left at sale price — selling fast!</span>
          </div>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/products"
              className="group bg-gradient-brand text-white px-10 py-4 rounded-full text-lg font-bold hover:shadow-xl hover:shadow-emerald-500/30 transition-all hover:-translate-y-1 flex items-center gap-2"
            >
              Claim Your Discount Now
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/products"
              className="text-white/60 hover:text-white text-sm underline underline-offset-4 transition-colors"
            >
              Browse all products →
            </Link>
          </div>

          {/* Trust badges */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-white/50">
            {[
              { icon: Truck, text: 'Free Shipping Pan India' },
              { icon: BadgeCheck, text: 'COD Available' },
              { icon: Shield, text: '30-Day Money Back' },
            ].map((item) => (
              <div key={item.text} className="flex items-center gap-2 text-sm">
                <item.icon className="w-4 h-4" />
                <span>{item.text}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

