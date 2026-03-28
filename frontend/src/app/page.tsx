'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchActiveCampaign } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const redirectToActiveCampaign = async () => {
      try {
        const campaign = await fetchActiveCampaign();
        if (campaign?.slug) {
          router.push(`/${campaign.slug}`);
          return;
        }
      } catch (error) {
        console.error(error);
      }

      router.push('/financial-advisor');
    };

    redirectToActiveCampaign();
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-xl">Redirecting to demo campaign...</p>
    </div>
  );
}
