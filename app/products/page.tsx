import dynamic from 'next/dynamic';

const ProductsClient = dynamic(() => import('./products-client'), { ssr: false });

export default function ProductsPage() {
  return <ProductsClient />;
}
