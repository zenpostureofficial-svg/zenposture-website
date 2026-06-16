import dynamic from 'next/dynamic';

const AccountClient = dynamic(() => import('./account-client'), { ssr: false });

export default function AccountPage() {
  return <AccountClient />;
}
