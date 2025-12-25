import { useState, useEffect, useRef } from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";

interface UseAnimeStudioProps {
  baseUrl: string;
  onStepChange: (step: 0 | 1 | 2) => void;
}

const base64ToBlob = async (base64: string) => {
  const res = await fetch(base64);
  return await res.blob();
};

export const useAnimeStudio = ({
  baseUrl,
  onStepChange,
}: UseAnimeStudioProps) => {
  // 폼 입력 관리
  const [projectName, setProjectName] = useState("");
  const [prompt, setPrompt] = useState("");

  // 파일 및 프리뷰 상태
  const [startFile, setStartFile] = useState<File | null>(null);
  const [endFile, setEndFile] = useState<File | null>(null);
  const [startPreview, setStartPreview] = useState<string | null>(null);
  const [endPreview, setEndPreview] = useState<string | null>(null);

  // 서버 통신 상태
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  // 통합 플레이어 제어
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [fps, setFps] = useState(30);
  const sliderRef = useRef<HTMLDivElement>(null);

  // Revision State
  const [selectionStart, setSelectionStart] = useState<number | null>(null);
  const [selectionEnd, setSelectionEnd] = useState<number | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [revisionPrompt, setRevisionPrompt] = useState("");
  const [validationWarning, setValidationWarning] = useState<string | null>(
    null
  );

  // Export State
  const [isRendering, setIsRendering] = useState(false);
  const [isZipping, setIsZipping] = useState(false);

  // 재생 루프 이펙트
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

  // 타임라인 스크롤 동기화
  useEffect(() => {
    if (sliderRef.current && result?.data?.frames) {
      const scrollContainer = sliderRef.current;
      const frameWidth = 222;
      const targetScroll = currentFrameIndex * frameWidth + frameWidth / 2;

      scrollContainer.scrollTo({
        left: targetScroll,
        behavior: isPlaying ? "auto" : "smooth",
      });
    }
  }, [currentFrameIndex, result, isPlaying]);

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
    setVideoUrl(null);

    try {
      const formData = new FormData();
      formData.append("start_image", startFile);
      formData.append("end_image", endFile);
      formData.append("prompt", prompt);
      formData.append("project_name", projectName);

      const cleanBaseUrl = baseUrl.endsWith("/")
        ? baseUrl.slice(0, -1)
        : baseUrl;
      const endpoint = `${cleanBaseUrl}/generate-video`;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `Error: ${response.status}`);
      }

      setResult(data);
      if (data.data?.frames?.length > 0) {
        setCurrentFrameIndex(0);
      }

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

      onStepChange(1);
    } catch (err: any) {
      setError(err.message || "Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  const handleMockGenerate = () => {
    const dummyFrames = Array.from({ length: 10 }).map((_, i) => {
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
          revision_prompt: revisionPrompt,
          target_frame_count: endIdx - startIdx,
        }),
      });

      const data = await response.json();
      if (data.status === "success") {
        const newFrames = data.data.frames;
        const updatedFrames = [...result.data.frames];
        const before = updatedFrames.slice(0, startIdx + 1);
        const after = updatedFrames.slice(endIdx);
        const finalFrames = [...before, ...newFrames, ...after];

        setResult({
          ...result,
          data: {
            ...result.data,
            frames: finalFrames,
            video_data: null,
          },
        });
        setVideoUrl(null);
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

  const handleRenderVideo = async (): Promise<boolean> => {
    if (!result?.data?.frames) return false;
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

  const handleExportZip = async () => {
    setIsZipping(true);
    try {
      const zip = new JSZip();
      if (result?.data?.frames) {
        result.data.frames.forEach((frame: string, i: number) => {
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

  const togglePlay = () => setIsPlaying(!isPlaying);

  return {
    projectName,
    setProjectName,
    prompt,
    setPrompt,
    startFile,
    endFile,
    startPreview,
    endPreview,
    loading,
    result,
    error,
    videoUrl,
    isPlaying,
    setIsPlaying,
    currentFrameIndex,
    setCurrentFrameIndex,
    fps,
    setFps,
    sliderRef,
    selectionStart,
    setSelectionStart,
    selectionEnd,
    setSelectionEnd,
    isRegenerating,
    revisionPrompt,
    setRevisionPrompt,
    validationWarning,
    setValidationWarning,
    isRendering,
    isZipping,
    handleFileChange,
    handleGenerate,
    handleMockGenerate,
    handleRegenerate,
    handleRenderVideo,
    handleExportZip,
    handleExportVideo,
    togglePlay,
  };
};
