'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { CheckCircle, Zap, Heart, ShieldCheck, Leaf, Award } from 'lucide-react';

const benefits = [
  {
    icon: ShieldCheck,
    title: 'Clinically-Designed',
    description: 'Each product is designed with input from physiotherapists for effective, safe daily use.',
  },
  {
    icon: Leaf,
    title: 'Breathable Materials',
    description: 'Premium fabrics that work in Indian weather. Lightweight, soft & comfortable all day.',
  },
  {
    icon: Zap,
    title: 'Instant Relief',
    description: 'Feel the difference from Day 1. Our products provide immediate posture support & pain relief.',
  },
  {
    icon: Heart,
    title: 'For Every Body',
    description: 'Adjustable designs that fit all body types. From office workers to new moms to gym enthusiasts.',
  },
  {
    icon: Award,
    title: 'Premium Quality',
    description: 'Built to last with reinforced stitching and medical-grade materials that maintain shape.',
  },
  {
    icon: CheckCircle,
    title: '30-Day Guarantee',
    description: 'Not satisfied? Full refund within 30 days. No questions asked. Your comfort is guaranteed.',
  },
];

export default function WhySection() {
  return (
    <section className="py-20 lg:py-28 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Image */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="relative aspect-[4/3] rounded-3xl overflow-hidden shadow-2xl">
              <Image
                src="/images/posture-comparison.jpg"
                alt="Before and after posture comparison showing the benefits of ZenPosture products"
                fill
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
            </div>
            {/* Floating stat card */}
            <div className="absolute -bottom-6 -right-6 bg-white rounded-2xl shadow-xl p-5 border border-gray-100">
              <p className="text-3xl font-bold text-gradient">93%</p>
              <p className="text-sm text-gray-600 font-medium">Report reduced<br />back pain in 2 weeks</p>
            </div>
          </motion.div>

          {/* Right: Benefits */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold font-display text-gray-900">
                Why <span className="text-gradient">10,000+ Indians</span>
                <br />Choose ZenPosture
              </h2>
              <p className="mt-4 text-gray-600 text-lg">
                We don&apos;t just sell products. We help you build habits for a healthier, pain-free life.
              </p>
            </motion.div>

            <div className="mt-10 grid sm:grid-cols-2 gap-6">
              {benefits.map((b, i) => (
                <motion.div
                  key={b.title}
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className="flex gap-4"
                >
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center flex-shrink-0">
                    <b.icon className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{b.title}</h3>
                    <p className="text-sm text-gray-500 mt-0.5 leading-relaxed">{b.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
