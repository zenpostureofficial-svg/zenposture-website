'use client';

import { motion } from 'framer-motion';
import Image from 'next/image';
import { Star, Quote, CheckCircle } from 'lucide-react';

const testimonials = [
  {
    name: 'Priya Sharma',
    location: 'Mumbai',
    image: '/images/happy-customer-1.jpg',
    rating: 5,
    comment: 'I work 10+ hours at my desk daily. After using the posture corrector for just one week, my back pain reduced significantly. Best investment for my health!',
    product: 'Posture Corrector',
    verified: true,
  },
  {
    name: 'Rahul Verma',
    location: 'Bangalore',
    image: '/images/happy-customer-2.jpg',
    rating: 5,
    comment: 'The quality is amazing for this price point. I was skeptical at first, but the cross back corrector is super comfortable. Wearing it daily under my shirt.',
    product: 'Cross Back Corrector',
    verified: true,
  },
  {
    name: 'Ananya Patel',
    location: 'Delhi',
    image: '/images/happy-customer-3.jpg',
    rating: 5,
    comment: 'Bought the postpartum belt after my delivery. It gave me so much support during recovery. The material is breathable even in summer. Highly recommend to all new moms!',
    product: 'Postpartum Recovery Belt',
    verified: true,
  },
];

export default function TestimonialsSection() {
  return (
    <section className="py-20 lg:py-28 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-gray-900">
            Real People. <span className="text-gradient">Real Results.</span>
          </h2>
          <p className="mt-4 text-gray-600 text-lg">See how ZenPosture is changing lives across India</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-lg transition-shadow"
            >
              {/* Quote icon */}
              <Quote className="w-8 h-8 text-emerald-200 mb-4" />

              {/* Stars */}
              <div className="flex gap-0.5 mb-3">
                {[...Array(t.rating)].map((_, j) => (
                  <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>

              {/* Comment */}
              <p className="text-gray-700 leading-relaxed">&ldquo;{t.comment}&rdquo;</p>

              {/* Author */}
              <div className="flex items-center gap-3 mt-6 pt-4 border-t border-gray-50">
                <div className="relative w-12 h-12 rounded-full overflow-hidden bg-gray-100">
                  <Image src={t.image} alt={t.name} fill className="object-cover" sizes="48px" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-1.5">
                    <p className="font-semibold text-gray-900 text-sm">{t.name}</p>
                    {t.verified && <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />}
                  </div>
                  <p className="text-xs text-gray-500">{t.location} • Bought {t.product}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Social proof bar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 text-center"
        >
          <div className="inline-flex items-center gap-3 bg-emerald-50 border border-emerald-100 px-6 py-3 rounded-full">
            <div className="flex -space-x-2">
              {testimonials.map((t, i) => (
                <div key={i} className="relative w-8 h-8 rounded-full border-2 border-white overflow-hidden">
                  <Image src={t.image} alt={t.name} fill className="object-cover" sizes="32px" />
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-700">
              <span className="font-bold text-emerald-700">10,000+</span> happy customers across India
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
