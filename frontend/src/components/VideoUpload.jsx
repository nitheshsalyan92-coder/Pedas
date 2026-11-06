
import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function VideoUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [videoId, setVideoId] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  async function uploadVideo() {
    if (!file) {
      setMessage("Please select a video first.");
      return;
    }

    try {
      setIsUploading(true);
      setMessage("Uploading video...");
      setResult(null);

      // Upload video
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadResponse.json().catch(() => ({}));

      if (!uploadResponse.ok) {
        throw new Error(uploadData.message || `Upload failed (HTTP ${uploadResponse.status})`);
      }

      const id = uploadData.video_id;
      setVideoId(id);

      setMessage("Video uploaded. Analyzing...");

      // Analyze video
      const analyzeResponse = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_id: id,
        }),
      });

      const analyzeData = await analyzeResponse.json().catch(() => ({}));

      if (!analyzeResponse.ok) {
        throw new Error(analyzeData.message || `Analysis failed (HTTP ${analyzeResponse.status})`);
      }

      const analysis =
        analyzeData.result ?? analyzeData.results?.[0];

      if (!analysis) {
        throw new Error("Analysis result not returned");
      }

      setResult(analysis);
      setMessage("Analysis completed successfully!");
    } catch (error) {
      setMessage(
        error instanceof TypeError
          ? `Cannot reach the analysis server at ${API}. Start the backend and try again.`
          : error.message || "Video analysis failed."
      );
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="rounded-2xl border border-line bg-white p-5 shadow-sm space-y-4">
      <h2 className="font-display text-xl font-bold text-navy">
        Traffic Video Analysis
      </h2>

      <p className="text-sm text-slate-600">
        Upload a traffic video to analyze vehicles,
        pedestrians, and safety conflicts.
      </p>

      <label
        htmlFor="traffic-video"
        className="flex w-full cursor-pointer items-center justify-between gap-4 rounded-lg border border-line px-4 py-3 text-sm focus-within:ring-2 focus-within:ring-accent"
      >
        <span className="min-w-0 truncate text-slate-600">
          {file?.name ?? "No video selected"}
        </span>
        <span className="shrink-0 font-semibold text-accent">Choose video</span>
        <input
          id="traffic-video"
          type="file"
          accept="video/*"
          className="sr-only"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </label>

      <button
        onClick={uploadVideo}
        disabled={isUploading}
        className="rounded-lg bg-accent px-4 py-2 font-semibold text-white"
      >
        {isUploading ? "Uploading..." : "Upload & Analyze"}
      </button>

      <p className="text-sm text-slate-600" role="status" aria-live="polite">{message}</p>

      {videoId && (
        <p className="text-sm break-all">
          Video ID: {videoId}
        </p>
      )}

      {result && (
        <div className="grid gap-3 sm:grid-cols-2">
          <p>Vehicles: {result.vehicles_detected ?? 0}</p>
          <p>Pedestrians: {result.pedestrians_detected ?? 0}</p>
          <p>Conflicts: {result.conflicts_detected ?? 0}</p>
          <p>Risk: {result.risk_level ?? "UNKNOWN"}</p>
        </div>
      )}
    </section>
  );
}
