import React from "react";

interface ExportStepProps {
  projectName: string;
  result: any;
  videoUrl: string | null;
  isRendering: boolean;
  isZipping: boolean;
  onStepChange: (step: 0 | 1 | 2) => void;
  onRenderVideo: () => void;
  onExportVideo: () => void;
  onExportZip: () => void;
}

const ExportStep: React.FC<ExportStepProps> = ({
  projectName,
  result,
  videoUrl,
  isRendering,
  isZipping,
  onStepChange,
  onRenderVideo,
  onExportVideo,
  onExportZip,
}) => {
  return (
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
                      onClick={onRenderVideo}
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
                      onClick={onExportVideo}
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
              onClick={onExportZip}
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
};

export default ExportStep;
