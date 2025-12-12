export function NorthumbriaLogo() {
  return (
    <div className="relative h-10 w-10 flex items-center justify-center">
      <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-10 w-10">
        {/* Stylized N for Northumbria with modern academic feel */}
        <rect x="4" y="4" width="40" height="40" rx="8" className="fill-primary" />
        <path
          d="M14 32V16h3v11.5l8-11.5h3v16h-3V20.5L17 32h-3z"
          className="fill-primary-foreground"
          strokeWidth="0.5"
        />
        <circle cx="38" cy="38" r="4" className="fill-blue-400 animate-pulse" />
      </svg>
    </div>
  )
}
