'use client';

import { useState } from 'react';
import { X, Truck, Shield, IndianRupee } from 'lucide-react';

export default function AnnouncementBar() {
  const [visible, setVisible] = useState(true);
  if (!visible) return null;

  return (
    <div className="bg-gradient-brand text-white text-sm relative overflow-hidden">
      <div className="absolute inset-0 animate-shimmer pointer-events-none" />
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-6 py-2.5 px-4 relative">
        <div className="hidden sm:flex items-center gap-1.5">
          <Truck className="w-3.5 h-3.5" />
          <span className="font-medium">Free Shipping</span>
        </div>
        <span className="hidden sm:block text-white/40">|</span>
        <div className="flex items-center gap-1.5 font-semibold">
          <span>🔥</span>
          <span>Launch Offer: Up to 63% OFF — Limited Stock</span>
        </div>
        <span className="hidden sm:block text-white/40">|</span>
        <div className="hidden sm:flex items-center gap-1.5">
          <IndianRupee className="w-3.5 h-3.5" />
          <span className="font-medium">COD Available</span>
        </div>
        <button
          onClick={() => setVisible(false)}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-white/20 rounded-full transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
