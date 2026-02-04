const NovartisLogo = ({ className = "h-12" }: { className?: string }) => {
  return (
    <svg 
      viewBox="0 0 400 100" 
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Orange/Red flame on left */}
      <path
        d="M 45 25 Q 35 35, 35 50 Q 35 65, 45 75 Q 50 70, 50 50 Q 50 30, 45 25 Z"
        fill="#E94E1B"
      />
      
      {/* Yellow flame in middle */}
      <path
        d="M 55 30 Q 50 40, 50 50 Q 50 60, 55 70 Q 60 65, 60 50 Q 60 35, 55 30 Z"
        fill="#F39200"
      />
      
      {/* Blue arc */}
      <path
        d="M 65 35 Q 70 40, 70 50 Q 70 60, 65 65"
        stroke="#00457C"
        strokeWidth="4"
        fill="none"
      />
      
      {/* NOVARTIS text */}
      <text
        x="120"
        y="65"
        fontFamily="Arial, sans-serif"
        fontSize="48"
        fontWeight="bold"
        fill="#00457C"
        letterSpacing="2"
      >
        NOVARTIS
      </text>
    </svg>
  );
};

export default NovartisLogo;