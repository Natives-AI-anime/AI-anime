import React from "react";
import { useAnimeStudio } from "../hooks/useAnimeStudio";
import CreationStep from "./studio/CreationStep";
import ReviewStep from "./studio/ReviewStep";
import ExportStep from "./studio/ExportStep";

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
  const {
    projectName,
    setProjectName,
    prompt,
    setPrompt,
    startPreview,
    endPreview,
    loading,
    result,
    videoUrl,
    isPlaying,
    setIsPlaying,
    currentFrameIndex,
    setCurrentFrameIndex,
    fps,
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
  } = useAnimeStudio({ baseUrl, onStepChange });

  const steps = [
    { title: "Creation", icon: "fa-pencil-alt", desc: "Setup Generation" },
    { title: "Review", icon: "fa-eye", desc: "Check & Modify" },
    { title: "Export", icon: "fa-download", desc: "Save Results" },
  ];

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

          <div className="flex flex-col gap-6">
            {steps.map((step, idx) => (
              <div
                key={idx}
                className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-300 ${
                  activeStep === idx
                    ? "bg-purple-600/10 border border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.2)]"
                    : "opacity-50 hover:opacity-80 hover:bg-slate-800/50"
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-all ${
                    activeStep === idx
                      ? "bg-gradient-to-br from-purple-500 to-indigo-600 text-white shadow-lg"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  <i className={`fas ${step.icon} text-lg`}></i>
                </div>
                <div className="hidden lg:block overflow-hidden">
                  <h3
                    className={`font-bold text-sm ${
                      activeStep === idx ? "text-white" : "text-slate-400"
                    }`}
                  >
                    {step.title}
                  </h3>
                  <p className="text-[10px] text-slate-500 truncate">
                    {step.desc}
                  </p>
                </div>
                {activeStep === idx && (
                  <div className="ml-auto w-1 h-8 bg-purple-500 rounded-full hidden lg:block shadow-[0_0_10px_rgba(168,85,247,0.8)]"></div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-auto pt-8 border-t border-slate-800/50 hidden lg:block">
            <div className="flex items-center gap-3 opacity-60 hover:opacity-100 transition-opacity cursor-pointer">
              <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                <i className="fas fa-cog text-slate-400"></i>
              </div>
              <span className="text-xs font-bold text-slate-400">Settings</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-w-0 bg-slate-950 relative flex flex-col h-full overflow-hidden">
        {/* Top Header / Breadcrumb */}
        <div className="h-16 border-b border-slate-900 bg-slate-950/80 backdrop-blur-sm flex items-center px-8 justify-between shrink-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-slate-500 text-sm font-medium">Project</span>
            <i className="fas fa-chevron-right text-[10px] text-slate-700"></i>
            <span className="text-white text-sm font-bold">
              {projectName || "New Animation"}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-3 py-1 bg-slate-900 rounded-full border border-slate-800 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                System Ready
              </span>
            </div>
          </div>
        </div>

        {/* Content Scroll Area */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-8 custom-scrollbar">
          <div className="max-w-[1600px] mx-auto h-full flex flex-col items-center">
            {activeStep === 0 && (
              <CreationStep
                startPreview={startPreview}
                endPreview={endPreview}
                projectName={projectName}
                prompt={prompt}
                loading={loading}
                onFileChange={handleFileChange}
                setProjectName={setProjectName}
                setPrompt={setPrompt}
                onGenerate={handleGenerate}
                onMockGenerate={handleMockGenerate}
              />
            )}

            {activeStep === 1 && (
              <ReviewStep
                currentFrameIndex={currentFrameIndex}
                result={result}
                onStepChange={onStepChange}
                isRendering={isRendering}
                onRenderVideo={handleRenderVideo}
                isPlaying={isPlaying}
                togglePlay={togglePlay}
                selectionStart={selectionStart}
                setSelectionStart={setSelectionStart}
                selectionEnd={selectionEnd}
                setSelectionEnd={setSelectionEnd}
                validationWarning={validationWarning}
                setValidationWarning={setValidationWarning}
                setIsPlaying={setIsPlaying}
                setCurrentFrameIndex={setCurrentFrameIndex}
                revisionPrompt={revisionPrompt}
                setRevisionPrompt={setRevisionPrompt}
                onRegenerate={handleRegenerate}
                isRegenerating={isRegenerating}
                sliderRef={sliderRef}
                fps={fps}
              />
            )}

            {activeStep === 2 && (
              <ExportStep
                projectName={projectName}
                result={result}
                videoUrl={videoUrl}
                isRendering={isRendering}
                isZipping={isZipping}
                onStepChange={onStepChange}
                onRenderVideo={handleRenderVideo}
                onExportVideo={handleExportVideo}
                onExportZip={handleExportZip}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnimeStudio;
