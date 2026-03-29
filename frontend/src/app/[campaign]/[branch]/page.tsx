'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchBranch, getBranchErrorMessage, submitLead } from '@/lib/api';
import { useFunnelStore } from '@/store/useFunnelStore';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, Volume2, VolumeX, X } from 'lucide-react';
import { Input } from '@/components/ui/input';

declare global {
  interface Window {
    Calendly?: {
      initInlineWidget: (options: {
        url: string;
        parentElement: HTMLElement;
        resize?: boolean;
        prefill?: {
          name?: string;
          firstName?: string;
          lastName?: string;
          email?: string;
        };
      }) => void;
    };
  }
}

export default function BranchPage() {
  const { campaign: campaignSlug, branch: branchSlug } = useParams();
  const router = useRouter();
  const { branch, setBranch } = useFunnelStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isCalendlyOpen, setIsCalendlyOpen] = useState(false);
  const [isCalendlyReady, setIsCalendlyReady] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [scheduleLead, setScheduleLead] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const videoRef = useRef<HTMLVideoElement>(null);
  const calendlyContainerRef = useRef<HTMLDivElement>(null);
  const hasSubmittedScheduledLeadRef = useRef(false);

  useEffect(() => {
    const getBranch = async () => {
      try {
        const data = await fetchBranch(campaignSlug as string, branchSlug as string);
        setBranch(data);
      } catch (err) {
        setError(getBranchErrorMessage(err));
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    getBranch();
  }, [campaignSlug, branchSlug, setBranch]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !branch?.video_url) {
      return;
    }

    let cancelled = false;

    const startPlayback = async () => {
      try {
        video.currentTime = 0;
        video.muted = false;
        setIsMuted(false);
        await video.play();
      } catch {
        if (cancelled) {
          return;
        }
        video.muted = true;
        setIsMuted(true);
        try {
          await video.play();
        } catch (playError) {
          console.error(playError);
        }
      }
    };

    startPlayback();

    return () => {
      cancelled = true;
    };
  }, [branch?.video_url]);

  useEffect(() => {
    if (!isCalendlyOpen || !isCalendlyReady || branch?.cta.type !== 'schedule' || !branch?.cta.config.url) {
      return;
    }

    const initCalendlyWidget = () => {
      if (!window.Calendly || !calendlyContainerRef.current) {
        return;
      }

      calendlyContainerRef.current.innerHTML = '';
      window.Calendly.initInlineWidget({
        url: branch.cta.config.url,
        parentElement: calendlyContainerRef.current,
        resize: true,
        prefill: {
          firstName: scheduleLead.first_name,
          lastName: scheduleLead.last_name,
          email: scheduleLead.email,
          name: `${scheduleLead.first_name} ${scheduleLead.last_name}`.trim(),
        },
      });
    };

    const existingScript = document.querySelector<HTMLScriptElement>('script[data-calendly-widget="true"]');
    if (existingScript) {
      initCalendlyWidget();
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    script.dataset.calendlyWidget = 'true';
    script.onload = initCalendlyWidget;
    document.body.appendChild(script);
  }, [branch?.cta.config.url, branch?.cta.type, isCalendlyOpen, isCalendlyReady, scheduleLead.email, scheduleLead.first_name, scheduleLead.last_name]);

  useEffect(() => {
    if (!isCalendlyOpen || branch?.cta.type !== 'schedule') {
      return;
    }

    const handleCalendlyMessage = async (event: MessageEvent) => {
      if (!event.origin.endsWith('calendly.com')) {
        return;
      }

      if (event.data?.event !== 'calendly.event_scheduled' || hasSubmittedScheduledLeadRef.current) {
        return;
      }

      hasSubmittedScheduledLeadRef.current = true;

      try {
        await submitLead({
          campaign: branch.campaign?.id ?? branch.campaign ?? undefined,
          branch: branch.id,
          cta_type: 'schedule',
          first_name: scheduleLead.first_name,
          last_name: scheduleLead.last_name,
          email: scheduleLead.email,
          phone: scheduleLead.phone,
          responses: [],
        });
        router.push(`/${campaignSlug}/${branchSlug}/success`);
      } catch (submissionError) {
        console.error(submissionError);
        setScheduleError('The meeting was booked, but saving the lead failed. Please contact support.');
        hasSubmittedScheduledLeadRef.current = false;
      }
    };

    window.addEventListener('message', handleCalendlyMessage);
    return () => window.removeEventListener('message', handleCalendlyMessage);
  }, [branch, branchSlug, campaignSlug, isCalendlyOpen, router, scheduleLead]);

  if (loading) return <div className="container mx-auto p-8"><Skeleton className="h-[400px] w-full" /></div>;
  if (error || !branch) return <div className="text-center p-8">{error || 'Branch not found'}</div>;

  const branchCta = branch.cta;
  const hasCta = Boolean(branchCta?.type);
  const branchDescription = branch.description || 'More information for this branch is coming soon.';

  const handleCTA = () => {
    if (!branchCta?.type) {
      return;
    }

    if (branchCta.type === 'assessment') {
      router.push(`/${campaignSlug}/${branchSlug}/assessment`);
    } else if (branchCta.type === 'schedule') {
      setScheduleError(null);
      setIsCalendlyReady(false);
      hasSubmittedScheduledLeadRef.current = false;
      setIsCalendlyOpen(true);
    } else {
      // Redirect to external URL for schedule/download
      if (branchCta.config?.url) {
        window.open(branchCta.config.url, '_blank');
      }
      router.push(`/${campaignSlug}/${branchSlug}/success`);
    }
  };

  const calendlyUrl = branchCta?.type === 'schedule' ? branchCta.config?.url : '';

  const openCalendlyScheduler = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!scheduleLead.first_name || !scheduleLead.last_name || !scheduleLead.email) {
      setScheduleError('First name, last name, and email are required.');
      return;
    }

    setScheduleError(null);
    setIsCalendlyReady(true);
    hasSubmittedScheduledLeadRef.current = false;
  };

  const toggleMute = () => {
    if (!videoRef.current) {
      return;
    }

    const nextMuted = !videoRef.current.muted;
    videoRef.current.muted = nextMuted;
    setIsMuted(nextMuted);

    if (!nextMuted) {
      videoRef.current.play().catch((playError) => {
        console.error(playError);
      });
    }
  };

  return (
    <main className="h-screen w-full bg-slate-950 text-white overflow-hidden flex flex-col md:flex-row">
      {/* Video Section - Main Content */}
      <div className="flex-1 relative bg-black flex items-center justify-center">
        <div className="w-full h-full relative">
          {branch.video_url && (
            <video
              ref={videoRef}
              key={branch.video_url}
              src={branch.video_url}
              autoPlay
              muted={isMuted}
              loop
              playsInline
              preload="auto"
              className="absolute top-0 left-0 h-full w-full object-cover"
            />
          )}
          {!branch.video_url && <div className="absolute inset-0 bg-slate-900" />}
        </div>
        
        {/* Back Button Overlay */}
        <div className="absolute top-8 left-8 z-10">
          <Button 
            variant="ghost" 
            onClick={() => router.push(`/${campaignSlug}`)}
            className="bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm border border-white/10"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to choices
          </Button>
        </div>

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
      </div>

      {isCalendlyOpen && calendlyUrl && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
          <div className="relative h-[90vh] w-full max-w-5xl overflow-hidden rounded-2xl border border-slate-700 bg-white shadow-2xl">
            <button
              type="button"
              onClick={() => {
                setIsCalendlyOpen(false);
                setIsCalendlyReady(false);
                setScheduleError(null);
              }}
              className="absolute top-4 right-4 z-10 rounded-full bg-slate-900/80 p-2 text-white transition-colors hover:bg-slate-900"
              aria-label="Close scheduler"
            >
              <X className="h-5 w-5" />
            </button>
            {!isCalendlyReady ? (
              <div className="flex h-full flex-col justify-center gap-6 bg-slate-50 p-6 md:p-10">
                <div>
                  <h2 className="text-2xl font-semibold text-slate-900">Schedule a conversation</h2>
                  <p className="mt-2 text-sm text-slate-600">
                    Add your contact details first. Once the meeting is booked, this branch will register it as a lead submission automatically.
                  </p>
                </div>

                <form className="grid gap-4 md:grid-cols-2" onSubmit={openCalendlyScheduler}>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-800">First name</label>
                    <Input
                      value={scheduleLead.first_name}
                      onChange={(event) =>
                        setScheduleLead((current) => ({ ...current, first_name: event.target.value }))
                      }
                      placeholder="Jane"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-800">Last name</label>
                    <Input
                      value={scheduleLead.last_name}
                      onChange={(event) =>
                        setScheduleLead((current) => ({ ...current, last_name: event.target.value }))
                      }
                      placeholder="Doe"
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-slate-800">Email</label>
                    <Input
                      type="email"
                      value={scheduleLead.email}
                      onChange={(event) =>
                        setScheduleLead((current) => ({ ...current, email: event.target.value }))
                      }
                      placeholder="jane@example.com"
                    />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-slate-800">Phone</label>
                    <Input
                      value={scheduleLead.phone}
                      onChange={(event) =>
                        setScheduleLead((current) => ({ ...current, phone: event.target.value }))
                      }
                      placeholder="555-0123"
                    />
                  </div>
                  {scheduleError && (
                    <p className="md:col-span-2 text-sm font-medium text-red-600">{scheduleError}</p>
                  )}
                  <div className="md:col-span-2 flex justify-end">
                    <Button type="submit">Continue to scheduler</Button>
                  </div>
                </form>
              </div>
            ) : (
              <div className="h-full w-full bg-white">
                {scheduleError && (
                  <div className="border-b border-red-200 bg-red-50 px-6 py-3 text-sm font-medium text-red-700">
                    {scheduleError}
                  </div>
                )}
                <div ref={calendlyContainerRef} className="h-full w-full" />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Info & CTA Sidebar */}
      <div className="w-full md:w-[400px] h-full bg-slate-900 border-l border-slate-800 flex flex-col p-8 overflow-y-auto">
        <div className="mb-8 md:mt-12">
          <h1 className="text-3xl font-bold tracking-tight mb-4">{branch.name}</h1>
          <p className="text-slate-300 text-lg leading-relaxed">{branchDescription}</p>
        </div>

        <div className="mt-auto space-y-6 pb-8">
          <div className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700">
            <h2 className="text-xl font-semibold mb-4 text-center">Ready to take the next step?</h2>
            {hasCta ? (
              <Button size="lg" className="w-full py-6 text-lg rounded-xl shadow-xl hover:scale-[1.02] transition-transform" onClick={handleCTA}>
                {branchCta.type === 'assessment' ? 'Start Assessment' : branchCta.config?.button_text || 'Continue'}
              </Button>
            ) : (
              <div className="rounded-xl border border-dashed border-slate-600 px-4 py-6 text-center text-sm text-slate-400">
                This branch is live, but its next-step CTA has not been configured yet.
              </div>
            )}
          </div>
          
          <div className="text-center">
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Powered by Starlight Creative Studios</p>
          </div>
        </div>
      </div>
    </main>
  );
}
