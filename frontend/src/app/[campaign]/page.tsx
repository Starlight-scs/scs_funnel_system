'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchCampaign } from '@/lib/api';
import { useFunnelStore } from '@/store/useFunnelStore';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Volume2, VolumeX } from 'lucide-react';

export default function CampaignPage() {
  const { campaign: campaignSlug } = useParams();
  const router = useRouter();
  const { campaign, setCampaign, setBranch } = useFunnelStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const getCampaign = async () => {
      try {
        const data = await fetchCampaign(campaignSlug as string);
        console.log('Campaign data:', data);
        console.log('Intro video URL:', data.intro_video_url);
        setCampaign(data);
      } catch (err) {
        setError('Campaign not found');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    getCampaign();
  }, [campaignSlug, setCampaign]);

  if (loading) return <div className="container mx-auto p-8"><Skeleton className="h-[400px] w-full" /></div>;
  if (error || !campaign) return <div className="text-center p-8">{error || 'Campaign not found'}</div>;

  const handleBranchSelect = (branch: any) => {
    setBranch(branch);
    router.push(`/${campaignSlug}/${branch.slug}`);
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted;
      setIsMuted(!isMuted);
    }
  };

  return (
    <main className="h-screen w-full bg-slate-950 text-white overflow-hidden relative">
      {/* Full Screen Video Background */}
      <div className="absolute inset-0">
        {campaign.intro_video_url && (
          <video
            ref={videoRef}
            src={campaign.intro_video_url}
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
          />
        )}
        {/* Dark Overlay */}
        <div className="absolute inset-0 bg-black/50"></div>
      </div>

      {/* Content Layer */}
      <div className="relative z-10 h-full flex flex-col md:flex-row items-center p-4 md:p-8">
        {/* Title Section - Left Side */}
        <div className="flex-1 flex items-center justify-center p-4 md:p-8">
          <div className="text-center">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold tracking-tight drop-shadow-lg mb-4 md:mb-6">
              {campaign.name}
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl lg:text-4xl text-slate-100 drop-shadow-md">
              {campaign.headline}
            </p>
          </div>
        </div>

        {/* Floating Branch Selection Card - Right Side */}
        <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-md rounded-2xl border border-slate-700/50 shadow-2xl p-5 md:p-8 md:mr-2 lg:mr-3">
          <div className="mb-5 md:mb-6 text-center">
            <h2 className="text-xl md:text-2xl font-semibold mb-2">There is a place for you here.</h2>
            <p className="text-slate-400 text-xs md:text-sm">Select what fits your situation.</p>
          </div>

          <div className="space-y-3 md:space-y-4">
            {campaign.branches.map((branch: any) => (
              <Card
                key={branch.id}
                className="bg-slate-800/80 border-slate-700 hover:border-primary transition-all cursor-pointer hover:shadow-2xl group text-white text-center"
                onClick={() => handleBranchSelect(branch)}
              >
                <CardHeader className="p-3 md:p-4">
                  <CardTitle className="text-xl md:text-2xl group-hover:text-primary transition-colors">{branch.label}</CardTitle>
                  <CardDescription className="text-slate-400 text-sm md:text-base">{branch.description}</CardDescription>
                </CardHeader>
                <CardContent className="p-3 md:p-4 pt-0">
                  <Button variant="secondary" size="sm" className="px-3 py-1 h-7 text-xs group-hover:bg-primary group-hover:text-white transition-all">
                    Choose Path
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-6 md:mt-8 text-center">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Powered by Starlight Creative Studios</p>
          </div>
        </div>
      </div>

      {/* Audio Toggle Button */}
      <button
        onClick={toggleMute}
        className="absolute bottom-4 left-4 md:bottom-8 md:left-8 z-20 p-2 md:p-3 bg-black/50 hover:bg-black/70 rounded-full transition-colors backdrop-blur-sm border border-white/20"
        aria-label={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? (
          <VolumeX className="w-5 h-5 md:w-6 md:h-6 text-white" />
        ) : (
          <Volume2 className="w-5 h-5 md:w-6 md:h-6 text-white" />
        )}
      </button>
    </main>
  );
}
