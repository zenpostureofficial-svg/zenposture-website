'use client';

import { Truck, Shield, CreditCard, RotateCcw, Award } from 'lucide-react';
import { motion } from 'framer-motion';

const proofs = [
  { icon: Truck, label: 'Free Shipping', sub: 'Pan India' },
  { icon: CreditCard, label: 'COD Available', sub: 'Pay at Doorstep' },
  { icon: Shield, label: 'Secure Checkout', sub: 'Razorpay & UPI' },
  { icon: RotateCcw, label: '30-Day Returns', sub: 'Comfort Guarantee' },
  { icon: Award, label: 'Premium Quality', sub: 'Trusted by 10K+' },
];

export default function SocialProofBar() {
  return (
    <section className="border-y border-gray-100 bg-gray-50/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 divide-x divide-gray-100">
          {proofs.map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="flex items-center gap-3 py-5 px-4 justify-center"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center flex-shrink-0">
                <item.icon className="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900">{item.label}</p>
                <p className="text-xs text-gray-500">{item.sub}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
