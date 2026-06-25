'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { ArrowRight, Star, Shield, Truck, BadgeCheck, Users } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-white to-emerald-50/30">
      {/* Subtle background decoration */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-100/30 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-teal-100/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/4" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-8 pb-16 lg:pt-16 lg:pb-24 relative">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Copy */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: 'easeOut' }}
            className="text-center lg:text-left"
          >
            {/* Trust badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-2 rounded-full text-sm font-medium mb-6"
            >
              <span className="flex items-center gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                ))}
              </span>
              <span>Rated 4.8/5 by 10,000+ Customers</span>
            </motion.div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-display leading-tight text-gray-900">
              Fix Your Posture.
              <br />
              <span className="text-gradient">Transform Your Life.</span>
            </h1>

            <p className="mt-6 text-lg text-gray-600 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              India&apos;s most trusted posture correction brand. Clinically-designed support for desk workers, students, new moms &amp; fitness enthusiasts.
            </p>

            {/* Price highlight */}
            <div className="mt-8 flex flex-col sm:flex-row items-center lg:items-start gap-4">
              <Link
                href="/products"
                className="group bg-gradient-brand text-white px-8 py-4 rounded-full text-lg font-bold hover:shadow-xl hover:shadow-emerald-500/30 transition-all hover:-translate-y-1 flex items-center gap-2"
              >
                Shop Best Sellers
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <div className="text-center lg:text-left">
                <p className="text-sm text-gray-500">Starting at just</p>
                <p className="text-2xl font-bold text-gray-900">
                  ₹499 <span className="text-base text-gray-400 line-through font-normal">₹999</span>
                  <span className="ml-2 text-sm font-semibold text-red-500 bg-red-50 px-2 py-0.5 rounded-full">50% OFF</span>
                </p>
              </div>
            </div>

            {/* Trust signals row */}
            <div className="mt-10 flex flex-wrap justify-center lg:justify-start gap-6">
              {[
                { icon: Truck, label: 'Free Shipping' },
                { icon: Shield, label: '30-Day Guarantee' },
                { icon: BadgeCheck, label: 'COD Available' },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-2 text-gray-600">
                  <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center">
                    <item.icon className="w-4 h-4 text-emerald-600" />
                  </div>
                  <span className="text-sm font-medium">{item.label}</span>
                </div>
              ))}
            </div>

            {/* As seen on */}
            <div className="mt-10 pt-8 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4 text-center lg:text-left">As Featured In</p>
              <div className="flex flex-wrap justify-center lg:justify-start items-center gap-6 opacity-40 grayscale">
                {['YourStory', 'Inc42', 'ET Retail', 'Femina', 'Health+'].map((name) => (
                  <span key={name} className="text-sm font-bold text-gray-600 font-display tracking-tight">{name}</span>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Right: Hero Image */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="relative"
          >
            <div className="relative aspect-[4/5] sm:aspect-[3/4] lg:aspect-[4/5] rounded-3xl overflow-hidden shadow-2xl">
              <Image
                src="/images/hero-lifestyle.jpg"
                alt="Professional woman with perfect posture at her desk, showcasing ZenPosture benefits"
                fill
                className="object-cover"
                priority
                sizes="(max-width: 768px) 100vw, 50vw"
              />
              {/* Overlay gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />
            </div>

            {/* Floating badge 1 */}
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8, type: 'spring' }}
              className="absolute -left-4 top-1/4 bg-white rounded-2xl shadow-xl p-4 border border-gray-100"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                  <Star className="w-5 h-5 fill-amber-500 text-amber-500" />
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">4.8/5 Rating</p>
                  <p className="text-xs text-gray-500">10,000+ Reviews</p>
                </div>
              </div>
            </motion.div>

            {/* Floating badge 2 */}
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1, type: 'spring' }}
              className="absolute -right-4 bottom-1/4 bg-white rounded-2xl shadow-xl p-4 border border-gray-100"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center">
                  <Users className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-900">10,000+</p>
                  <p className="text-xs text-gray-500">Happy Customers</p>
                </div>
              </div>
            </motion.div>

            {/* Up to 63% OFF floating badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2 }}
              className="absolute -bottom-4 left-1/2 -translate-x-1/2 bg-red-500 text-white px-6 py-2.5 rounded-full font-bold text-sm shadow-lg shadow-red-500/30 animate-pulse-soft"
            >
              🔥 Up to 63% OFF — Limited Time!
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
