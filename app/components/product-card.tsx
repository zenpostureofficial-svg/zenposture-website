'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { ShoppingBag, Star, Eye } from 'lucide-react';
import { ProductData, getCheckoutUrl } from '@/lib/products-data';

export default function ProductCard({ product, index = 0 }: { product: ProductData; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      className="group bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-500 hover:-translate-y-1"
    >
      {/* Image */}
      <Link href={`/products/${product.handle}`} className="block relative">
        <div className="relative aspect-square bg-gray-50 overflow-hidden">
          <Image
            src={product.images[0]}
            alt={product.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-700"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />

          {/* Badges */}
          <div className="absolute top-3 left-3 flex flex-col gap-1.5">
            <span className="bg-red-500 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm">
              {product.discount}% OFF
            </span>
            {product.badge && (
              <span className="bg-gradient-brand text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm">
                {product.badge}
              </span>
            )}
          </div>

          {/* Quick view overlay */}
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
            <span className="opacity-0 group-hover:opacity-100 transition-opacity bg-white text-gray-900 px-4 py-2 rounded-full text-sm font-medium shadow-lg flex items-center gap-2">
              <Eye className="w-4 h-4" />
              Quick View
            </span>
          </div>
        </div>
      </Link>

      {/* Content */}
      <div className="p-4">
        <Link href={`/products/${product.handle}`}>
          <h3 className="font-semibold text-gray-900 group-hover:text-emerald-700 transition-colors line-clamp-2 leading-snug">
            {product.shortTitle || product.title}
          </h3>
        </Link>

        <p className="text-sm text-gray-500 mt-1 line-clamp-1">{product.shortDescription}</p>

        {/* Rating */}
        <div className="flex items-center gap-1 mt-2">
          {[...Array(5)].map((_, i) => (
            <Star key={i} className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
          ))}
          <span className="text-xs text-gray-500 ml-1">(4.8)</span>
        </div>

        {/* Price */}
        <div className="flex items-baseline gap-2 mt-3">
          <span className="text-xl font-bold text-gray-900">₹{product.price}</span>
          <span className="text-sm text-gray-400 line-through">₹{product.compareAtPrice}</span>
          <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
            Save ₹{product.compareAtPrice - product.price}
          </span>
        </div>

        {/* CTA */}
        <a
          href={getCheckoutUrl(product.variantId)}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 w-full flex items-center justify-center gap-2 bg-gray-900 hover:bg-emerald-600 text-white py-3 rounded-xl font-semibold text-sm transition-colors"
        >
          <ShoppingBag className="w-4 h-4" />
          Add to Cart
        </a>
      </div>
    </motion.div>
  );
}
