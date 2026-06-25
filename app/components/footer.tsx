'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Mail, Clock, Heart, Instagram, Youtube, Facebook, ArrowRight, CheckCircle } from 'lucide-react';

const socialLinks = [
  { icon: Instagram, label: 'Instagram', href: 'https://instagram.com/zenposture.in' },
  { icon: Facebook, label: 'Facebook', href: 'https://facebook.com/zenposturein' },
  { icon: Youtube, label: 'YouTube', href: 'https://youtube.com/@zenposture' },
];

const footerLinks = {
  Shop: [
    { label: 'Posture Correctors', href: '/products' },
    { label: 'Back Support Belts', href: '/products' },
    { label: 'Postpartum Belts', href: '/products' },
    { label: 'Fitness Belts', href: '/products' },
    { label: 'View All Products', href: '/products' },
  ],
  Support: [
    { label: 'About Us', href: '/about' },
    { label: 'Contact Us', href: '/contact' },
    { label: 'Track Order', href: '/contact' },
    { label: 'FAQ', href: '/#faq' },
  ],
  Legal: [
    { label: 'Privacy Policy', href: '/contact' },
    { label: 'Refund Policy', href: '/contact' },
    { label: 'Terms of Service', href: '/contact' },
    { label: 'Shipping Policy', href: '/contact' },
  ],
};

export default function Footer() {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      setSubscribed(true);
      setEmail('');
    }
  };

  return (
    <footer className="bg-gray-950 text-white">
      {/* Newsletter strip */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h3 className="text-xl font-bold font-display text-white">Get 10% Off Your First Order</h3>
              <p className="text-gray-400 text-sm mt-1">Join 10,000+ subscribers. Health tips & exclusive deals.</p>
            </div>
            {subscribed ? (
              <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                <CheckCircle className="w-5 h-5" />
                <span>Welcome! Check your inbox for your discount.</span>
              </div>
            ) : (
              <form onSubmit={handleSubscribe} className="flex gap-2 w-full md:w-auto">
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="flex-1 md:w-64 bg-gray-800 border border-gray-700 text-white placeholder-gray-500 rounded-full px-5 py-2.5 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
                  required
                />
                <button
                  type="submit"
                  className="flex items-center gap-1.5 bg-gradient-brand text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-emerald-500/25 transition-all"
                >
                  Subscribe
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

      {/* Main footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-14">
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 bg-gradient-brand rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg font-display">Z</span>
              </div>
              <span className="text-xl font-bold font-display">ZenPosture</span>
            </div>
            <p className="text-gray-400 max-w-xs leading-relaxed text-sm">
              India&apos;s trusted brand for posture correction and body support. Clinically-designed products for a healthier, pain-free life.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full text-sm font-medium border border-emerald-500/20">
              🇮🇳 Made with <Heart className="w-3.5 h-3.5 fill-red-400 text-red-400" /> in India
            </div>
            {/* Social */}
            <div className="mt-6 flex items-center gap-3">
              {socialLinks.map(s => (
                <a
                  key={s.label}
                  href={s.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={s.label}
                  className="w-9 h-9 rounded-full bg-gray-800 hover:bg-emerald-600 flex items-center justify-center transition-colors"
                >
                  <s.icon className="w-4 h-4" />
                </a>
              ))}
            </div>
            {/* Contact */}
            <div className="mt-6 space-y-2 text-sm text-gray-400">
              <a href="mailto:support@zenposture.in" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
                <Mail className="w-4 h-4 flex-shrink-0" />
                support@zenposture.in
              </a>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 flex-shrink-0" />
                Mon–Sat, 10 AM – 6 PM IST
              </div>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([heading, links]) => (
            <div key={heading}>
              <h3 className="font-semibold text-white mb-4 text-sm uppercase tracking-widest">{heading}</h3>
              <div className="space-y-3">
                {links.map(link => (
                  <Link
                    key={link.label}
                    href={link.href}
                    className="block text-gray-400 hover:text-emerald-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} ZenPosture. All Rights Reserved.
          </p>
          <div className="flex items-center gap-2 text-gray-600 text-xs">
            <span>Secure payments via</span>
            {['UPI', 'Razorpay', 'COD', 'Net Banking'].map(method => (
              <span key={method} className="bg-gray-800 px-2 py-1 rounded text-gray-400 font-medium">
                {method}
              </span>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}

