import React, { useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from "recharts";

import { getDriverColor } from '../utils/colors';

const getCompoundShape = (compound) => {
  switch (compound) {
    case "SOFT":
      return "circle";
    case "MEDIUM":
      return "square";
    case "HARD":
      return "triangle";
    case "INTERMEDIATE":
      return "diamond";
    case "WET":
      return "cross";
    default:
      return "circle";
  }
};

const CustomShape = (props) => {
  const { cx, cy, payload, fill } = props;
  if (!cx || !cy) return null;
  const shapeType = getCompoundShape(payload.Compound);
  
  if (shapeType === 'square') {
    return <rect x={cx - 4} y={cy - 4} width={8} height={8} fill={fill} />;
  } else if (shapeType === 'triangle') {
    return <polygon points={`${cx},${cy - 5} ${cx - 5},${cy + 4} ${cx + 5},${cy + 4}`} fill={fill} />;
  } else if (shapeType === 'diamond') {
    return <polygon points={`${cx},${cy - 5} ${cx - 5},${cy} ${cx},${cy + 5} ${cx + 5},${cy}`} fill={fill} />;
  } else if (shapeType === 'cross') {
    return (
      <g stroke={fill} strokeWidth={2}>
        <line x1={cx - 4} y1={cy - 4} x2={cx + 4} y2={cy + 4} />
        <line x1={cx + 4} y1={cy - 4} x2={cx - 4} y2={cy + 4} />
      </g>
    );
  }
  return <circle cx={cx} cy={cy} r={4} fill={fill} />;
};

const RacePaceChart = ({ paceData }) => {
  // paceData format: { VER: [ {LapNumber: 1, LapTime: 95.2, Compound: 'SOFT', TyreLife: 1}, ... ], LEC: [...] }

  const formattedData = useMemo(() => {
    const drivers = Object.keys(paceData);

    // We want to group by driver so each driver is a Scatter series
    return drivers.map((driver) => {
      const laps = paceData[driver].filter((lap) => lap.LapTime > 0); // basic sanity filter
      return {
        name: driver,
        data: laps,
        fill: getDriverColor(driver),
      };
    });
  }, [paceData]);

  if (!formattedData || formattedData.length === 0) {
    return (
      <div>
        No race pace data available. Make sure session is set to Race (R).
      </div>
    );
  }

  // Calculate Y-axis bounds (remove outliers > 120% of fastest lap for better scaling)
  const allLaps = formattedData.flatMap((d) => d.data.map((l) => l.LapTime));
  const fastestLap = Math.min(...allLaps);
  const cutoff = fastestLap * 1.15; // 115% of fastest lap

  const yDomain = [
    Math.floor(fastestLap) - 1,
    Math.ceil(Math.min(Math.max(...allLaps), cutoff)) + 1,
  ];

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(3);
    return `${mins}:${secs.padStart(6, "0")}`;
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          className="glass-panel"
          style={{ padding: "10px", fontSize: "0.85rem" }}
        >
          <p
            style={{
              fontWeight: "bold",
              color: getDriverColor(payload[0].name),
            }}
          >
            {payload[0].name}
          </p>
          <p>Lap: {data.LapNumber}</p>
          <p>Time: {formatTime(data.LapTime)}</p>
          <p>
            Tyre: {data.Compound} (L{data.TyreLife})
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ height: "400px", width: "100%" }}>
      <p
        style={{
          fontSize: "0.85rem",
          color: "var(--text-secondary)",
          marginBottom: "1rem",
        }}
      >
        Scatter plot of lap times vs lap number. Outlier laps (e.g., Pit stops,
        SC) beyond 115% of the fastest lap are hidden for scale. Different
        compounds are typically represented by shapes (Soft: Circle, Medium:
        Square, Hard: Triangle).
      </p>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            type="number"
            dataKey="LapNumber"
            name="Lap"
            stroke="rgba(255,255,255,0.5)"
            label={{
              value: "Lap Number",
              position: "bottom",
              offset: 5,
              fill: "rgba(255,255,255,0.5)",
            }}
          />
          <YAxis
            type="number"
            dataKey="LapTime"
            name="Lap Time"
            domain={yDomain}
            stroke="rgba(255,255,255,0.5)"
            tickFormatter={formatTime}
            label={{
              value: "Lap Time",
              angle: -90,
              position: "insideLeft",
              offset: -45,
              fill: "rgba(255,255,255,0.5)",
            }}
          />
          <ZAxis type="category" dataKey="Compound" name="Tyre" />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ strokeDasharray: "3 3" }}
          />
          <Legend wrapperStyle={{ bottom: -10 }} />

          {formattedData.map((series) => (
            <Scatter
              key={series.name}
              name={series.name}
              data={series.data.filter((d) => d.LapTime <= cutoff)}
              fill={series.fill}
              shape={<CustomShape />}
              line={{ stroke: series.fill, strokeWidth: 1 }}
              lineType="joint"
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RacePaceChart;
