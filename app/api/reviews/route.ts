export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request?.url ?? '');
    const productId = searchParams?.get?.('productId');

    if (!productId) {
      return NextResponse.json({ reviews: [] });
    }

    const reviews = await prisma.review.findMany({
      where: { productId },
      include: { user: { select: { name: true } } },
      orderBy: { createdAt: 'desc' },
      take: 20,
    });

    return NextResponse.json({ reviews: reviews ?? [] });
  } catch (error: any) {
    console.error('Reviews GET error:', error);
    return NextResponse.json({ reviews: [] });
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const userId = (session.user as any)?.id;
    const body = await request.json();
    const { productId, rating, title, comment } = body ?? {};

    if (!productId || !rating || !comment) {
      return NextResponse.json({ error: 'Product ID, rating, and comment are required' }, { status: 400 });
    }

    const review = await prisma.review.create({
      data: {
        userId,
        productId,
        rating: Math.min(5, Math.max(1, rating)),
        title: title ?? '',
        comment,
      },
    });

    return NextResponse.json({ review }, { status: 201 });
  } catch (error: any) {
    console.error('Reviews POST error:', error);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}
