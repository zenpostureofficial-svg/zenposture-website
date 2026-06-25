'use client';

import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const steps = [
  {
    number: '01',
    title: 'Wear It',
    description: 'Slip on your ZenPosture corrector in under 60 seconds. Fits under clothing.',
  },
  {
    number: '02',
    title: 'Feel It',
    description: 'Instant posture alignment from Day 1. Your muscles learn the correct position.',
  },
  {
    number: '03',
    title: 'Transform',
    description: '93% of users report less back pain within 2 weeks. Confidence that shows.',
  },
];

const beforeAfter = [
  { stat: '93%', label: 'reduced back pain in 2 weeks' },
  { stat: '10K+', label: 'happy customers across India' },
  { stat: '4.8★', label: 'average rating from verified buyers' },
  { stat: '30 days', label: 'money-back guarantee, no questions' },
];

export default function TransformationSection() {
  return (
    <section className="py-20 lg:py-28 bg-gradient-to-br from-slate-900 via-gray-900 to-emerald-950 text-white relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-emerald-500 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-teal-400 rounded-full blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 relative">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="inline-block bg-emerald-500/20 text-emerald-400 text-sm font-semibold px-4 py-1.5 rounded-full border border-emerald-500/30 mb-4">
            The ZenPosture Effect
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display">
            Three Steps to a
            <br />
            <span className="bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Pain-Free Life
            </span>
          </h2>
        </motion.div>

        {/* Steps */}
        <div className="grid sm:grid-cols-3 gap-6 lg:gap-8 mb-20">
          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="relative"
            >
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-colors">
                <div className="text-5xl font-bold font-display text-white/10 mb-4">{step.number}</div>
                <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                <p className="text-white/60 leading-relaxed">{step.description}</p>
              </div>
              {i < steps.length - 1 && (
                <div className="hidden sm:block absolute top-1/2 -right-4 z-10 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/30">
                  <ArrowRight className="w-4 h-4 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Stats grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {beforeAfter.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-white/5 border border-white/10 rounded-2xl p-6 text-center"
            >
              <div className="text-3xl sm:text-4xl font-bold font-display bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
                {item.stat}
              </div>
              <p className="mt-2 text-sm text-white/60 leading-snug">{item.label}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mt-14"
        >
          <Link
            href="/products"
            className="group inline-flex items-center gap-2 bg-gradient-brand text-white px-8 py-4 rounded-full text-lg font-bold hover:shadow-xl hover:shadow-emerald-500/30 transition-all hover:-translate-y-1"
          >
            Start Your Transformation
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <p className="mt-4 text-sm text-white/40 flex items-center justify-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5" />
            30-day money-back guarantee. No risk.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
