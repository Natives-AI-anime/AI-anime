import React, { useState, useRef, useEffect } from "react";

interface AnimeStudioProps {
  baseUrl: string;
}

interface Frame {
  url: string;
  path: string; // The relative path needed for export API
}

interface ProjectData {
  projectName: string;
  prompt: string;
  frameCount: number;
}

const AnimeStudio: React.FC<AnimeStudioProps> = ({ baseUrl }) => {
  const [activeTab, setActiveTab] = useState<"create" | "review" | "download">(
    "create"
  );
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  // Create Tab State
  const [projectName, setProjectName] = useState("my_anime_project");
  const [prompt, setPrompt] = useState(
    "Two samurai fighting under cherry blossoms, cinematic lighting, anime style"
  );
  const [startImage, setStartImage] = useState<File | null>(null);
  const [endImage, setEndImage] = useState<File | null>(null);
  const [startPreview, setStartPreview] = useState<string | null>(null);
  const [endPreview, setEndPreview] = useState<string | null>(null);

  // Review/Download State
  const [frames, setFrames] = useState<Frame[]>([]);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const playIntervalRef = useRef<number | null>(null);

  // Result URLs
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [zipUrl, setZipUrl] = useState<string | null>(null);

  // Handle Image Selection
  const handleImageChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "start" | "end"
  ) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (type === "start") {
        setStartImage(file);
        setStartPreview(URL.createObjectURL(file));
      } else {
        setEndImage(file);
        setEndPreview(URL.createObjectURL(file));
      }
    }
  };

  // 1. Generate Video
  const handleGenerate = async () => {
    if (!startImage || !endImage) {
      alert("Please select both start and end images.");
      return;
    }

    setLoading(true);
    setStatusMessage("Generating animation frames... This might take a while.");

    try {
      const formData = new FormData();
      formData.append("start_image", startImage);
      formData.append("end_image", endImage);
      formData.append("prompt", prompt);
      formData.append("project_name", projectName);

      const response = await fetch(`${baseUrl}/generate-video`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.status === "success") {
        // Parse frames. The API returns full URLs.
        // We need to extract the path relative to server root for export APIs.
        // URL: http://localhost:8000/generated_frames/proj/frame.jpg
        // Path needed: generated_frames/proj/frame.jpg

        const newFrames: Frame[] = data.data.frames.map((url: string) => {
          // Extract part after host
          const urlObj = new URL(url);
          const path = urlObj.pathname.substring(1); // remove leading slash
          return { url, path };
        });

        setFrames(newFrames);
        setActiveTab("review");
        setStatusMessage("Generation complete!");
      } else {
        setStatusMessage(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error(error);
      setStatusMessage("Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  // Video Preview Logic
  useEffect(() => {
    if (isPlaying) {
      playIntervalRef.current = window.setInterval(() => {
        setCurrentFrameIndex((prev) => (prev + 1) % frames.length);
      }, 1000 / 15); // Preview at ~15fps
    } else {
      if (playIntervalRef.current) {
        clearInterval(playIntervalRef.current);
      }
    }
    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, [isPlaying, frames.length]);

  // 2. Export Video
  const handleExportVideo = async () => {
    setLoading(true);
    setStatusMessage("Rendering video...");
    try {
      const response = await fetch(`${baseUrl}/export-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName,
          frame_paths: frames.map((f) => f.path),
          fps: 15,
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        setVideoUrl(data.data.video_url);
      } else {
        alert("Export failed: " + data.message);
      }
    } catch (e) {
      alert("Error processing export request");
    } finally {
      setLoading(false);
    }
  };

  // 3. Export ZIP
  const handleExportZip = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${baseUrl}/export-frames`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName,
          frame_paths: frames.map((f) => f.path),
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        setZipUrl(data.data.zip_url);
      } else {
        alert("Export failed: " + data.message);
      }
    } catch (e) {
      alert("Error processing export request");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col p-6 max-w-6xl mx-auto">
      {/* Tabs */}
      <div className="flex gap-4 mb-8 border-b border-slate-700/50 pb-1">
        {(["create", "review", "download"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => {
              if (tab === "review" && frames.length === 0) return;
              if (tab === "download" && frames.length === 0) return;
              setActiveTab(tab);
            }}
            className={`px-4 py-2 text-sm font-medium transition-colors relative
              ${
                activeTab === tab
                  ? "text-primary-500"
                  : frames.length === 0 &&
                    (tab === "review" || tab === "download")
                  ? "text-slate-600 cursor-not-allowed"
                  : "text-slate-400 hover:text-slate-300"
              }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
            {activeTab === tab && (
              <div className="absolute bottom-[-5px] left-0 w-full h-0.5 bg-primary-500 rounded-full"></div>
            )}
          </button>
        ))}
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center backdrop-blur-sm">
          <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-200">{statusMessage}</p>
          </div>
        </div>
      )}

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {/* CREATE TAB */}
        {activeTab === "create" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in">
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-400">
                  Project Name
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-primary-500"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-400">
                  Prompt / Scenario
                </label>
                <textarea
                  rows={4}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-primary-500 resize-none"
                />
              </div>

              <button
                onClick={handleGenerate}
                className="w-full bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-500 hover:to-indigo-500 text-white font-bold py-3 rounded-lg shadow-lg shadow-primary-900/20 transition-all active:scale-[0.98]"
              >
                <i className="fas fa-magic mr-2"></i> Generate Animation
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Start Image Upload */}
              <div className="aspect-square bg-slate-900/50 border-2 border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center relative hover:border-slate-500 transition-colors group overflow-hidden">
                {startPreview ? (
                  <>
                    <img
                      src={startPreview}
                      alt="Start"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                      <p className="text-white text-sm">Change Start Image</p>
                    </div>
                  </>
                ) : (
                  <div className="text-center p-4">
                    <i className="fas fa-image text-3xl text-slate-600 mb-2"></i>
                    <p className="text-sm text-slate-500">Start Frame</p>
                  </div>
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageChange(e, "start")}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
              </div>

              {/* End Image Upload */}
              <div className="aspect-square bg-slate-900/50 border-2 border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center relative hover:border-slate-500 transition-colors group overflow-hidden">
                {endPreview ? (
                  <>
                    <img
                      src={endPreview}
                      alt="End"
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                      <p className="text-white text-sm">Change End Image</p>
                    </div>
                  </>
                ) : (
                  <div className="text-center p-4">
                    <i className="fas fa-flag-checkered text-3xl text-slate-600 mb-2"></i>
                    <p className="text-sm text-slate-500">End Frame</p>
                  </div>
                )}
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageChange(e, "end")}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
              </div>
            </div>
          </div>
        )}

        {/* REVIEW TAB */}
        {activeTab === "review" && frames.length > 0 && (
          <div className="flex flex-col h-full gap-6">
            <div className="flex-1 flex items-center justify-center bg-black/40 rounded-xl border border-slate-800 p-4 relative">
              <img
                src={frames[currentFrameIndex].url}
                alt={`Frame ${currentFrameIndex}`}
                className="max-h-full max-w-full object-contain rounded shadow-2xl"
              />
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-slate-900/80 backdrop-blur px-6 py-2 rounded-full border border-slate-700">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="hover:text-primary-400 transition-colors"
                >
                  <i
                    className={`fas ${isPlaying ? "fa-pause" : "fa-play"}`}
                  ></i>
                </button>
                <span className="text-xs font-mono text-slate-400">
                  {currentFrameIndex + 1} / {frames.length}
                </span>
                <input
                  type="range"
                  min="0"
                  max={frames.length - 1}
                  value={currentFrameIndex}
                  onChange={(e) =>
                    setCurrentFrameIndex(parseInt(e.target.value))
                  }
                  className="w-48 accent-primary-500 h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setActiveTab("create")}
                className="px-4 py-2 rounded-lg text-slate-400 hover:bg-slate-800 transition-colors"
              >
                Back to Edit
              </button>
              <button
                onClick={() => setActiveTab("download")}
                className="px-6 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-medium shadow-lg shadow-primary-900/20 transition-all"
              >
                Proceed to Download{" "}
                <i className="fas fa-arrow-right ml-2 text-xs"></i>
              </button>
            </div>
          </div>
        )}

        {/* DOWNLOAD TAB */}
        {activeTab === "download" && frames.length > 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-green-500/10 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/20">
                <i className="fas fa-check text-4xl"></i>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Project Ready!
              </h2>
              <p className="text-slate-400">
                Your animation frames have been generated successfully.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl">
              <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl flex flex-col gap-4 hover:border-slate-600 transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
                    <i className="fas fa-film"></i>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200">Video File</h3>
                    <p className="text-xs text-slate-500">MP4 Format</p>
                  </div>
                </div>
                {videoUrl ? (
                  <a
                    href={videoUrl}
                    download
                    className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white text-center rounded-lg font-medium transition-colors"
                  >
                    Download MP4
                  </a>
                ) : (
                  <button
                    onClick={handleExportVideo}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium transition-colors"
                  >
                    Generate MP4
                  </button>
                )}
              </div>

              <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl flex flex-col gap-4 hover:border-slate-600 transition-colors">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 rounded-lg bg-yellow-500/20 text-yellow-400 flex items-center justify-center">
                    <i className="fas fa-images"></i>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-200">Frame Sequence</h3>
                    <p className="text-xs text-slate-500">ZIP Archive</p>
                  </div>
                </div>
                {zipUrl ? (
                  <a
                    href={zipUrl}
                    download
                    className="w-full py-2 bg-yellow-600 hover:bg-yellow-500 text-white text-center rounded-lg font-medium transition-colors"
                  >
                    Download ZIP
                  </a>
                ) : (
                  <button
                    onClick={handleExportZip}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium transition-colors"
                  >
                    Generate ZIP
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnimeStudio;
