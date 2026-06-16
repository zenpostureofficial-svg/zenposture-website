'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useSession } from 'next-auth/react';
import {
  Star, Heart, ShoppingBag, Zap, Truck, Shield, BadgeCheck, ChevronLeft,
  Check, Minus, Plus, ArrowRight, RotateCcw, Award, Eye,
} from 'lucide-react';
import { toast } from 'sonner';
import AnnouncementBar from '../../components/announcement-bar';
import Header from '../../components/header';
import Footer from '../../components/footer';
import ProductCard from '../../components/product-card';
import { PRODUCTS, ProductData, getProductByHandle, getCheckoutUrl, getBuyNowUrl } from '@/lib/products-data';

export default function ProductDetailClient({ handle }: { handle: string }) {
  const product = getProductByHandle(handle);
  const { data: session } = useSession() || {};
  const [selectedImage, setSelectedImage] = useState(0);
  const [selectedVariant, setSelectedVariant] = useState(0);
  const [qty, setQty] = useState(1);
  const [wishlisted, setWishlisted] = useState(false);

  useEffect(() => {
    if (product && session) {
      fetch(`/api/wishlist?productId=${product.id}`)
        .then(r => r.json())
        .then(d => setWishlisted(d.wishlisted))
        .catch(() => {});
    }
  }, [product, session]);

  const toggleWishlist = async () => {
    if (!session) { toast.error('Please login to save items'); return; }
    if (!product) return;
    try {
      const method = wishlisted ? 'DELETE' : 'POST';
      await fetch('/api/wishlist', {
        method, headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId: String(product.id) }),
      });
      setWishlisted(!wishlisted);
      toast.success(wishlisted ? 'Removed from wishlist' : 'Added to wishlist');
    } catch { toast.error('Something went wrong'); }
  };

  if (!product) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <h1 className="text-2xl font-bold text-gray-900">Product Not Found</h1>
          <Link href="/products" className="text-emerald-600 mt-4 inline-block hover:underline">Browse All Products</Link>
        </div>
        <Footer />
      </div>
    );
  }

  const variant = product.variants[selectedVariant];
  const variantId = variant?.id || product.variantId;
  const related = PRODUCTS.filter(p => p.id !== product.id).slice(0, 3);

  return (
    <div className="min-h-screen bg-white">
      <AnnouncementBar />
      <Header />

      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
        <nav className="flex items-center gap-2 text-sm text-gray-500">
          <Link href="/" className="hover:text-emerald-600">Home</Link>
          <span>/</span>
          <Link href="/products" className="hover:text-emerald-600">Products</Link>
          <span>/</span>
          <span className="text-gray-900 font-medium truncate">{product.shortTitle}</span>
        </nav>
      </div>

      {/* Product Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        <div className="grid lg:grid-cols-2 gap-10 lg:gap-16">
          {/* Image Gallery */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-4"
          >
            {/* Main Image */}
            <div className="relative aspect-square rounded-2xl overflow-hidden bg-gray-50 shadow-lg">
              <Image
                src={product.images[selectedImage]}
                alt={product.title}
                fill
                className="object-cover"
                priority
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
              {/* Badges */}
              <div className="absolute top-4 left-4 flex flex-col gap-2">
                <span className="bg-red-500 text-white text-sm font-bold px-3 py-1.5 rounded-full shadow">
                  {product.discount}% OFF
                </span>
                {product.badge && (
                  <span className="bg-gradient-brand text-white text-sm font-bold px-3 py-1.5 rounded-full shadow">
                    {product.badge}
                  </span>
                )}
              </div>
            </div>

            {/* Thumbnails */}
            <div className="flex gap-3 overflow-x-auto scrollbar-none">
              {product.images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedImage(i)}
                  className={`relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 border-2 transition-all ${
                    selectedImage === i ? 'border-emerald-500 shadow-md' : 'border-transparent opacity-70 hover:opacity-100'
                  }`}
                >
                  <Image src={img} alt={`${product.title} view ${i + 1}`} fill className="object-cover" sizes="80px" />
                </button>
              ))}
            </div>
          </motion.div>

          {/* Product Info */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex flex-col"
          >
            {/* Category */}
            <p className="text-sm text-emerald-600 font-medium uppercase tracking-wider">{product.productType}</p>

            <h1 className="text-2xl sm:text-3xl font-bold font-display text-gray-900 mt-2">{product.title}</h1>

            {/* Rating */}
            <div className="flex items-center gap-2 mt-3">
              <div className="flex gap-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>
              <span className="text-sm text-gray-500">4.8/5 (500+ reviews)</span>
            </div>

            {/* Price */}
            <div className="mt-5 p-4 bg-emerald-50/50 rounded-xl border border-emerald-100">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold text-gray-900">₹{product.price}</span>
                <span className="text-lg text-gray-400 line-through">₹{product.compareAtPrice}</span>
                <span className="bg-red-500 text-white text-sm font-bold px-3 py-1 rounded-full">
                  Save ₹{product.compareAtPrice - product.price}
                </span>
              </div>
              <p className="text-sm text-emerald-700 font-medium mt-2">
                🔥 {product.discount}% off — Limited time launch offer
              </p>
            </div>

            {/* Description */}
            <p className="text-gray-600 mt-5 leading-relaxed">{product.shortDescription}</p>

            {/* Benefits */}
            <div className="mt-5 space-y-2">
              {product.benefits.map((b) => (
                <div key={b} className="flex items-center gap-2 text-sm text-gray-700">
                  <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                  {b}
                </div>
              ))}
            </div>

            {/* Variants */}
            {product.variants.length > 1 && (
              <div className="mt-6">
                <p className="text-sm font-semibold text-gray-700 mb-2">Color / Variant</p>
                <div className="flex gap-2">
                  {product.variants.map((v, i) => (
                    <button
                      key={v.id}
                      onClick={() => { setSelectedVariant(i); }}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all border ${
                        selectedVariant === i
                          ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                          : 'border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {v.title}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Quantity */}
            <div className="mt-6">
              <p className="text-sm font-semibold text-gray-700 mb-2">Quantity</p>
              <div className="inline-flex items-center border border-gray-200 rounded-xl overflow-hidden">
                <button onClick={() => setQty(Math.max(1, qty - 1))} className="p-3 hover:bg-gray-50 transition-colors">
                  <Minus className="w-4 h-4" />
                </button>
                <span className="px-5 font-semibold text-gray-900">{qty}</span>
                <button onClick={() => setQty(qty + 1)} className="p-3 hover:bg-gray-50 transition-colors">
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* CTAs */}
            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <a
                href={getCheckoutUrl(variantId)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 bg-gray-900 hover:bg-gray-800 text-white py-4 rounded-xl font-bold text-base transition-colors"
              >
                <ShoppingBag className="w-5 h-5" />
                Add to Cart
              </a>
              <a
                href={getBuyNowUrl(variantId)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 bg-gradient-brand hover:shadow-lg hover:shadow-emerald-500/25 text-white py-4 rounded-xl font-bold text-base transition-all"
              >
                <Zap className="w-5 h-5" />
                Buy Now
              </a>
              <button
                onClick={toggleWishlist}
                className={`p-4 rounded-xl border-2 transition-all ${
                  wishlisted
                    ? 'border-red-200 bg-red-50 text-red-500'
                    : 'border-gray-200 text-gray-400 hover:border-red-200 hover:text-red-500'
                }`}
              >
                <Heart className={`w-5 h-5 ${wishlisted ? 'fill-current' : ''}`} />
              </button>
            </div>

            {/* Trust Badges */}
            <div className="mt-8 grid grid-cols-2 gap-3">
              {[
                { icon: Truck, label: 'Free Shipping', sub: 'Pan India delivery' },
                { icon: BadgeCheck, label: 'COD Available', sub: 'Pay at doorstep' },
                { icon: RotateCcw, label: '30-Day Returns', sub: 'Easy returns' },
                { icon: Shield, label: 'Secure Payment', sub: 'UPI, Cards, Wallets' },
              ].map((t) => (
                <div key={t.label} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <t.icon className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{t.label}</p>
                    <p className="text-xs text-gray-500">{t.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Related Products */}
      {related.length > 0 && (
        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <h2 className="text-2xl sm:text-3xl font-bold font-display text-gray-900 text-center mb-10">
              You May Also Like
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
              {related.map((p, i) => (
                <ProductCard key={p.id} product={p} index={i} />
              ))}
            </div>
          </div>
        </section>
      )}

      <Footer />
    </div>
  );
}
