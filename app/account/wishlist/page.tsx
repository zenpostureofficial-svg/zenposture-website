import dynamic from 'next/dynamic';

const WishlistClient = dynamic(() => import('./wishlist-client'), { ssr: false });

export default function WishlistPage() {
  return <WishlistClient />;
}
