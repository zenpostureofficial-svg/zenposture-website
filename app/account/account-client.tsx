'use client';

import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { User, Heart, Shield, ArrowRight, LogOut } from 'lucide-react';
import Link from 'next/link';
import Header from '../components/header';
import Footer from '../components/footer';

export default function AccountClient() {
  const { data: session, status } = useSession() || {};
  const router = useRouter();

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!session) { router.replace('/auth/login'); return null; }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <section className="max-w-3xl mx-auto px-4 sm:px-6 py-16">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold font-display text-gray-900">My Account</h1>
          <p className="text-gray-500 mt-2">Welcome back, {session.user?.name || 'there'}!</p>

          <div className="mt-8 space-y-4">
            {/* Profile card */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center">
                  <User className="w-7 h-7 text-emerald-600" />
                </div>
                <div>
                  <p className="font-bold text-gray-900">{session.user?.name}</p>
                  <p className="text-sm text-gray-500">{session.user?.email}</p>
                </div>
              </div>
            </div>

            {/* Links */}
            <Link href="/account/wishlist" className="flex items-center justify-between bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow group">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
                  <Heart className="w-5 h-5 text-red-500" />
                </div>
                <span className="font-semibold text-gray-900">My Wishlist</span>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-emerald-600 group-hover:translate-x-1 transition-all" />
            </Link>

            <div className="flex items-center justify-between bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-blue-500" />
                </div>
                <span className="font-semibold text-gray-900">Account Secured</span>
              </div>
              <span className="text-xs bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full font-medium">Active</span>
            </div>

            <button
              onClick={() => signOut({ callbackUrl: '/' })}
              className="flex items-center gap-3 w-full bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md hover:border-red-100 transition-all text-left group"
            >
              <div className="w-10 h-10 rounded-xl bg-gray-50 group-hover:bg-red-50 flex items-center justify-center transition-colors">
                <LogOut className="w-5 h-5 text-gray-400 group-hover:text-red-500 transition-colors" />
              </div>
              <span className="font-semibold text-gray-900 group-hover:text-red-600 transition-colors">Sign Out</span>
            </button>
          </div>
        </motion.div>
      </section>
      <Footer />
    </div>
  );
}
