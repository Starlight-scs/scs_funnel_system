'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchActiveCampaign } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [message, setMessage] = useState('Loading campaign...');

  useEffect(() => {
    const redirectToActiveCampaign = async () => {
      try {
        const campaign = await fetchActiveCampaign();
        if (campaign?.slug) {
          router.push(`/${campaign.slug}`);
          return;
        }
        setMessage('No published campaign is available yet.');
      } catch (error) {
        console.error(error);
        setMessage('Unable to load the active campaign.');
      }
    };

    redirectToActiveCampaign();
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-xl">{message}</p>
    </div>
  );
}
