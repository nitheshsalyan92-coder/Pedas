
import { useState } from "react";

const API = "http://localhost:5000";

export default function VideoUpload() {
  const [file, setFile] = useState(null);
  const [videoId, setVideoId] = useState("");
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");

  async function uploadVideo() {
    if (!file) {
      setMessage("Please select a video first.");
      return;
    }

    try {
      setMessage("Uploading video...");

      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(`${API}/upload`, {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadResponse.json();

      if (!uploadResponse.ok) {
        throw new Error(uploadData.message || "Upload failed");
      }

      const id = uploadData.video_id;
      setVideoId(id);

      setMessage("Video uploaded. Analyzing...");

      const analyzeResponse = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ video_id: id }),
      });

      const analyzeData = await analyzeResponse.json();

      if (!analyzeResponse.ok) {
        throw new Error(analyzeData.message || "Analysis failed");
      }

      setResult(analyzeData.result);
      setMessage("Analysis completed!");
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <section className="rounded-2xl border border-line bg-white p-5 shadow-sm space-y-4">
      <h2 className="font-display text-xl font-bold text-navy">
        Traffic Video Analysis
      </h2>

      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button
        onClick={uploadVideo}
        className="rounded-lg bg-accent px-4 py-2 font-semibold text-white"
      >
        Upload & Analyze
      </button>

      <p className="text-sm text-slate-600">{message}</p>

      {videoId && (
        <p className="text-sm break-all">
          Video ID: {videoId}
        </p>
      )}

      {result && (
        <div className="grid gap-3 sm:grid-cols-2">
          <p>Vehicles: {result.vehicles_detected}</p>
          <p>Pedestrians: {result.pedestrians_detected}</p>
          <p>Conflicts: {result.conflicts_detected}</p>
          <p>Risk: {result.risk_level}</p>
        </div>
      )}
    </section>
  );
}

