type MatchGaugeProps = {
  percentage: number;
};

export default function MatchGauge({ percentage }: MatchGaugeProps) {
  const radius = 70;
  const strokeWidth = 12;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = Math.PI * normalizedRadius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  let strokeColor = "#10B981";
  let bgColor = "#D1FAE5";

  if (percentage < 40) {
    strokeColor = "#EF4444";
    bgColor = "#FEE2E2";
  } else if (percentage < 70) {
    strokeColor = "#F59E0B";
    bgColor = "#FEF3C7";
  }

  return (
    <div className="relative w-40 h-24 flex justify-center items-center">
      <svg
        height={radius}
        width={radius * 2}
      >
        <circle
          stroke={bgColor}
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          strokeDasharray={circumference + " " + circumference}
          strokeDashoffset={0}
          transform={`rotate(-180 ${radius} ${radius})`}
        />
        <circle
          stroke={strokeColor}
          fill="transparent"
          strokeWidth={strokeWidth}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          strokeDasharray={circumference + " " + circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-180 ${radius} ${radius})`}
        />
      </svg>

      <div className="absolute bottom-0 text-xl font-bold">{percentage}%</div>
    </div>
  );
}
