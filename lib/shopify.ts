export interface ShopifyProduct {
  id: number;
  title: string;
  handle: string;
  body_html: string;
  published_at: string;
  product_type: string;
  vendor: string;
  tags: string[];
  variants: ShopifyVariant[];
  images: ShopifyImage[];
  options: ShopifyOption[];
}

export interface ShopifyVariant {
  id: number;
  title: string;
  price: string;
  compare_at_price: string | null;
  available: boolean;
  option1: string | null;
  option2: string | null;
  option3: string | null;
}

export interface ShopifyImage {
  id: number;
  src: string;
  width: number;
  height: number;
  position: number;
}

export interface ShopifyOption {
  name: string;
  position: number;
  values: string[];
}

const STORE_URL = 'zen-posture-2.myshopify.com';

export async function fetchAllProducts(): Promise<ShopifyProduct[]> {
  try {
    const res = await fetch(`https://${STORE_URL}/products.json?limit=50`, {
      next: { revalidate: 300 },
    });
    if (!res?.ok) return [];
    const data = await res.json();
    return data?.products ?? [];
  } catch (error) {
    console.error('Failed to fetch Shopify products:', error);
    return [];
  }
}

export async function fetchProductByHandle(handle: string): Promise<ShopifyProduct | null> {
  try {
    const res = await fetch(`https://${STORE_URL}/products/${handle}.json`, {
      next: { revalidate: 300 },
    });
    if (!res?.ok) return null;
    const data = await res.json();
    return data?.product ?? null;
  } catch (error) {
    console.error('Failed to fetch product:', error);
    return null;
  }
}

export function getDiscountPercentage(price: string, compareAtPrice: string | null): number {
  if (!compareAtPrice) return 0;
  const p = parseFloat(price);
  const cp = parseFloat(compareAtPrice);
  if (cp <= 0 || p <= 0) return 0;
  return Math.round(((cp - p) / cp) * 100);
}

export function formatPrice(price: string | number): string {
  const num = typeof price === 'string' ? parseFloat(price) : price;
  return `₹${Math.round(num ?? 0)}`;
}

export function getCheckoutUrl(variantId: number): string {
  return `https://${STORE_URL}/cart/${variantId}:1`;
}

export function getBuyNowUrl(variantId: number): string {
  return `https://${STORE_URL}/cart/${variantId}:1`;
}
