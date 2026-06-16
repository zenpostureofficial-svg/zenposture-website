'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import ProductCard from './product-card';
import { PRODUCTS } from '@/lib/products-data';

export default function AllProductsSection() {
  // Show remaining products (after featured 3)
  const remaining = PRODUCTS.slice(3);

  return (
    <section className="py-20 lg:py-28 bg-gray-50/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="text-3xl sm:text-4xl font-bold font-display text-gray-900">
            More <span className="text-gradient">Great Products</span>
          </h2>
          <p className="mt-4 text-gray-600 text-lg">
            Complete your posture and wellness journey
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {remaining.map((product, i) => (
            <ProductCard key={product.id} product={product} index={i} />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <Link
            href="/products"
            className="group inline-flex items-center gap-2 bg-gray-900 hover:bg-emerald-600 text-white px-8 py-3.5 rounded-full font-semibold transition-colors"
          >
            View All Products
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>
      </div>
    </section>
  );
}
