'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import Link from 'next/link';
import { Heart, Shield, Users, Award, ArrowRight } from 'lucide-react';
import Header from '../components/header';
import Footer from '../components/footer';
import AnnouncementBar from '../components/announcement-bar';

const values = [
  { icon: Heart, title: 'Care First', desc: 'Every product is designed with your comfort and health as the top priority.' },
  { icon: Shield, title: 'Quality Promise', desc: 'Premium materials and construction that you can trust for daily use.' },
  { icon: Users, title: 'Community', desc: 'We\'re building a healthier India, one posture at a time.' },
  { icon: Award, title: '30-Day Guarantee', desc: 'Not happy? Full refund within 30 days. No questions asked.' },
];

export default function AboutClient() {
  return (
    <div className="min-h-screen bg-white">
      <AnnouncementBar />
      <Header />

      {/* Hero */}
      <section className="bg-gradient-to-b from-gray-50 to-white py-16 lg:py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-gray-900">
              Our <span className="text-gradient">Story</span>
            </h1>
            <p className="mt-6 text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
              ZenPosture was born from a simple belief: everyone deserves to live and work without the burden of poor posture and back pain.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Values */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition-shadow text-center"
              >
                <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-emerald-50 flex items-center justify-center">
                  <v.icon className="w-7 h-7 text-emerald-600" />
                </div>
                <h3 className="font-bold text-gray-900">{v.title}</h3>
                <p className="text-sm text-gray-500 mt-2">{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Story */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="relative aspect-[4/3] rounded-3xl overflow-hidden shadow-xl">
                <Image
                  src="/images/posture-at-work.jpg"
                  alt="Person wearing ZenPosture product while working"
                  fill
                  className="object-cover"
                  sizes="(max-width: 1024px) 100vw, 50vw"
                />
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-bold font-display text-gray-900">
                Built for <span className="text-gradient">Indian Lifestyles</span>
              </h2>
              <div className="mt-6 space-y-4 text-gray-600 leading-relaxed">
                <p>
                  We noticed something alarming: millions of Indians — desk workers, students, new mothers, and fitness enthusiasts — were suffering from posture-related issues but had limited access to quality, affordable solutions.
                </p>
                <p>
                  That&apos;s why we created ZenPosture. Our products are designed specifically for Indian body types and weather conditions, using breathable, durable materials that work all day, every day.
                </p>
                <p>
                  Today, over 10,000 Indians trust ZenPosture for their daily comfort and health. And we&apos;re just getting started.
                </p>
              </div>
              <Link
                href="/products"
                className="group mt-8 inline-flex items-center gap-2 bg-gradient-brand text-white px-6 py-3 rounded-full font-semibold hover:shadow-lg transition-all"
              >
                Explore Products
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
