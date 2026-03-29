'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useFunnelStore } from '@/store/useFunnelStore';
import { submitLead } from '@/lib/api';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';

const leadSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional(),
});

export default function AssessmentPage() {
  const { campaign: campaignSlug, branch: branchSlug } = useParams();
  const router = useRouter();
  const { branch, campaign } = useFunnelStore();
  const [step, setStep] = useState(0); // 0 is Lead Capture, 1+ are Questions
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<z.infer<typeof leadSchema>>({
    resolver: zodResolver(leadSchema),
  });

  if (!branch) return <div className="text-center p-8">Loading...</div>;

  const questions = branch.assessment?.questions || [];
  const campaignId =
    typeof branch.campaign === 'number' ? branch.campaign : branch.campaign?.id;
  const totalSteps = questions.length + 1;
  const progress = ((step) / totalSteps) * 100;

  const nextStep = () => {
    if (step === 0) {
      form.handleSubmit(() => setStep(1))();
    } else if (step < questions.length) {
      setStep(step + 1);
    } else {
      handleSubmitAll();
    }
  };

  const handleSubmitAll = async () => {
    if (!campaignId) {
      alert('Campaign data is missing. Please go back and try again.');
      return;
    }

    setIsSubmitting(true);
    try {
      const leadData = form.getValues();
      const payload = {
        campaign: campaignId,
        branch: branch.id,
        cta_type: 'assessment',
        ...leadData,
        responses: Object.entries(answers).map(([qId, answer]) => ({
          question: parseInt(qId),
          answer,
        })),
      };
      await submitLead(payload);
      router.push(`/${campaignSlug}/${branchSlug}/success`);
    } catch (err) {
      console.error(err);
      alert('Error submitting. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 py-12">
      <div className="container mx-auto px-4 max-w-2xl">
        <Progress value={progress} className="mb-8" />
        
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="text-center">
              {step === 0 ? "Let's get started" : `Question ${step} of ${questions.length}`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {step === 0 ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>First Name</Label>
                    <Input {...form.register('first_name')} placeholder="Jane" />
                    {form.formState.errors.first_name && <p className="text-red-500 text-sm">{form.formState.errors.first_name.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Last Name</Label>
                    <Input {...form.register('last_name')} placeholder="Doe" />
                    {form.formState.errors.last_name && <p className="text-red-500 text-sm">{form.formState.errors.last_name.message}</p>}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input {...form.register('email')} placeholder="jane@example.com" />
                  {form.formState.errors.email && <p className="text-red-500 text-sm">{form.formState.errors.email.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Phone (Optional)</Label>
                  <Input {...form.register('phone')} placeholder="555-0123" />
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <h3 className="text-xl font-medium">{questions[step - 1].text}</h3>
                {questions[step - 1].type === 'multiple_choice' ? (
                  <RadioGroup
                    onValueChange={(val) =>
                      setAnswers((current) => ({
                        ...current,
                        [questions[step - 1].id]: val,
                      }))
                    }
                    value={answers[questions[step - 1].id] ?? ''}
                  >
                    {questions[step-1].options.map((opt: string, idx: number) => (
                      <div key={idx} className="flex items-center space-x-2 border p-3 rounded-lg hover:bg-slate-50">
                        <RadioGroupItem value={opt} id={`opt-${idx}`} />
                        <Label htmlFor={`opt-${idx}`} className="w-full cursor-pointer">{opt}</Label>
                      </div>
                    ))}
                  </RadioGroup>
                ) : (
                  <Input
                    onChange={(e) =>
                      setAnswers((current) => ({
                        ...current,
                        [questions[step - 1].id]: e.target.value,
                      }))
                    }
                    value={answers[questions[step-1].id] || ''}
                    placeholder="Type your answer here..."
                  />
                )}
              </div>
            )}

            <div className="flex justify-between mt-8">
              {step > 0 && <Button variant="ghost" onClick={() => setStep(step - 1)}>Back</Button>}
              <Button 
                className="ml-auto" 
                onClick={nextStep}
                disabled={isSubmitting}
              >
                {step === questions.length ? (isSubmitting ? 'Submitting...' : 'Finish') : 'Continue'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
