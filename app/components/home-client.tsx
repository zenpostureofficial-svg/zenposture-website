'use client';

import AnnouncementBar from './announcement-bar';
import Header from './header';
import HeroSection from './hero-section';
import SocialProofBar from './social-proof-bar';
import FeaturedProducts from './featured-products';
import CategorySection from './category-section';
import WhySection from './why-section';
import TrustSection from './trust-section';
import TransformationSection from './transformation-section';
import AllProductsSection from './all-products-section';
import TestimonialsSection from './testimonials-section';
import FaqSection from './faq-section';
import CtaBanner from './cta-banner';
import Footer from './footer';

export default function HomeClient() {
  return (
    <div className="min-h-screen bg-white">
      <AnnouncementBar />
      <Header />
      <HeroSection />
      <SocialProofBar />
      <FeaturedProducts />
      <CategorySection />
      <WhySection />
      <TrustSection />
      <TransformationSection />
      <AllProductsSection />
      <TestimonialsSection />
      <FaqSection />
      <CtaBanner />
      <Footer />
    </div>
  );
}
