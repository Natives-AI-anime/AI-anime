import React, { useState, useEffect } from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";

const base64ToBlob = async (base64: string) => {
  const res = await fetch(base64);
  return await res.blob();
};

interface AnimeStudioProps {
  baseUrl: string;
  activeStep: 0 | 1 | 2;
  onStepChange: (step: 0 | 1 | 2) => void;
}

const AnimeStudio: React.FC<AnimeStudioProps> = ({
  baseUrl,
  activeStep,
  onStepChange,
}) => {
  // Navigation State (Lifted to parent)

  // Form State
  const [projectName, setProjectName] = useState("");
  const [prompt, setPrompt] = useState("");

  // File State
  const [startFile, setStartFile] = useState<File | null>(null);
  const [endFile, setEndFile] = useState<File | null>(null);
  const [startPreview, setStartPreview] = useState<string | null>(null);
  const [endPreview, setEndPreview] = useState<string | null>(null);

  // Request State
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [zipUrl, setZipUrl] = useState<string | null>(null);

  // Unified Player State
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [fps, setFps] = useState(10); // Playback speed for JS player
  const sliderRef = React.useRef<HTMLDivElement>(null);

  // Revision State
  const [selectionStart, setSelectionStart] = useState<number | null>(null);
  const [selectionEnd, setSelectionEnd] = useState<number | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [revisionPrompt, setRevisionPrompt] = useState("");

  // Playback Loop
  useEffect(() => {
    let interval: number;
    if (isPlaying && result?.data?.frames?.length > 0) {
      interval = window.setInterval(() => {
        setCurrentFrameIndex((prev) => {
          const next = prev + 1;
          if (next >= result.data.frames.length) {
            setIsPlaying(false); // Stop at end
            return prev;
          }
          return next;
        });
      }, 1000 / fps);
    }
    return () => clearInterval(interval);
  }, [isPlaying, fps, result]);

  // Sync scroll with current frame
  useEffect(() => {
    if (sliderRef.current && result?.data?.frames) {
      const scrollContainer = sliderRef.current;
      const frameWidth = 222; // Approx 213px width + 8px gap (height 120px * 16/9)
      // With padding-left/right: 50%, the frame 0 starts at center.
      // We want to scroll so that the center of the viewport (scrollLeft + width/2)
      // matches the center of the target frame (padding + index*stride + stride/2).
      // scrollLeft + width/2 = width/2 + index*stride + stride/2
      // scrollLeft = index * stride + stride/2
      // But we adjust slightly for visual centering of the image itself not the slot
      const targetScroll = currentFrameIndex * frameWidth + frameWidth / 2;

      // Use "auto" (instant) scrolling during playback to prevent lag, "smooth" otherwise
      scrollContainer.scrollTo({
        left: targetScroll,
        behavior: isPlaying ? "auto" : "smooth",
      });
    }
  }, [currentFrameIndex, result, isPlaying]);

  const togglePlay = () => setIsPlaying(!isPlaying);

  const steps = [
    { title: "Creation", icon: "fa-pencil-alt", desc: "Setup Generation" },
    { title: "Review", icon: "fa-eye", desc: "Check & Modify" },
    { title: "Export", icon: "fa-download", desc: "Save Results" },
  ];

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "start" | "end"
  ) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const previewUrl = URL.createObjectURL(file);

      if (type === "start") {
        setStartFile(file);
        setStartPreview(previewUrl);
      } else {
        setEndFile(file);
        setEndPreview(previewUrl);
      }
    }
  };

  const handleGenerate = async () => {
    if (!startFile || !endFile) {
      setError("Please select both start and end images.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setVideoUrl(null); // Reset video url

    try {
      const formData = new FormData();
      formData.append("start_image", startFile);
      formData.append("end_image", endFile);
      formData.append("prompt", prompt);
      formData.append("project_name", projectName);

      // Clean base url to remove trailing slash
      const cleanBaseUrl = baseUrl.endsWith("/")
        ? baseUrl.slice(0, -1)
        : baseUrl;
      const endpoint = `${cleanBaseUrl}/generate-video`;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData, // fetch automatically sets Content-Type to multipart/form-data
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `Error: ${response.status}`);
      }

      setResult(data);
      if (data.data?.frames?.length > 0) {
        // Set initial frame for player
        setCurrentFrameIndex(0);
      }

      // Handle Video Base64 -> Blob URL
      if (data.data?.video_data) {
        try {
          const blob = await base64ToBlob(data.data.video_data);
          const url = URL.createObjectURL(blob);
          setVideoUrl(url);
        } catch (e) {
          console.error("Failed to process video blob", e);
          setVideoUrl(null);
        }
      } else {
        setVideoUrl(null);
      }

      onStepChange(1); // Move to review step
    } catch (err: any) {
      setError(err.message || "Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  const handleMockGenerate = () => {
    // Generate 10 dummy frames (simple colored placeholders)
    const dummyFrames = Array.from({ length: 10 }).map((_, i) => {
      // Create a canvas to generate a data URL
      const canvas = document.createElement("canvas");
      canvas.width = 640;
      canvas.height = 360;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = i % 2 === 0 ? "#1e293b" : "#334155";
        ctx.fillRect(0, 0, 640, 360);
        ctx.fillStyle = "#ffffff";
        ctx.font = "40px sans-serif";
        ctx.fillText(`Mock Frame ${i + 1}`, 240, 180);
      }
      return canvas.toDataURL("image/jpeg");
    });

    setResult({
      status: "success",
      data: {
        frames: dummyFrames,
        video_data: null,
      },
    });
    setCurrentFrameIndex(0);
    onStepChange(1);
    setIsPlaying(true);
  };

  const renderStep0 = () => (
    <div className="flex flex-col items-center w-full max-w-5xl animate-fadeIn">
      {/* Frames Container */}
      <div className="flex items-center gap-6 w-full justify-center mb-8">
        {/* Start Frame Card */}
        <div className="flex-1 max-w-[450px] flex flex-col gap-3 group">
          <div className="flex justify-between items-end px-2">
            <span className="text-xs font-bold text-slate-400 tracking-wider">
              START FRAME
            </span>
          </div>
          <div className="aspect-video bg-slate-900/50 backdrop-blur-md border-2 border-dashed border-slate-800 rounded-xl hover:border-purple-500/50 hover:bg-slate-900/80 transition-all duration-300 relative overflow-hidden shadow-2xl group-hover:shadow-purple-900/10">
            {startPreview ? (
              <img
                src={startPreview}
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                alt="Start"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 transition-colors group-hover:text-slate-500">
                <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center mb-3">
                  <i className="fas fa-image text-2xl"></i>
                </div>
                <span className="text-xs uppercase font-bold tracking-widest">
                  Drop Start Image
                </span>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={(e) => handleFileChange(e, "start")}
            />
            {startPreview && (
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                <span className="px-4 py-2 bg-slate-900/80 rounded-lg text-xs font-bold text-white border border-slate-700">
                  Change Image
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Connector */}
        <div className="flex flex-col items-center gap-2 opacity-40 shrink-0">
          <i className="fas fa-chevron-right text-3xl text-slate-700"></i>
        </div>

        {/* End Frame Card */}
        <div className="flex-1 max-w-[450px] flex flex-col gap-3 group">
          <div className="flex justify-between items-end px-2">
            <span className="text-xs font-bold text-slate-400 tracking-wider">
              END FRAME
            </span>
          </div>
          <div className="aspect-video bg-slate-900/50 backdrop-blur-md border-2 border-dashed border-slate-800 rounded-xl hover:border-purple-500/50 hover:bg-slate-900/80 transition-all duration-300 relative overflow-hidden shadow-2xl group-hover:shadow-purple-900/10">
            {endPreview ? (
              <img
                src={endPreview}
                className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                alt="End"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-600 transition-colors group-hover:text-slate-500">
                <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center mb-3">
                  <i className="fas fa-flag-checkered text-2xl"></i>
                </div>
                <span className="text-xs uppercase font-bold tracking-widest">
                  Drop End Image
                </span>
              </div>
            )}
            <input
              type="file"
              accept="image/*"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={(e) => handleFileChange(e, "end")}
            />
            {endPreview && (
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                <span className="px-4 py-2 bg-slate-900/80 rounded-lg text-xs font-bold text-white border border-slate-700">
                  Change Image
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Configuration Form (Moved from sidebar to main area for step 0) */}
      <div className="w-full max-w-3xl bg-slate-900/50 border border-slate-800 rounded-2xl p-8 space-y-6">
        <div className="flex items-center gap-2 pb-4 border-b border-slate-800/50">
          <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
            <i className="fas fa-sliders-h text-purple-500"></i>
          </div>
          <h3 className="font-bold text-lg text-white">Project Settings</h3>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-3">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
              <i className="fas fa-folder mr-2"></i>Project Name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my_anime_project"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 
              text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500 
              outline-none transition-all text-slate-200 placeholder-slate-600 
              shadow-inner"
            />
          </div>
          {/* Can add more specific settings here later */}
        </div>

        <div className="space-y-3">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
            <i className="fas fa-magic mr-2"></i>Interpolation Prompt
          </label>
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 
              text-sm focus:border-purple-500 focus:ring-1 focus:ring-purple-500 
              outline-none h-32 resize-none leading-relaxed text-slate-300 
              placeholder-slate-600 shadow-inner"
              placeholder="Describe the motion and style..."
            />
          </div>
        </div>

        <div className="pt-4 flex justify-end gap-3">
          <button
            onClick={handleMockGenerate}
            className="px-6 py-3 rounded-xl bg-slate-800 text-slate-400 font-bold text-sm hover:bg-slate-700 hover:text-white transition-colors border border-slate-700"
          >
            <i className="fas fa-bug mr-2"></i> Debug: Mock Data
          </button>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className={`px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold text-sm shadow-lg shadow-purple-900/20 hover:shadow-purple-900/40 hover:scale-[1.02] transition-all active:scale-[0.98] flex items-center gap-3 ${
              loading ? "opacity-70 cursor-wait" : ""
            }`}
          >
            {loading ? (
              <>
                <i className="fas fa-circle-notch fa-spin"></i> Processing...
              </>
            ) : (
              <>
                <i className="fas fa-wand-magic-sparkles"></i> Generate Sequence
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const handleRegenerate = async () => {
    if (selectionStart === null || selectionEnd === null) return;

    setIsRegenerating(true);
    try {
      const startIdx = Math.min(selectionStart, selectionEnd);
      const endIdx = Math.max(selectionStart, selectionEnd);

      const response = await fetch(`${baseUrl}/regenerate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName || "project",
          start_image: result.data.frames[startIdx],
          end_image: result.data.frames[endIdx],
          prompt: prompt,
          revision_prompt: revisionPrompt, // Pass specific revision prompt
          target_frame_count: endIdx - startIdx, // approx
        }),
      });

      const data = await response.json();
      if (data.status === "success") {
        // Splice new frames
        const newFrames = data.data.frames;
        const updatedFrames = [...result.data.frames];
        // Remove old range and insert new
        // Note: target_frame_count is just a hint, returned count might differ.
        // We replace the middle part (excluding start/end to keep continuity? or inclusive?)
        // The API returns frames inclusive or exclusive? Usually inclusive of generated content.
        // Let's assume we replace the range [startIdx+1, endIdx-1] with new frames?
        // Actually, simpler to just replace [startIdx, endIdx] with new frames if they include boundaries.
        // But regeneration usually creates frames BETWEEN start and end.
        // Let's assume we replace the whole block.

        // Correct logic: we replace frames BETWEEN start and end.
        // So we keep startIdx and endIdx (anchors) and replace the middle.
        // But what if we want to change the anchors? The user selected them.
        // Let's assume the API returns the FULL sequence including start/end or compatible.
        // If API returns N frames, we place them at startIdx.

        // Simpler for now: Replace the range [startIdx+1, endIdx-1] with newFrames.
        // API logic in main.py calls `regenerate_video_segment`.

        // Update frames
        // We need to know EXACTLY what the server returns.
        // For now, let's just replace the range [startIdx, endIdx] with newFrames assuming they cover the gap.

        const before = updatedFrames.slice(0, startIdx + 1);
        const after = updatedFrames.slice(endIdx);
        const finalFrames = [...before, ...newFrames, ...after];

        setResult({
          ...result,
          data: {
            ...result.data,
            frames: finalFrames,
            video_data: null, // Invalidate video
          },
        });
        setVideoUrl(null); // Invalidate video URL
        setSelectionStart(null);
        setSelectionEnd(null);
      } else {
        alert("Regeneration failed: " + data.message);
      }
    } catch (e) {
      console.error(e);
      alert("Error regenerating segment");
    } finally {
      setIsRegenerating(false);
    }
  };

  const renderStep1 = () => (
    <div className="w-full max-w-6xl animate-fadeIn flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Review Animation
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Frame {currentFrameIndex + 1} / {result?.data?.frames?.length || 0}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onStepChange(0)}
            className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-sm font-semibold hover:bg-slate-700 transition-colors"
          >
            <i className="fas fa-arrow-left mr-2"></i> Edit Parameters
          </button>
          <button
            onClick={async () => {
              // Trigger render first, then navigate
              const success = await handleRenderVideo();
              if (success) {
                onStepChange(2);
              }
            }}
            disabled={isRendering}
            className={`px-6 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm font-bold hover:shadow-lg hover:shadow-purple-900/40 transition-all flex items-center gap-2 ${
              isRendering ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {isRendering ? (
              <>
                <i className="fas fa-circle-notch fa-spin"></i> Rendering...
              </>
            ) : (
              <>
                Accept & Export <i className="fas fa-arrow-right ml-2"></i>
              </>
            )}
          </button>
        </div>
      </div>

      {result && result.data?.frames ? (
        <div className="flex-1 flex flex-col min-h-0 gap-6">
          {/* Main Unified Player */}
          <div className="flex-1 bg-black/40 border border-slate-800 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center group shadow-2xl">
            <div className="w-full h-full p-4 flex items-center justify-center">
              <img
                src={result.data.frames[currentFrameIndex]}
                className="max-h-full max-w-full object-contain pointer-events-none select-none drop-shadow-2xl"
                alt="Animation Preview"
              />
            </div>

            {/* Revision Controls Overlay */}
            <div className="absolute top-4 right-4 flex flex-col gap-2 z-20">
              <button
                onClick={() => setSelectionStart(currentFrameIndex)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  selectionStart === currentFrameIndex
                    ? "bg-green-500 text-white"
                    : "bg-slate-800/80 text-slate-300 hover:bg-slate-700"
                }`}
              >
                Set Start
              </button>
              <button
                onClick={() => setSelectionEnd(currentFrameIndex)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  selectionEnd === currentFrameIndex
                    ? "bg-red-500 text-white"
                    : "bg-slate-800/80 text-slate-300 hover:bg-slate-700"
                }`}
              >
                Set End
              </button>
            </div>

            {/* Floating Controls */}
            <div className="absolute bottom-6 bg-slate-900/80 backdrop-blur-md border border-slate-700/50 rounded-full px-6 py-3 flex items-center gap-6 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 translate-y-2 group-hover:translate-y-0">
              <button
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentFrameIndex((prev) => Math.max(0, prev - 1));
                }}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <i className="fas fa-step-backward"></i>
              </button>

              <button
                onClick={() => {
                  if (
                    !isPlaying &&
                    currentFrameIndex >= result.data.frames.length - 1
                  ) {
                    setCurrentFrameIndex(0);
                  }
                  togglePlay();
                }}
                className="w-12 h-12 rounded-full bg-white text-slate-900 flex items-center justify-center hover:scale-110 active:scale-95 transition-all shadow-lg shadow-white/10"
              >
                <i
                  className={`fas ${isPlaying ? "fa-pause" : "fa-play pl-1"}`}
                ></i>
              </button>

              <button
                onClick={() => {
                  setIsPlaying(false);
                  setCurrentFrameIndex((prev) =>
                    Math.min(result.data.frames.length - 1, prev + 1)
                  );
                }}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <i className="fas fa-step-forward"></i>
              </button>

              <div className="h-6 w-px bg-slate-700 mx-2"></div>

              <div className="text-xs font-mono text-slate-400 min-w-[60px] text-center">
                Frame{" "}
                <span className="text-white font-bold">
                  {currentFrameIndex + 1}
                </span>
                <span className="opacity-50">/{result.data.frames.length}</span>
              </div>
            </div>

            {/* Regeneration Panel */}
            {selectionStart !== null && selectionEnd !== null && (
              <div className="absolute bottom-24 bg-slate-800/90 backdrop-blur border border-purple-500/30 p-4 rounded-xl flex flex-col gap-3 animate-fadeIn min-w-[300px]">
                <div className="flex items-center justify-between">
                  <div className="text-xs text-slate-300">
                    <span className="font-bold text-white">Modify Range:</span>{" "}
                    {Math.min(selectionStart, selectionEnd) + 1} -{" "}
                    {Math.max(selectionStart, selectionEnd) + 1}
                  </div>
                  <button
                    onClick={() => {
                      setSelectionStart(null);
                      setSelectionEnd(null);
                      setRevisionPrompt("");
                    }}
                    className="text-slate-400 hover:text-white"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>

                <input
                  type="text"
                  value={revisionPrompt}
                  onChange={(e) => setRevisionPrompt(e.target.value)}
                  placeholder="Describe changes (optional)..."
                  className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-purple-500 outline-none"
                />

                <button
                  onClick={handleRegenerate}
                  disabled={isRegenerating}
                  className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  {isRegenerating ? (
                    <i className="fas fa-circle-notch fa-spin"></i>
                  ) : (
                    <i className="fas fa-wand-magic-sparkles"></i>
                  )}
                  Regenerate Segment
                </button>
              </div>
            )}
          </div>

          {/* Filmstrip Timeline */}
          <div className="h-[220px] shrink-0 bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col relative">
            <div className="flex justify-between items-center mb-4 px-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                <i className="fas fa-film mr-2"></i>Timeline
              </span>
              <span className="text-[10px] text-slate-500">
                fps: <span className="text-slate-300 font-mono">{fps}</span>
              </span>
            </div>

            <div
              ref={sliderRef}
              className="flex-1 overflow-x-auto flex items-center gap-2 px-[50%] custom-scrollbar pb-2"
              style={{ scrollSnapType: "x mandatory" }}
            >
              {result.data.frames.map((frame: string, idx: number) => {
                const isSelected =
                  selectionStart === idx || selectionEnd === idx;
                const isInRange =
                  selectionStart !== null &&
                  selectionEnd !== null &&
                  idx >= Math.min(selectionStart, selectionEnd) &&
                  idx <= Math.max(selectionStart, selectionEnd);

                return (
                  <div
                    key={idx}
                    onClick={() => {
                      setIsPlaying(false);
                      setCurrentFrameIndex(idx);
                    }}
                    className={`
                            h-[120px] aspect-video shrink-0 rounded-lg overflow-hidden cursor-pointer relative transition-all duration-100 border-[3px] 
                            ${
                              currentFrameIndex === idx
                                ? "border-purple-500 shadow-[0_0_20px_rgba(168,85,247,0.6)] z-10 brightness-110"
                                : isInRange
                                ? "border-yellow-500/50 opacity-100"
                                : "border-slate-800 opacity-60 hover:opacity-100 hover:border-slate-600"
                            }
                        `}
                    style={{ scrollSnapAlign: "center" }}
                  >
                    <img
                      src={frame}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    {isSelected && (
                      <div className="absolute inset-0 border-4 border-yellow-500 z-20 pointer-events-none rounded-lg"></div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 h-4 bg-black/60 text-[8px] text-white flex items-center justify-center font-mono backdrop-blur-[1px]">
                      {idx + 1}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Center Marker Line */}
            <div className="absolute left-1/2 top-[40px] bottom-3 w-px bg-purple-500/50 pointer-events-none z-0"></div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-slate-500 border border-slate-800 border-dashed rounded-2xl bg-slate-900/20">
          <div className="text-center">
            <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-800">
              <i className="fas fa-film text-2xl opacity-50"></i>
            </div>
            <p>
              No content generated yet. Please go back to the Creation step.
            </p>
          </div>
        </div>
      )}
    </div>
  );

  // Export State
  const [isRendering, setIsRendering] = useState(false);
  const [isZipping, setIsZipping] = useState(false);

  const handleExportZip = async () => {
    setIsZipping(true);
    try {
      const zip = new JSZip();
      if (result?.data?.frames) {
        result.data.frames.forEach((frame: string, i: number) => {
          // data:image/jpeg;base64,... -> extract base64, ext
          const parts = frame.split(",");
          const base64Data = parts[1];
          const mime = parts[0].split(":")[1].split(";")[0];
          const ext = mime.split("/")[1];
          zip.file(
            `frame_${i.toString().padStart(3, "0")}.${ext}`,
            base64Data,
            { base64: true }
          );
        });
      }
      const content = await zip.generateAsync({ type: "blob" });
      saveAs(content, `${projectName || "anime_project"}_frames.zip`);
    } catch (e) {
      console.error(e);
      alert("Failed to create ZIP");
    } finally {
      setIsZipping(false);
    }
  };

  const handleExportVideo = async () => {
    if (videoUrl) {
      saveAs(videoUrl, `${projectName || "anime_project"}.webm`);
    } else if (result?.data?.video_data) {
      try {
        const blob = await base64ToBlob(result.data.video_data);
        saveAs(blob, `${projectName || "anime_project"}.webm`);
      } catch (e) {
        console.error("Failed to export video", e);
      }
    }
  };

  const handleRenderVideo = async (): Promise<boolean> => {
    if (!result?.data?.frames) return false;

    // If video is already rendered (videoUrl exists), skip re-rendering
    if (videoUrl) return true;

    setIsRendering(true);
    let success = false;
    try {
      const response = await fetch(`${baseUrl}/render-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName || "project",
          frames: result.data.frames,
          fps: fps,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(
          `Server returned ${response.status}: ${text.slice(0, 100)}`
        );
      }

      const data = await response.json();
      if (data.status === "success" && data.data.video_data) {
        const blob = await base64ToBlob(data.data.video_data);
        const url = URL.createObjectURL(blob);
        setVideoUrl(url);

        setResult((prev: any) => ({
          ...prev,
          data: {
            ...prev.data,
            video_data: data.data.video_data,
          },
        }));
        success = true;
      } else {
        alert("Rendering failed: " + data.message);
      }
    } catch (e: any) {
      console.error(e);
      alert(`Error rendering video: ${e.message}`);
    } finally {
      setIsRendering(false);
    }
    return success;
  };

  const renderStep2 = () => (
    <div className="w-full max-w-6xl animate-fadeIn flex flex-col h-full">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Export Project
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Review your final animation and download the assets.
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => onStepChange(1)}
            className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-sm font-semibold hover:bg-slate-700 transition-colors"
          >
            <i className="fas fa-arrow-left mr-2"></i> Back to Review
          </button>
        </div>
      </div>

      <div className="flex flex-col items-center gap-8 flex-1 min-h-0">
        <div className="flex flex-col gap-4 w-full max-w-4xl">
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center relative overflow-hidden aspect-video shadow-2xl">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider absolute top-4 left-6 z-10">
              <i className="fas fa-video mr-2"></i> Video Preview
            </h3>

            {isRendering ? (
              <div className="flex flex-col items-center gap-4">
                <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                <div className="text-center">
                  <p className="font-bold text-purple-400">
                    Rendering Video...
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Stitching generated frames (OpenCV)
                  </p>
                </div>
              </div>
            ) : videoUrl ? (
              <div className="w-full h-full flex flex-col items-center justify-center pt-8">
                <video
                  src={videoUrl}
                  controls
                  autoPlay
                  loop
                  muted
                  className="w-full h-full object-contain rounded-lg bg-black"
                />
              </div>
            ) : (
              <div className="text-center text-slate-500">
                {result?.data?.frames ? (
                  <>
                    <i className="fas fa-film text-4xl mb-3 text-purple-500"></i>
                    <p className="text-slate-300 mb-2">
                      Frames modified. Video rendering required.
                    </p>
                    <button
                      onClick={handleRenderVideo}
                      className="px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-colors"
                    >
                      <i className="fas fa-gears mr-2"></i> Render Video
                    </button>
                  </>
                ) : (
                  <>
                    <i className="fas fa-exclamation-triangle text-4xl mb-3 opacity-50"></i>
                    <p>Video generation failed.</p>
                    <button
                      onClick={handleExportVideo}
                      className="mt-4 text-purple-400 hover:text-purple-300 underline"
                    >
                      Try Again
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Download Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href={videoUrl || "#"}
              download={
                videoUrl ? `${projectName || "anime_project"}.webm` : undefined
              }
              onClick={(e) => {
                if (!videoUrl || isRendering) e.preventDefault();
              }}
              className={`block w-full py-4 rounded-xl font-bold text-center transition-all ${
                videoUrl && !isRendering
                  ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-900/20 cursor-pointer"
                  : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
              }`}
            >
              {isRendering ? (
                <span>
                  <i className="fas fa-circle-notch fa-spin mr-2"></i>{" "}
                  Loading...
                </span>
              ) : videoUrl ? (
                <span>
                  <i className="fas fa-download mr-2"></i> Download Video (WebM)
                </span>
              ) : (
                <span>
                  <i className="fas fa-video-slash mr-2"></i> Video Not Ready
                </span>
              )}
            </a>

            <button
              onClick={handleExportZip}
              disabled={isZipping || !result?.data?.frames}
              className={`block w-full py-4 rounded-xl font-bold border transition-all text-center flex items-center justify-center gap-2 ${
                !isZipping && result?.data?.frames
                  ? "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700 hover:border-slate-600 cursor-pointer"
                  : "bg-slate-900 text-slate-600 border-slate-800 cursor-not-allowed"
              }`}
            >
              {isZipping ? (
                <>
                  <i className="fas fa-circle-notch fa-spin text-yellow-500"></i>{" "}
                  Packaging...
                </>
              ) : (
                <>
                  <i className="fas fa-file-zipper text-yellow-500"></i>{" "}
                  Download Frames (ZIP)
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-full text-slate-200 font-sans">
      {/* Left Navigation Sidebar */}
      <div className="w-[80px] lg:w-[240px] bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 z-20 shadow-2xl transition-all duration-300">
        <div className="p-6 flex flex-col h-full">
          {/* Nav Title (Desktop) */}
          <div className="hidden lg:block pb-8 border-b border-slate-800/50 mb-6">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest">
              Steps
            </h2>
          </div>

          {/* Steps List */}
          <div className="space-y-2 flex-1">
            {steps.map((step, idx) => (
              <button
                key={idx}
                onClick={() => {
                  // Temporarily allow free navigation
                  onStepChange(idx as any);
                }}
                className={`w-full flex items-center gap-4 px-4 py-4 rounded-xl transition-all duration-200 group relative ${
                  activeStep === idx
                    ? "bg-purple-600/10 text-white"
                    : "text-slate-500 hover:bg-slate-800/50 hover:text-slate-300"
                }`}
              >
                {/* Active Indicator Bar */}
                {activeStep === idx && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-purple-500 rounded-r-full"></div>
                )}

                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center text-lg transition-colors ${
                    activeStep === idx
                      ? "bg-purple-600 text-white shadow-lg shadow-purple-900/30"
                      : "bg-slate-800"
                  }`}
                >
                  <i className={`fas ${step.icon}`}></i>
                </div>
                <div className="hidden lg:block text-left">
                  <div
                    className={`font-bold text-sm ${
                      activeStep === idx ? "text-purple-400" : ""
                    }`}
                  >
                    {step.title}
                  </div>
                  <div className="text-[10px] opacity-70 font-normal">
                    {step.desc}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Status Box */}
          {error && (
            <div className="mt-auto hidden lg:block p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
              <div className="flex items-start gap-3 text-red-400">
                <i className="fas fa-exclamation-circle mt-1"></i>
                <p className="text-xs leading-relaxed">{error}</p>
              </div>
            </div>
          )}

          {loading && (
            <div className="mt-auto hidden lg:block p-4 bg-slate-950/50 border border-slate-800 rounded-xl">
              <div className="flex items-center gap-3 text-purple-400">
                <i className="fas fa-circle-notch fa-spin"></i>
                <p className="text-xs font-bold">Processing...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950 relative overflow-hidden">
        {/* Grid Background */}
        <div
          className="absolute inset-0 opacity-10 pointer-events-none"
          style={{
            backgroundImage:
              "linear-gradient(#334155 1px, transparent 1px), linear-gradient(90deg, #334155 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent pointer-events-none"></div>

        {/* Content Scroll Area */}
        <div className="flex-1 overflow-y-auto relative z-10 flex flex-col p-10 scroll-smooth">
          {/* Step Content Switcher */}
          <div className="flex justify-center w-full min-h-full">
            {activeStep === 0 && renderStep0()}
            {activeStep === 1 && renderStep1()}
            {activeStep === 2 && renderStep2()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimeStudio;
