import React, { useState } from "react";
import AnimeStudio from "./components/AnimeStudio";

const App: React.FC = () => {
  // Default connection URL for the Anime Service
  const [serviceBaseUrl, setServiceBaseUrl] = useState(
    import.meta.env.VITE_API_URL || "http://140.245.72.199:8000"
  );
  const [step, setStep] = useState<0 | 1 | 2>(0);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans selection:bg-purple-500/30">
      {/* Background Gradient Mesh (Visual Flair) */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[120px]"></div>
      </div>

      <main className="flex-1 flex flex-col min-w-0 z-10 relative">
        {/* Minimal Header */}
        <header className="h-14 border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-md flex items-center px-6 justify-between shrink-0">
          <div
            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => setStep(0)}
          >
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-purple-900/30">
              <i className="fas fa-dragon text-white text-xs"></i>
            </div>
            <h1 className="font-bold text-lg tracking-tight text-white">
              AniGen <span className="text-slate-500 font-normal">Studio</span>
            </h1>
          </div>
        </header>

        {/* Main Workspace */}
        <div className="flex-1 overflow-hidden">
          <AnimeStudio
            baseUrl={serviceBaseUrl}
            activeStep={step}
            onStepChange={setStep}
          />
        </div>
      </main>
    </div>
  );
};

export default App;
