'use client';

import { useState, useEffect } from 'react';
import { X, Truck, IndianRupee, Clock } from 'lucide-react';

function useCountdown(targetHours = 6) {
  const [timeLeft, setTimeLeft] = useState({ h: targetHours, m: 0, s: 0 });

  useEffect(() => {
    const end = Date.now() + targetHours * 3600 * 1000;
    const tick = () => {
      const diff = Math.max(0, end - Date.now());
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      setTimeLeft({ h, m, s });
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [targetHours]);

  return timeLeft;
}

export default function AnnouncementBar() {
  const [visible, setVisible] = useState(true);
  const { h, m, s } = useCountdown(6);
  if (!visible) return null;

  const pad = (n: number) => String(n).padStart(2, '0');

  return (
    <div className="bg-gradient-brand text-white text-sm relative overflow-hidden">
      <div className="absolute inset-0 animate-shimmer pointer-events-none" />
      <div className="max-w-7xl mx-auto flex items-center justify-center gap-4 sm:gap-6 py-2.5 px-8 relative">
        <div className="hidden sm:flex items-center gap-1.5">
          <Truck className="w-3.5 h-3.5" />
          <span className="font-medium">Free Shipping Pan India</span>
        </div>
        <span className="hidden sm:block text-white/40">|</span>
        <div className="flex items-center gap-2 font-semibold">
          <span>🔥</span>
          <span>Sale ends in</span>
          <span className="inline-flex items-center gap-1 bg-white/20 rounded px-2 py-0.5 font-mono font-bold tracking-wider">
            <Clock className="w-3 h-3" />
            {pad(h)}:{pad(m)}:{pad(s)}
          </span>
          <span className="hidden sm:inline">— Up to 63% OFF</span>
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
