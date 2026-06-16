'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, Shield, Truck, BadgeCheck } from 'lucide-react';

export default function CtaBanner() {
  return (
    <section className="py-20 lg:py-28 bg-gradient-dark text-white relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />

      <div className="max-w-4xl mx-auto px-4 sm:px-6 relative text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm text-white/90 px-4 py-1.5 rounded-full text-sm font-medium mb-6 border border-white/10">
            🔥 Limited Time Launch Offer
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

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/products"
              className="group bg-gradient-brand text-white px-8 py-4 rounded-full text-lg font-bold hover:shadow-xl hover:shadow-emerald-500/30 transition-all hover:-translate-y-1 flex items-center gap-2"
            >
              Shop Now — Save Up to 63%
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {/* Trust badges */}
          <div className="mt-10 flex flex-wrap items-center justify-center gap-6 text-white/60">
            {[
              { icon: Truck, text: 'Free Shipping' },
              { icon: BadgeCheck, text: 'COD Available' },
              { icon: Shield, text: '30-Day Guarantee' },
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
