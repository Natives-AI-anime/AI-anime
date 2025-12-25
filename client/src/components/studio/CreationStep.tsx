import React from "react";

interface CreationStepProps {
  startPreview: string | null;
  endPreview: string | null;
  projectName: string;
  prompt: string;
  loading: boolean;
  onFileChange: (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "start" | "end"
  ) => void;
  setProjectName: (value: string) => void;
  setPrompt: (value: string) => void;
  onGenerate: () => void;
  onMockGenerate: () => void;
}

const CreationStep: React.FC<CreationStepProps> = ({
  startPreview,
  endPreview,
  projectName,
  prompt,
  loading,
  onFileChange,
  setProjectName,
  setPrompt,
  onGenerate,
  onMockGenerate,
}) => {
  return (
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
              onChange={(e) => onFileChange(e, "start")}
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
              onChange={(e) => onFileChange(e, "end")}
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

      {/* Configuration Form */}
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
            onClick={onMockGenerate}
            className="px-6 py-3 rounded-xl bg-slate-800 text-slate-400 font-bold text-sm hover:bg-slate-700 hover:text-white transition-colors border border-slate-700"
          >
            <i className="fas fa-bug mr-2"></i> Debug: Mock Data
          </button>
          <button
            onClick={onGenerate}
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
};

export default CreationStep;
