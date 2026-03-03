import { useState } from "react";

function App() {
  const [status, setStatus] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-10">
      
      <h1 className="text-4xl font-bold text-center mb-10">
        Animal Crossing Detection Dashboard
      </h1>

      <div className="flex justify-center mb-8">
        <button
          onClick={() => setStatus(!status)}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-xl transition duration-300 shadow-lg"
        >
          Toggle Detection
        </button>
      </div>

      <div className="flex justify-center">
        <div
          className={`w-96 p-10 rounded-3xl text-center transition-all duration-500 shadow-2xl ${
            status
              ? "bg-red-600 shadow-red-500/40"
              : "bg-green-600 shadow-green-500/40"
          }`}
        >
          <h2 className="text-2xl font-semibold">
            {status ? "🚨 Animal Detected" : "✅ Safe Zone"}
          </h2>
        </div>
      </div>

    </div>
  );
}

export default App;