import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const hashedPassword = await bcrypt.hash('johndoe123', 12);
  
  await prisma.user.upsert({
    where: { email: 'john@doe.com' },
    update: {},
    create: {
      email: 'john@doe.com',
      name: 'John Doe',
      password: hashedPassword,
      role: 'admin',
    },
  });

  // Seed some reviews for social proof
  const reviewsData = [
    { productId: '10265057296666', rating: 5, title: 'Life changing!', comment: 'I work 10 hours at my desk and this posture corrector has completely eliminated my back pain. Best purchase ever!', name: 'Rahul M.', email: 'rahul.m@example.com' },
    { productId: '10265057296666', rating: 5, title: 'Perfect for WFH', comment: 'Working from home was ruining my posture. This corrector is comfortable enough to wear all day under my shirt.', name: 'Priya S.', email: 'priya.s@example.com' },
    { productId: '10265057296666', rating: 4, title: 'Really helps with desk posture', comment: 'Noticed improvement in my shoulder alignment within the first week. Very comfortable material.', name: 'Amit K.', email: 'amit.k@example.com' },
    { productId: '10265057362202', rating: 5, title: 'Stronger support than expected', comment: 'The figure-8 design provides much better shoulder retraction. Wearing it during study sessions has really helped.', name: 'Sneha R.', email: 'sneha.r@example.com' },
    { productId: '10265057362202', rating: 5, title: 'Great quality', comment: 'Material is breathable and the velcro holds well. Using it for 3 weeks now and can feel the difference.', name: 'Vikram P.', email: 'vikram.p@example.com' },
    { productId: '10265057132826', rating: 5, title: 'Excellent core support', comment: 'Using this after my gym sessions. Provides perfect compression without being too tight. Highly recommend!', name: 'Deepak L.', email: 'deepak.l@example.com' },
    { productId: '10265057231130', rating: 5, title: 'Essential for new moms', comment: 'This belt was a lifesaver during my postpartum recovery. Gentle but firm support exactly where needed.', name: 'Anita G.', email: 'anita.g@example.com' },
    { productId: '10265057526042', rating: 4, title: 'Great workout companion', comment: 'Love wearing this during my cardio sessions. The neoprene material is high quality and comfortable.', name: 'Karan T.', email: 'karan.t@example.com' },
  ];

  for (const review of reviewsData) {
    const hashedPw = await bcrypt.hash('password123', 12);
    const user = await prisma.user.upsert({
      where: { email: review.email },
      update: {},
      create: {
        email: review.email,
        name: review.name,
        password: hashedPw,
      },
    });

    const existingReview = await prisma.review.findFirst({
      where: { userId: user.id, productId: review.productId },
    });
    if (!existingReview) {
      await prisma.review.create({
        data: {
          userId: user.id,
          productId: review.productId,
          rating: review.rating,
          title: review.title,
          comment: review.comment,
          verified: true,
        },
      });
    }
  }

  console.log('Seed completed successfully');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
