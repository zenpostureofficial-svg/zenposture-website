'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import { Menu, X, ShoppingBag, User, Heart, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: session } = useSession() || {};

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navLinks = [
    { label: 'Home', href: '/' },
    { label: 'Shop All', href: '/products' },
    { label: 'About', href: '/about' },
    { label: 'Contact', href: '/contact' },
  ];

  return (
    <header
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-md shadow-md border-b border-gray-100'
          : 'bg-white'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16 lg:h-18">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 bg-gradient-brand rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow">
              <span className="text-white font-bold text-lg font-display">Z</span>
            </div>
            <span className="text-xl font-bold font-display text-gray-900 tracking-tight">
              Zen<span className="text-gradient">Posture</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden lg:flex items-center gap-8">
            {navLinks.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-gray-600 hover:text-emerald-600 transition-colors relative group"
              >
                {link.label}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-emerald-500 transition-all group-hover:w-full" />
              </Link>
            ))}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden lg:flex items-center gap-3">
            {session ? (
              <div className="flex items-center gap-3">
                <Link href="/account/wishlist" className="p-2 text-gray-500 hover:text-emerald-600 transition-colors">
                  <Heart className="w-5 h-5" />
                </Link>
                <Link href="/account" className="p-2 text-gray-500 hover:text-emerald-600 transition-colors">
                  <User className="w-5 h-5" />
                </Link>
                <button onClick={() => signOut()} className="text-sm text-gray-500 hover:text-gray-700">
                  Sign Out
                </button>
              </div>
            ) : (
              <Link href="/auth/login" className="text-sm font-medium text-gray-600 hover:text-emerald-600 transition-colors">
                Login
              </Link>
            )}
            <Link
              href="/products"
              className="bg-gradient-brand text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-emerald-500/25 transition-all hover:-translate-y-0.5"
            >
              Shop Now
            </Link>
          </div>

          {/* Mobile Toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-2 text-gray-600"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="lg:hidden overflow-hidden bg-white border-t"
          >
            <div className="px-4 py-4 space-y-1">
              {navLinks.map(link => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="block py-3 px-3 text-gray-700 hover:bg-emerald-50 hover:text-emerald-700 rounded-lg font-medium transition-colors"
                >
                  {link.label}
                </Link>
              ))}
              <div className="pt-3 border-t mt-3">
                {session ? (
                  <>
                    <Link href="/account" onClick={() => setMobileOpen(false)} className="block py-3 px-3 text-gray-700 hover:bg-emerald-50 rounded-lg">
                      My Account
                    </Link>
                    <Link href="/account/wishlist" onClick={() => setMobileOpen(false)} className="block py-3 px-3 text-gray-700 hover:bg-emerald-50 rounded-lg">
                      Wishlist
                    </Link>
                    <button onClick={() => { signOut(); setMobileOpen(false); }} className="block w-full text-left py-3 px-3 text-gray-500">
                      Sign Out
                    </button>
                  </>
                ) : (
                  <Link href="/auth/login" onClick={() => setMobileOpen(false)} className="block py-3 px-3 text-gray-700 hover:bg-emerald-50 rounded-lg">
                    Login / Sign Up
                  </Link>
                )}
                <Link
                  href="/products"
                  onClick={() => setMobileOpen(false)}
                  className="block mt-3 text-center bg-gradient-brand text-white py-3 rounded-full font-semibold"
                >
                  Shop Now
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
