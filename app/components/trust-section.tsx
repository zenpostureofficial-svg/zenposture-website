'use client';

import { useRef, useState, useEffect } from 'react';
import { motion, useInView } from 'framer-motion';
import { Users, Award, Star, ShieldCheck } from 'lucide-react';

function AnimatedCounter({ end, suffix = '', prefix = '' }: { end: number; suffix?: string; prefix?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const duration = 2000;
    const steps = 60;
    const increment = end / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [isInView, end]);

  return (
    <div ref={ref} className="text-4xl sm:text-5xl font-bold font-display text-gradient">
      {prefix}{count.toLocaleString('en-IN')}{suffix}
    </div>
  );
}

const stats = [
  { icon: Users, end: 10000, suffix: '+', label: 'Happy Customers' },
  { icon: Award, end: 98, suffix: '%', label: 'Satisfaction Rate' },
  { icon: Star, end: 4, suffix: '.8', label: 'Average Rating' },
  { icon: ShieldCheck, end: 30, label: 'Day Guarantee', suffix: '-Day' },
];

export default function TrustSection() {
  return (
    <section className="py-16 bg-white border-y border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-emerald-50 flex items-center justify-center">
                <stat.icon className="w-7 h-7 text-emerald-600" />
              </div>
              <AnimatedCounter end={stat.end} suffix={stat.suffix} />
              <p className="mt-2 text-sm font-medium text-gray-500">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
