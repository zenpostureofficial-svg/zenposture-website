export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ wishlisted: false }, { status: 200 });
    }
    const userId = (session.user as any)?.id;
    const { searchParams } = new URL(request?.url ?? '');
    const productId = searchParams?.get?.('productId');

    if (productId) {
      const item = await prisma.wishlist.findUnique({
        where: { userId_productId: { userId, productId } },
      });
      return NextResponse.json({ wishlisted: !!item });
    }

    const items = await prisma.wishlist.findMany({ where: { userId } });
    return NextResponse.json({ items: items ?? [] });
  } catch (error: any) {
    console.error('Wishlist GET error:', error);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
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
    const { productId } = body ?? {};

    if (!productId) {
      return NextResponse.json({ error: 'Product ID required' }, { status: 400 });
    }

    await prisma.wishlist.create({
      data: { userId, productId },
    });

    return NextResponse.json({ message: 'Added to wishlist' }, { status: 201 });
  } catch (error: any) {
    if (error?.code === 'P2002') {
      return NextResponse.json({ message: 'Already in wishlist' }, { status: 200 });
    }
    console.error('Wishlist POST error:', error);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }
    const userId = (session.user as any)?.id;
    const body = await request.json();
    const { productId } = body ?? {};

    if (!productId) {
      return NextResponse.json({ error: 'Product ID required' }, { status: 400 });
    }

    await prisma.wishlist.deleteMany({
      where: { userId, productId },
    });

    return NextResponse.json({ message: 'Removed from wishlist' });
  } catch (error: any) {
    console.error('Wishlist DELETE error:', error);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}
