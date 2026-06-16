export const STORE_URL = 'zen-posture-2.myshopify.com';

export interface ProductData {
  id: number;
  title: string;
  shortTitle: string;
  handle: string;
  productType: string;
  price: number;
  compareAtPrice: number;
  discount: number;
  images: string[];
  benefits: string[];
  shortDescription: string;
  tags: string[];
  variantId: number;
  variants: { id: number; title: string; price: string; compareAtPrice: string | null; available: boolean }[];
  badge?: string;
}

export const PRODUCTS: ProductData[] = [
  {
    id: 10265057296666,
    title: 'Posture Corrector - Back & Shoulder Support',
    shortTitle: 'Posture Corrector',
    handle: 'posture-corrector-back-shoulder-support-brace',
    productType: 'Health & Wellness',
    price: 899,
    compareAtPrice: 1999,
    discount: 55,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.30.45AM_1.jpg?v=1780863830',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.30.45AM.jpg?v=1780863830',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.30.46AM_1.jpg?v=1780863830',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.30.46AM.jpg?v=1780863830',
    ],
    benefits: ['Natural shoulder alignment', 'Lightweight & breathable', 'Adjustable straps', 'Wear under clothing', 'Unisex design'],
    shortDescription: 'Gentle daily support for better posture. Perfect for office workers, students & WFH professionals.',
    tags: ['bestseller', 'posture', 'back support'],
    variantId: 52324664344858,
    variants: [{ id: 52324664344858, title: 'Default Title', price: '899.00', compareAtPrice: '1999.00', available: true }],
    badge: 'Bestseller',
  },
  {
    id: 10265057362202,
    title: 'Cross Back Posture Corrector - Figure 8 Support',
    shortTitle: 'Cross Back Corrector',
    handle: 'cross-back-posture-corrector-figure-8-support-brace',
    productType: 'Health & Wellness',
    price: 899,
    compareAtPrice: 1599,
    discount: 44,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.31.26AM.jpg?v=1780863498',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.31.27AM_1.jpg?v=1780863498',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.31.27AM_2.jpg?v=1780863498',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.31.27AM.jpg?v=1780863498',
    ],
    benefits: ['Figure-8 cross design', 'Superior shoulder alignment', 'Clavicle area support', 'Simple slip-on', 'Unisex & adjustable'],
    shortDescription: 'Stronger upper back & shoulder support with figure-8 pattern for firmer shoulder retraction.',
    tags: ['posture', 'figure 8', 'upper back'],
    variantId: 52324664607002,
    variants: [{ id: 52324664607002, title: 'Default Title', price: '899.00', compareAtPrice: '1599.00', available: true }],
  },
  {
    id: 10265057132826,
    title: 'Abdominal Support Belt - Core Comfort & Stability',
    shortTitle: 'Abdominal Support Belt',
    handle: 'abdominal-support-belt-core-support-recovery',
    productType: 'Health & Wellness',
    price: 599,
    compareAtPrice: 1599,
    discount: 63,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.32.25AM.jpg?v=1780864098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.32.26AM_1.jpg?v=1780864098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.32.26AM_2.jpg?v=1780864098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.32.26AM.jpg?v=1780864098',
    ],
    benefits: ['Targeted compression', 'Adjustable velcro closure', 'Breathable material', 'Spinal alignment', 'Reduces strain'],
    shortDescription: 'Core & waist support for daily comfort. Gentle compression for stability during work or recovery.',
    tags: ['core support', 'abdominal', 'recovery'],
    variantId: 52324663820570,
    variants: [{ id: 52324663820570, title: 'Default Title', price: '599.00', compareAtPrice: '1599.00', available: true }],
    badge: 'Best Value',
  },
  {
    id: 10265057231130,
    title: 'Postpartum Recovery Belt - New Mother Support',
    shortTitle: 'Postpartum Recovery Belt',
    handle: 'postpartum-tummy-belt-post-pregnancy-recovery',
    productType: 'Maternity & Baby',
    price: 1099,
    compareAtPrice: 2199,
    discount: 50,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.27.46AM_1.jpg?v=1780864001',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.27.46AM.jpg?v=1780864002',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.27.47AM_1.jpg?v=1780864001',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.27.47AM.jpg?v=1780864001',
    ],
    benefits: ['Gentle abdominal compression', 'Post-delivery comfort', 'Core muscle support', 'Lower back support', 'Soft & breathable'],
    shortDescription: 'Designed with care for new moms. Gentle support during postpartum recovery.',
    tags: ['postpartum', 'maternity', 'recovery'],
    variantId: 52324664082714,
    variants: [
      { id: 52324664082714, title: 'Beige', price: '1099.00', compareAtPrice: '2199.00', available: true },
      { id: 52324755570970, title: 'Black', price: '1099.00', compareAtPrice: '2199.00', available: true },
    ],
  },
  {
    id: 10265057526042,
    title: 'Sweat Belt - Fitness & Workout Waist Support',
    shortTitle: 'Sweat Belt',
    handle: 'sweat-belt-fitness-workout-waist-support',
    productType: 'Fitness & Sports',
    price: 499,
    compareAtPrice: 999,
    discount: 50,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.35.28AM.jpg?v=1780863226',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.35.29AM.jpg?v=1780863226',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.35.30AM_1.jpg?v=1780863226',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.35.30AM.jpg?v=1780863226',
    ],
    benefits: ['Premium neoprene', 'Core compression', 'Thermal activity boost', 'Adjustable fit (28"-50")', 'Unisex design'],
    shortDescription: 'Enhance your workout with premium neoprene waist support. Perfect for gym, cardio & home workouts.',
    tags: ['fitness', 'workout', 'gym'],
    variantId: 52324665196826,
    variants: [{ id: 52324665196826, title: 'Default Title', price: '499.00', compareAtPrice: '999.00', available: true }],
  },
  {
    id: 10265056870682,
    title: 'Elastic Compression Belt (2 Meter) - Versatile Support',
    shortTitle: 'Compression Belt',
    handle: '2-meter-elastic-compression-belt-waist-support',
    productType: 'Health & Wellness',
    price: 599,
    compareAtPrice: 1299,
    discount: 54,
    images: [
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.29.15AM.jpg?v=1780863098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.29.16AM.jpg?v=1780863098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.29.17AM_1.jpg?v=1780863098',
      'https://cdn.shopify.com/s/files/1/0994/8836/6874/files/WhatsAppImage2026-06-07at10.29.17AM.jpg?v=1780863098',
    ],
    benefits: ['2-meter elastic length', 'Customizable compression', 'Versatile wrapping', 'Multi-purpose support', 'Breathable fabric'],
    shortDescription: 'Versatile 2-meter elastic belt for customizable compression and support wherever you need it.',
    tags: ['compression', 'elastic', 'versatile'],
    variantId: 52324662346010,
    variants: [{ id: 52324662346010, title: 'Default Title', price: '599.00', compareAtPrice: '1299.00', available: true }],
  },
];

export function getProductByHandle(handle: string): ProductData | undefined {
  return PRODUCTS?.find((p: ProductData) => p?.handle === handle);
}

export function getCheckoutUrl(variantId: number): string {
  return `https://${STORE_URL}/cart/${variantId}:1`;
}

export function getBuyNowUrl(variantId: number): string {
  return `https://${STORE_URL}/cart/${variantId}:1`;
}
