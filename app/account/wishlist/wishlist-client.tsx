'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Heart, ChevronLeft, ShoppingBag } from 'lucide-react';
import Link from 'next/link';
import Header from '../../components/header';
import Footer from '../../components/footer';
import ProductCard from '../../components/product-card';
import { PRODUCTS, ProductData } from '@/lib/products-data';

export default function WishlistClient() {
  const { data: session, status } = useSession() || {};
  const router = useRouter();
  const [wishlistIds, setWishlistIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') { router.replace('/auth/login'); return; }
    if (status !== 'authenticated') return;
    fetch('/api/wishlist')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setWishlistIds(data.map((w: any) => w.productId));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [status, router]);

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const wishlistProducts = PRODUCTS.filter((p: ProductData) => wishlistIds.includes(String(p.id)));

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <section className="max-w-7xl mx-auto px-4 sm:px-6 py-12">
        <div className="flex items-center gap-3 mb-8">
          <Link href="/account" className="p-2 rounded-xl hover:bg-white transition-colors">
            <ChevronLeft className="w-5 h-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold font-display text-gray-900">My Wishlist</h1>
            <p className="text-sm text-gray-500">{wishlistProducts.length} saved items</p>
          </div>
        </div>

        {wishlistProducts.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {wishlistProducts.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
            <Heart className="w-16 h-16 text-gray-200 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900">Your wishlist is empty</h3>
            <p className="text-gray-500 mt-2">Start saving products you love!</p>
            <Link
              href="/products"
              className="inline-flex items-center gap-2 mt-6 bg-gradient-brand text-white px-6 py-3 rounded-full font-semibold hover:shadow-lg transition-all"
            >
              <ShoppingBag className="w-5 h-5" />
              Browse Products
            </Link>
          </motion.div>
        )}
      </section>
      <Footer />
    </div>
  );
}
