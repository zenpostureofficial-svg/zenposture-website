'use client';

import Link from 'next/link';
import { Mail, MapPin, Clock, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-16">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 bg-gradient-brand rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg font-display">Z</span>
              </div>
              <span className="text-xl font-bold font-display">ZenPosture</span>
            </div>
            <p className="text-gray-400 max-w-sm leading-relaxed">
              Supporting better posture, comfort, and confidence for everyday life.
              India&apos;s trusted brand for posture correction and body support.
            </p>
            <div className="mt-6 inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full text-sm font-medium border border-emerald-500/20">
              🇮🇳 Made with <Heart className="w-3.5 h-3.5 fill-red-400 text-red-400" /> in India
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Quick Links</h3>
            <div className="space-y-3">
              {[
                { label: 'Shop All Products', href: '/products' },
                { label: 'About Us', href: '/about' },
                { label: 'Contact', href: '/contact' },
              ].map(link => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="block text-gray-400 hover:text-emerald-400 transition-colors text-sm"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-white mb-4">Contact Us</h3>
            <div className="space-y-3 text-sm text-gray-400">
              <a href="mailto:support@zenposture.in" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
                <Mail className="w-4 h-4" />
                support@zenposture.in
              </a>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Mon-Sat, 10 AM - 6 PM
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <p className="text-center text-sm text-gray-500">
            &copy; 2024 ZenPosture. All Rights Reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
