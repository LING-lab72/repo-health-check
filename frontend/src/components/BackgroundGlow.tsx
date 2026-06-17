import { useEffect, useRef } from 'react';

/** Mouse-following radial gradient + floating ambient orbs */
export default function BackgroundGlow() {
  const mouseRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      if (!mouseRef.current) return;
      mouseRef.current.style.transform = `translate(${e.clientX - 300}px, ${e.clientY - 300}px)`;
    };
    window.addEventListener('mousemove', handleMove);
    return () => window.removeEventListener('mousemove', handleMove);
  }, []);

  return (
    <div className="bg-glow">
      <div className="bg-glow-orb bg-glow-orb--purple" />
      <div className="bg-glow-orb bg-glow-orb--cyan" />
      <div className="bg-glow-orb bg-glow-orb--indigo" />
      <div className="bg-glow-mouse" ref={mouseRef} />
    </div>
  );
}
