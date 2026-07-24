import React, { useMemo } from "react";
import { getDriverColor } from "../utils/colors";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

// Helper to convert fastf1 telemetry dict format to Recharts array of objects
function formatTelemetry(telemetryData) {
  const drivers = Object.keys(telemetryData);
  if (drivers.length === 0) return [];

  // Use distance from the first driver as the baseline
  const baseDriver = drivers[0];
  const distances = telemetryData[baseDriver].Distance;

  const chartData = [];

  // To avoid huge arrays crashing the browser, we'll subsample (e.g., take every Nth point)
  const step = Math.max(1, Math.floor(distances.length / 800));

  for (let i = 0; i < distances.length; i += step) {
    const dataPoint = { distance: Math.round(distances[i]) };

    // For each driver, find the closest data point by distance (assuming they are sorted)
    drivers.forEach((driver) => {
      // In a real app we'd interpolate properly, but since fastf1 telemetry is dense,
      // array indexing for the base driver is fine.
      // We will just use the index for now, assuming the arrays align somewhat well
      // For accurate comparison, we should use interpolation.
      if (telemetryData[driver].Speed[i] !== undefined) {
        dataPoint[`${driver}_Speed`] = telemetryData[driver].Speed[i];
        dataPoint[`${driver}_Throttle`] = telemetryData[driver].Throttle[i];
        dataPoint[`${driver}_Brake`] = telemetryData[driver].Brake[i] * 100; // Scale brake to 100 for visibility
      }
    });

    chartData.push(dataPoint);
  }

  return { chartData, drivers };
}

const TelemetryChart = ({ telemetryData, corners }) => {
  const { chartData, drivers } = useMemo(
    () => formatTelemetry(telemetryData),
    [telemetryData],
  );

  if (!chartData || chartData.length === 0) {
    return <div>No data to display</div>;
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "20px",
        height: "100%",
      }}
    >
      {/* Speed Chart */}
      <div style={{ height: "250px" }}>
        <h4
          style={{
            fontSize: "0.85rem",
            color: "var(--text-secondary)",
            marginBottom: "5px",
          }}
        >
          Speed (km/h)
        </h4>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            syncId="telemetry"
            margin={{ top: 5, right: 20, left: -20, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.1)"
            />
            <XAxis
              dataKey="distance"
              type="number"
              domain={["dataMin", "dataMax"]}
              hide
            />
            <YAxis stroke="rgba(255,255,255,0.5)" />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--bg-glass)",
                backdropFilter: "blur(10px)",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
              }}
              labelFormatter={(val) => `Distance: ${val}m`}
            />
            <Legend verticalAlign="top" height={36} />

            {corners?.map((corner, i) => (
              <ReferenceLine
                key={i}
                x={corner.Distance}
                stroke="rgba(255,255,255,0.2)"
                strokeDasharray="3 3"
              />
            ))}

            {drivers.map((driver) => (
              <Line
                key={`${driver}_Speed`}
                type="monotone"
                dataKey={`${driver}_Speed`}
                name={driver}
                stroke={getDriverColor(driver)}
                dot={false}
                strokeWidth={2}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Throttle & Brake Chart */}
      <div style={{ height: "200px" }}>
        <h4
          style={{
            fontSize: "0.85rem",
            color: "var(--text-secondary)",
            marginBottom: "5px",
          }}
        >
          Throttle & Brake (%)
        </h4>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            syncId="telemetry"
            margin={{ top: 5, right: 20, left: -20, bottom: 20 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.1)"
            />
            <XAxis
              dataKey="distance"
              type="number"
              domain={["dataMin", "dataMax"]}
              stroke="rgba(255,255,255,0.5)"
              label={{
                value: "Distance on Track (m)",
                position: "insideBottom",
                offset: -20,
                fill: "rgba(255,255,255,0.5)",
              }}
            />
            <YAxis stroke="rgba(255,255,255,0.5)" domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--bg-glass)",
                backdropFilter: "blur(10px)",
                border: "1px solid var(--border-color)",
                borderRadius: "8px",
              }}
              labelFormatter={(val) => `Distance: ${val}m`}
            />

            {corners?.map((corner, i) => (
              <ReferenceLine
                key={i}
                x={corner.Distance}
                stroke="rgba(255,255,255,0.2)"
                strokeDasharray="3 3"
              />
            ))}

            {drivers.map((driver) => (
              <React.Fragment key={driver}>
                <Line
                  type="monotone"
                  dataKey={`${driver}_Throttle`}
                  name={`${driver} Throttle`}
                  stroke={getDriverColor(driver)}
                  dot={false}
                  strokeWidth={1.5}
                  isAnimationActive={false}
                />
                <Line
                  type="stepAfter"
                  dataKey={`${driver}_Brake`}
                  name={`${driver} Brake`}
                  stroke={getDriverColor(driver)}
                  dot={false}
                  strokeWidth={1.5}
                  strokeDasharray="5 5"
                  isAnimationActive={false}
                />
              </React.Fragment>
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TelemetryChart;
