import React from "react";

interface ReviewStepProps {
  currentFrameIndex: number;
  result: any;
  onStepChange: (step: 0 | 1 | 2) => void;
  isRendering: boolean;
  onRenderVideo: () => Promise<boolean>;
  isPlaying: boolean;
  togglePlay: () => void;
  selectionStart: number | null;
  setSelectionStart: (index: number | null) => void;
  selectionEnd: number | null;
  setSelectionEnd: (index: number | null) => void;
  validationWarning: string | null;
  setValidationWarning: (msg: string | null) => void;
  setIsPlaying: (playing: boolean) => void;
  setCurrentFrameIndex: (index: number | ((prev: number) => number)) => void;
  revisionPrompt: string;
  setRevisionPrompt: (prompt: string) => void;
  onRegenerate: () => void;
  isRegenerating: boolean;
  sliderRef: React.RefObject<HTMLDivElement | null>;
  fps: number;
}

const ReviewStep: React.FC<ReviewStepProps> = ({
  currentFrameIndex,
  result,
  onStepChange,
  isRendering,
  onRenderVideo,
  isPlaying,
  togglePlay,
  selectionStart,
  setSelectionStart,
  selectionEnd,
  setSelectionEnd,
  validationWarning,
  setValidationWarning,
  setIsPlaying,
  setCurrentFrameIndex,
  revisionPrompt,
  setRevisionPrompt,
  onRegenerate,
  isRegenerating,
  sliderRef,
  fps,
}) => {
  return (
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
              const success = await onRenderVideo();
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
                onClick={() => {
                  if (
                    selectionEnd !== null &&
                    currentFrameIndex >= selectionEnd
                  ) {
                    setValidationWarning(
                      "Start frame must be before End frame."
                    );
                  } else {
                    setSelectionStart(currentFrameIndex);
                    setValidationWarning(null);
                  }
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  selectionStart === currentFrameIndex
                    ? "bg-green-500 text-white"
                    : "bg-slate-800/80 text-slate-300 hover:bg-slate-700"
                }`}
              >
                Set Start
              </button>
              <button
                onClick={() => {
                  if (
                    selectionStart !== null &&
                    currentFrameIndex <= selectionStart
                  ) {
                    setValidationWarning(
                      "End frame must be after Start frame."
                    );
                  } else {
                    setSelectionEnd(currentFrameIndex);
                    setValidationWarning(null);
                  }
                }}
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

            {/* Regeneration Panel (Moved outside) */}
          </div>

          {/* Regeneration Panel Block */}
          {(selectionStart !== null || selectionEnd !== null) && (
            <div className="w-full bg-slate-900/50 border border-slate-800 rounded-xl p-4 flex flex-col gap-3 animate-fadeIn shrink-0">
              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-300 flex items-center gap-2">
                  <i className="fas fa-sliders-h text-purple-500"></i>
                  <span className="font-bold text-white">Modify Range:</span>

                  {/* Start Frame Badge */}
                  <div className="relative group">
                    <button
                      onClick={() =>
                        selectionStart !== null &&
                        setCurrentFrameIndex(selectionStart)
                      }
                      className={`bg-slate-800 px-2 py-0.5 rounded text-xs font-mono border border-slate-700 transition-colors ${
                        selectionStart !== null
                          ? "hover:bg-slate-700 cursor-pointer text-green-400"
                          : "text-slate-500 cursor-default"
                      }`}
                    >
                      frame {selectionStart !== null ? selectionStart + 1 : "?"}
                    </button>
                    {selectionStart !== null && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectionStart(null);
                          setValidationWarning(null);
                        }}
                        className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm z-10"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    )}
                  </div>

                  <i className="fas fa-arrow-right text-xs text-slate-600"></i>

                  {/* End Frame Badge */}
                  <div className="relative group">
                    <button
                      onClick={() =>
                        selectionEnd !== null &&
                        setCurrentFrameIndex(selectionEnd)
                      }
                      className={`bg-slate-800 px-2 py-0.5 rounded text-xs font-mono border border-slate-700 transition-colors ${
                        selectionEnd !== null
                          ? "hover:bg-slate-700 cursor-pointer text-red-400"
                          : "text-slate-500 cursor-default"
                      }`}
                    >
                      frame {selectionEnd !== null ? selectionEnd + 1 : "?"}
                    </button>
                    {selectionEnd !== null && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectionEnd(null);
                          setValidationWarning(null);
                        }}
                        className="absolute -top-2 -right-2 w-4 h-4 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-sm z-10"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectionStart(null);
                    setSelectionEnd(null);
                    setRevisionPrompt("");
                    setValidationWarning(null);
                  }}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>

              <div className="flex gap-3">
                <input
                  type="text"
                  value={revisionPrompt}
                  onChange={(e) => setRevisionPrompt(e.target.value)}
                  placeholder="Describe changes (e.g. 'Slow motion', 'Fix face')..."
                  className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder-slate-500 focus:border-purple-500 outline-none shadow-inner"
                />

                <button
                  onClick={onRegenerate}
                  disabled={
                    isRegenerating ||
                    selectionStart === null ||
                    selectionEnd === null
                  }
                  className={`px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-bold rounded-lg transition-colors flex items-center justify-center gap-2 ${
                    isRegenerating ||
                    selectionStart === null ||
                    selectionEnd === null
                      ? "opacity-50 cursor-not-allowed"
                      : ""
                  }`}
                >
                  {isRegenerating ? (
                    <i className="fas fa-circle-notch fa-spin"></i>
                  ) : (
                    <i className="fas fa-wand-magic-sparkles"></i>
                  )}
                  Regenerate
                </button>
              </div>
              {/* Helper text / Validation Warning */}
              {validationWarning ? (
                <div className="text-[11px] text-amber-400 flex items-center gap-2 pl-1 font-bold animate-pulse">
                  <i className="fas fa-exclamation-triangle"></i>
                  {validationWarning}
                </div>
              ) : selectionStart === null || selectionEnd === null ? (
                <div className="text-[11px] text-slate-400 flex items-center gap-2 pl-1">
                  <i className="fas fa-info-circle text-slate-500"></i>
                  Select both Start and End frames to enable regeneration.
                </div>
              ) : null}
            </div>
          )}

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
              style={{ scrollBehavior: isPlaying ? "auto" : "smooth" }}
              onWheel={(e) => {
                if (sliderRef.current) {
                  // 휠(Y) 또는 터치패드(X) 입력을 모두 수평 스크롤로 변환
                  // 세로 스크롤(휠) 속도를 5배 빠르게 조정
                  sliderRef.current.scrollLeft += e.deltaY * 5 + e.deltaX;
                }
              }}
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
                                ? "border-indigo-500/30 opacity-100"
                                : "border-slate-800 opacity-60 hover:opacity-100 hover:border-slate-600"
                            }
                        `}
                  >
                    <img
                      src={frame}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    {isSelected && (
                      <div className="absolute inset-0 border-4 border-indigo-400 z-20 pointer-events-none rounded-lg"></div>
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
};

export default ReviewStep;
