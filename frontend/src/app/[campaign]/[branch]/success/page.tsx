'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { CheckCircle2 } from 'lucide-react';

export default function SuccessPage() {
  const { campaign: campaignSlug } = useParams();
  const router = useRouter();

  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <div className="flex justify-center">
          <CheckCircle2 className="h-24 w-24 text-green-500" />
        </div>
        <h1 className="text-4xl font-bold">You&apos;re all set!</h1>
        <p className="text-xl text-muted-foreground">
          Thank you for your submission. We&apos;ve received your information and will be in touch shortly.
        </p>
        <div className="pt-8">
          <Button size="lg" onClick={() => router.push(`/${campaignSlug}`)} className="w-full">
            Return to Home
          </Button>
        </div>
      </div>
    </main>
  );
}
