'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Filter, SlidersHorizontal } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import AnnouncementBar from '../components/announcement-bar';
import Header from '../components/header';
import Footer from '../components/footer';
import ProductCard from '../components/product-card';
import { PRODUCTS, ProductData } from '@/lib/products-data';

const categories = [
  { label: 'All Products', value: 'all' },
  { label: 'Posture Correction', value: 'posture' },
  { label: 'Recovery & Support', value: 'recovery' },
  { label: 'Fitness', value: 'fitness' },
];

const sortOptions = [
  { label: 'Most Popular', value: 'popular' },
  { label: 'Price: Low to High', value: 'price-asc' },
  { label: 'Price: High to Low', value: 'price-desc' },
  { label: 'Biggest Discount', value: 'discount' },
];

export default function ProductsClient() {
  const searchParams = useSearchParams();
  const categoryParam = searchParams?.get('category') || 'all';
  const [category, setCategory] = useState(categoryParam);
  const [sort, setSort] = useState('popular');

  useEffect(() => {
    if (categoryParam) setCategory(categoryParam);
  }, [categoryParam]);

  const filtered = PRODUCTS.filter((p: ProductData) => {
    if (category === 'all') return true;
    if (category === 'posture') return p.tags.some(t => ['posture', 'back support', 'figure 8', 'upper back'].includes(t));
    if (category === 'recovery') return p.tags.some(t => ['recovery', 'postpartum', 'maternity', 'core support', 'abdominal', 'compression', 'elastic'].includes(t));
    if (category === 'fitness') return p.tags.some(t => ['fitness', 'workout', 'gym'].includes(t));
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sort === 'price-asc') return a.price - b.price;
    if (sort === 'price-desc') return b.price - a.price;
    if (sort === 'discount') return b.discount - a.discount;
    return 0; // popular = original order
  });

  return (
    <div className="min-h-screen bg-white">
      <AnnouncementBar />
      <Header />

      {/* Page Header */}
      <section className="bg-gradient-to-b from-gray-50 to-white py-12 lg:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 text-center">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-gray-900">
            Our <span className="text-gradient">Products</span>
          </h1>
          <p className="mt-4 text-gray-600 text-lg max-w-2xl mx-auto">
            Premium posture correction and body support products. Free shipping & COD available on all orders.
          </p>
        </div>
      </section>

      {/* Filters & Products */}
      <section className="py-10 lg:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          {/* Filter Bar */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10">
            {/* Categories */}
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <button
                  key={cat.value}
                  onClick={() => setCategory(cat.value)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    category === cat.value
                      ? 'bg-gradient-brand text-white shadow-md'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="w-4 h-4 text-gray-400" />
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Products Grid */}
          {sorted.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
              {sorted.map((product, i) => (
                <ProductCard key={product.id} product={product} index={i} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">No products found in this category.</p>
            </div>
          )}
        </div>
      </section>

      <Footer />
    </div>
  );
}
