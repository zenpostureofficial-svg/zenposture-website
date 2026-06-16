import dynamic from 'next/dynamic';

const HomeClient = dynamic(() => import('./components/home-client'), { ssr: false });

export default function HomePage() {
  return <HomeClient />;
}
