import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import GaugeChart from "react-gauge-chart";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [isLoginScreen, setIsLoginScreen] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const [data, setData] = useState({
    Type: "L",
    air_temp: "",
    process_temp: "",
    rpm: "",
    torque: "",
    tool_wear: ""
  });

  const [result, setResult] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [loading, setLoading] = useState(false);

  // Login handler
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");
    setLoading(true);
    try {
      const response = await axios.post("/login", {
        username,
        password
      });
      const accessToken = response.data.access_token;
      setToken(accessToken);
      localStorage.setItem("token", accessToken);
    } catch (error) {
      setLoginError("Invalid credentials or server unavailable.");
    } finally {
      setLoading(false);
    }
  };

  // Signup handler
  const handleSignup = async (e) => {
    e.preventDefault();
    setLoginError("");
    setLoading(true);
    try {
      const response = await axios.post("/signup", {
        username,
        password
      });
      const accessToken = response.data.access_token;
      setToken(accessToken);
      localStorage.setItem("token", accessToken);
    } catch (error) {
      if (error.response && error.response.data && error.response.data.msg) {
        setLoginError(error.response.data.msg);
      } else {
        setLoginError("Could not connect. Ensure server is running.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("token");
    setResult(null);
  };

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const predict = async () => {
    setLoading(true);
    setResult(null);
    try {
      const payload = {
        "Type": data.Type,
        "Air temperature K": Number(data.air_temp),
        "Process temperature K": Number(data.process_temp),
        "Rotational speed rpm": Number(data.rpm),
        "Torque Nm": Number(data.torque),
        "Tool wear min": Number(data.tool_wear)
      };

      const response = await axios.post("/predict", payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.error) {
        alert("Backend error: " + response.data.error);
        return;
      }

      setResult(response.data);
      setConfidence(response.data.confidence);

    } catch (error) {
      if (error.response && (error.response.status === 401 || error.response.status === 422)) {
        alert("Session expired or malformed. Please log in again.");
        handleLogout();
      } else {
        console.error("Error:", error);
        alert("Could not connect to backend! Make sure Flask is running.");
      }
    } finally {
      setLoading(false);
    }
  };

  // If there's no token, show login screen
  if (!token) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h1>⚙️ Predictive Maintenance</h1>
          <p>{isLoginScreen ? "Please log in to continue" : "Create a new account"}</p>
          {loginError && <p className="error-text">{loginError}</p>}
          <form onSubmit={isLoginScreen ? handleLogin : handleSignup} className="login-form">
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                placeholder="Enter username"
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Enter password"
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading 
                 ? (isLoginScreen ? "Authenticating..." : "Registering...") 
                 : (isLoginScreen ? "Login" : "Sign Up")}
            </button>
          </form>
          <div className="toggle-auth">
             {isLoginScreen ? (
                 <p>Don't have an account? <span onClick={() => setIsLoginScreen(false)}>Sign Up</span></p>
             ) : (
                 <p>Already have an account? <span onClick={() => setIsLoginScreen(true)}>Log in</span></p>
             )}
          </div>
        </div>
      </div>
    );
  }

  // If token exists, show the main dashboard
  return (
    <div className="container">
      <div className="header-row">
        <h1>⚙️ Predictive Maintenance Dashboard</h1>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </div>

      {/* INPUT SECTION */}
      <div className="card">
        <h2>Enter Machine Data</h2>
        <div className="form-grid">
          <div className="form-group">
            <label>Machine Type</label>
            <select name="Type" onChange={handleChange}>
              <option value="L">Low (L)</option>
              <option value="M">Medium (M)</option>
              <option value="H">High (H)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Air Temperature (K)</label>
            <input name="air_temp" type="number" placeholder="e.g. 298.1" onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Process Temperature (K)</label>
            <input name="process_temp" type="number" placeholder="e.g. 308.6" onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Rotational Speed (rpm)</label>
            <input name="rpm" type="number" placeholder="e.g. 1551" onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Torque (Nm)</label>
            <input name="torque" type="number" placeholder="e.g. 42.8" onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Tool Wear (min)</label>
            <input name="tool_wear" type="number" placeholder="e.g. 0" onChange={handleChange} />
          </div>
        </div>
        <button onClick={predict} disabled={loading}>
          {loading ? "Predicting..." : "Predict"}
        </button>
      </div>

      {/* RESULT SECTION */}
      {result && (
        <div className={`card result-card ${result.failure_detected ? "failure" : "normal"}`}>
          <h2>Prediction Result</h2>
          <h3 className="failure-type">{result.failure_type}</h3>
          <p className="status-text">
            {result.failure_detected
              ? "⚠️ Failure Detected — Immediate Attention Required!"
              : "✅ Machine Operating Normally"}
          </p>
        </div>
      )}

      {/* GAUGE SECTION */}
      <div className="card">
        <h2>Confidence Level</h2>
        <GaugeChart
          id="gauge"
          percent={confidence}
          nrOfLevels={20}
          arcPadding={0.02}
          needleColor="#94a3b8"
          textColor="#ffffff"
          colors={["#22c55e", "#facc15", "#ef4444"]}
        />
        <p className="confidence-text">{(confidence * 100).toFixed(2)}%</p>
      </div>
    </div>
  );
}

export default App;