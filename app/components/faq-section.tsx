'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, MessageCircle } from 'lucide-react';
import Link from 'next/link';

const faqs = [
  {
    q: 'How long should I wear a posture corrector daily?',
    a: 'Start with 15-30 minutes per day and gradually increase to 2-3 hours. Consistency matters more than duration. Most customers see visible improvement within 2-3 weeks of daily use.',
  },
  {
    q: 'Can I wear it under my clothes?',
    a: 'Yes! Our posture correctors are designed to be sleek and low-profile. They fit comfortably under most clothing, including formal shirts and t-shirts.',
  },
  {
    q: 'Do you offer Cash on Delivery?',
    a: 'Absolutely! We offer COD across India. You can also pay using UPI, cards, net banking, and wallets through our secure checkout.',
  },
  {
    q: 'What is your return policy?',
    a: 'We offer a 30-day comfort guarantee. If you\'re not satisfied with your purchase, contact us within 30 days for a full refund or exchange. No questions asked.',
  },
  {
    q: 'How do I choose the right size?',
    a: 'Most of our products are adjustable and fit a wide range of body sizes. Each product page has a detailed size guide. If you\'re unsure, our support team is happy to help on WhatsApp.',
  },
  {
    q: 'How fast is shipping?',
    a: 'We offer free shipping pan India. Orders are typically delivered within 3-7 business days depending on your location. You\'ll receive tracking details via SMS and email.',
  },
];

export default function FaqSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="py-20 lg:py-28 bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-gray-900">
            Frequently Asked <span className="text-gradient">Questions</span>
          </h2>
          <p className="mt-4 text-gray-600">Everything you need to know before buying</p>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="border border-gray-100 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-5 text-left hover:bg-gray-50 transition-colors"
              >
                <span className="font-semibold text-gray-900 pr-4">{faq.q}</span>
                <ChevronDown className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform duration-200 ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              <AnimatePresence>
                {openIndex === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="px-5 pb-5 text-gray-600 leading-relaxed">{faq.a}</div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="mt-10 text-center"
        >
          <div className="bg-emerald-50 rounded-2xl p-6 border border-emerald-100">
            <p className="font-semibold text-gray-900">Still have questions? We&apos;re here to help!</p>
            <div className="flex flex-wrap justify-center gap-3 mt-4">
              <a
                href="https://wa.me/919876543210"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-green-500 text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:bg-green-600 transition-colors"
              >
                <MessageCircle className="w-4 h-4" />
                Chat on WhatsApp
              </a>
              <Link
                href="/contact"
                className="inline-flex items-center gap-2 bg-white text-gray-700 px-5 py-2.5 rounded-full text-sm font-semibold border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Send us a Message
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
