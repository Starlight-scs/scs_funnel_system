"use client";

import { generateUploadButton } from "@uploadthing/react";
import { OurFileRouter } from "@/app/api/uploadthing/core";

// We point the URL to our Django backend endpoint
export const UploadButton = generateUploadButton<OurFileRouter>({
  url: "/api/uploadthing",
});
