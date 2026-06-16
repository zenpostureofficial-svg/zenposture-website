'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight } from 'lucide-react';

const categories = [
  {
    title: 'Posture Correctors',
    description: 'Back & shoulder support for daily comfort',
    image: '/images/posture-at-work.jpg',
    href: '/products?category=posture',
    color: 'from-emerald-500 to-teal-600',
  },
  {
    title: 'Support Belts',
    description: 'Abdominal & compression support',
    image: '/images/postpartum-care.jpg',
    href: '/products?category=recovery',
    color: 'from-rose-400 to-pink-600',
  },
  {
    title: 'Fitness & Wellness',
    description: 'Workout support & performance gear',
    image: '/images/fitness-belt.jpg',
    href: '/products?category=fitness',
    color: 'from-amber-400 to-orange-500',
  },
];

export default function CategorySection() {
  return (
    <section className="py-20 lg:py-28 bg-gray-50/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-gray-900">
            Shop by <span className="text-gradient">Category</span>
          </h2>
          <p className="mt-4 text-gray-600 text-lg">Find the right support for your needs</p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {categories.map((cat, i) => (
            <motion.div
              key={cat.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Link
                href={cat.href}
                className="group block relative rounded-2xl overflow-hidden aspect-[4/3] shadow-lg hover:shadow-xl transition-all"
              >
                <Image
                  src={cat.image}
                  alt={cat.title}
                  fill
                  className="object-cover group-hover:scale-110 transition-transform duration-700"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${cat.color} opacity-60 group-hover:opacity-70 transition-opacity`} />
                <div className="absolute inset-0 flex flex-col justify-end p-6 text-white">
                  <h3 className="text-2xl font-bold font-display">{cat.title}</h3>
                  <p className="text-white/80 text-sm mt-1">{cat.description}</p>
                  <div className="flex items-center gap-1 mt-3 text-sm font-semibold">
                    Shop Now <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
