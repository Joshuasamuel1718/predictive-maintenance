import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import GaugeChart from "react-gauge-chart";

function App() {

  const [data, setData] = useState({
    Type: "L",
    air_temp: "",
    process_temp: "",
    rpm: "",
    torque: "",
    tool_wear: ""
  });

  const [result, setResult] = useState("");
  const [probability, setProbability] = useState(0);

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const predict = async () => {
    const payload = {
      "Type": data.Type,  // ✅ send string (encoder will handle)
      "Air temperature [K]": Number(data.air_temp),
      "Process temperature [K]": Number(data.process_temp),
      "Rotational speed [rpm]": Number(data.rpm),
      "Torque [Nm]": Number(data.torque),
      "Tool wear [min]": Number(data.tool_wear)
    };

    const response = await axios.post("http://127.0.0.1:5000/predict", payload);
setResult(response.data.prediction);
setProbability(response.data.probability);
  };

  return (
    <div className="container">

      <h1>Predictive Maintenance Dashboard</h1>

      {/* INPUT */}
      <div className="card">

        <select name="Type" onChange={handleChange}>
          <option value="L">L</option>
          <option value="M">M</option>
          <option value="H">H</option>
        </select>

        <input name="air_temp" placeholder="Air Temp" onChange={handleChange} />
        <input name="process_temp" placeholder="Process Temp" onChange={handleChange} />
        <input name="rpm" placeholder="RPM" onChange={handleChange} />
        <input name="torque" placeholder="Torque" onChange={handleChange} />
        <input name="tool_wear" placeholder="Tool Wear" onChange={handleChange} />

        <button onClick={predict}>Predict</button>
      </div>

      {/* STATUS */}
      <div className="card">
        <h2>Status</h2>
        <h3>{result}</h3>
      </div>

      {/* GAUGE */}
      <div className="card">
        <h2>Failure Probability</h2>
        <GaugeChart id="gauge" percent={probability} />
      </div>

    </div>
  );
}

export default App;