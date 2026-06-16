import dynamic from 'next/dynamic';

const AboutClient = dynamic(() => import('./about-client'), { ssr: false });

export default function AboutPage() {
  return <AboutClient />;
}
