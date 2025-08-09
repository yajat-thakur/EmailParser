import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

function App() {
  const [bank, setBank] = useState("");
  const [fileName, setFileName] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const supportedBanks = ["HDFC", "AXIS", "SBI", "ICICI", "KOTAK", "IBL", "YES"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setResult(null);
    setIsLoading(true);

    if (!bank || !fileName) {
      setError("❌ Please select a bank and enter file name.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/document-parser?bank=${bank}&statement_type=credit_card&file_name=${fileName}`
      );
      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "❌ Something went wrong");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("❌ Failed to connect to backend");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      className="container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <motion.div
        className="card"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.h1
          className="title"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.4 }}
        >
          💳 Statement Lookup
        </motion.h1>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>🏦 Select Bank:</label>
            <select value={bank} onChange={(e) => setBank(e.target.value)}>
              <option value="">-- Select Bank --</option>
              {supportedBanks.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>📄 Enter File Name:</label>
            <input
              type="text"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              placeholder="example: icici.pdf (small letters)"
            />
          </div>

          <motion.button
            type="submit"
            className="submit-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading}
          >
            {isLoading ? "⏳ Processing..." : "🚀 Fetch Statement"}
          </motion.button>
        </form>

        <AnimatePresence>
          {error && (
            <motion.div
              className="error"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {result && (
            <motion.div
              className="result"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.3 }}
            >
              <motion.h2
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.3 }}
              >
                ✅ Parsed Statement Details
              </motion.h2>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}

export default App;
