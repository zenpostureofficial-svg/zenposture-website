export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, subject, message } = body ?? {};

    if (!name || !email || !subject || !message) {
      return NextResponse.json({ error: 'All fields are required' }, { status: 400 });
    }

    const session = await getServerSession(authOptions);
    const userId = (session?.user as any)?.id ?? null;

    await prisma.contactForm.create({
      data: {
        name,
        email,
        subject,
        message,
        userId,
      },
    });

    return NextResponse.json({ message: 'Contact form submitted successfully' }, { status: 201 });
  } catch (error: any) {
    console.error('Contact form error:', error);
    return NextResponse.json({ error: 'Something went wrong' }, { status: 500 });
  }
}
