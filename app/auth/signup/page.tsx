import dynamic from 'next/dynamic';

const SignupClient = dynamic(() => import('./signup-client'), { ssr: false });

export default function SignupPage() {
  return <SignupClient />;
}
