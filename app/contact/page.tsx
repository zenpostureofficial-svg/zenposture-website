import dynamic from 'next/dynamic';

const ContactClient = dynamic(() => import('./contact-client'), { ssr: false });

export default function ContactPage() {
  return <ContactClient />;
}
