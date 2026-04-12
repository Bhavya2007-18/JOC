import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useSystemMode } from '../../context/SystemModeContext';

export function DynamicBackground() {
  const { systemMode, visualIntensity, telemetry } = useSystemMode();
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [active, setActive] = useState(false);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
      setActive(true);
    };
    
    let idleTimer;
    const resetIdle = () => {
      setActive(true);
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => setActive(false), 5000);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mousemove', resetIdle);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mousemove', resetIdle);
    };
  }, []);

  return (
    <div className={`fixed inset-0 pointer-events-none overflow-hidden -z-10 bg-[#0a0a0c] mode-${systemMode}`}>
      {/* Layer 1: Multi-Depth Animated Mesh Blobs */}
      <div className="absolute inset-0">
        <BlobsGroup 
          mode={systemMode} 
          intensity={visualIntensity} 
          cpu={telemetry.cpu} 
          depth="back" // Background: Slow, Large, Very Blurred
        />
        <BlobsGroup 
          mode={systemMode} 
          intensity={visualIntensity} 
          cpu={telemetry.cpu} 
          depth="mid" // Midground: Faster, Smaller, Sharper
        />
      </div>

      {/* Layer 2: Dual-Layer Grain Overlay */}
      <GrainOverlay intensity={visualIntensity} />

      {/* Layer 3: Interactive Spotlight (with Inertia) */}
      <Spotlight x={mousePos.x} y={mousePos.y} active={active} mode={systemMode} intensity={visualIntensity} />

      {/* Layer 4: Thermal Bloom (Heat Leakage) */}
      <ThermalBloom cpu={telemetry.cpu} />
    </div>
  );
}

function BlobsGroup({ mode, depth, intensity, cpu }) {
  const configs = {
    chill: {
      colors: depth === 'back' ? ['#0f172a', '#1e1b4b'] : ['#1e3a8a', '#312e81'],
      blur: depth === 'back' ? '180px' : '120px',
      speed: depth === 'back' ? 0.2 : 0.4,
      scale: depth === 'back' ? 1.2 : 0.8,
      opacity: depth === 'back' ? 0.3 : 0.2
    },
    smart: {
      colors: depth === 'back' ? ['#1e1b4b', '#4c1d95'] : ['#0f172a', '#1e3a8a'],
      blur: depth === 'back' ? '160px' : '100px',
      speed: depth === 'back' ? 0.4 : 0.8,
      scale: depth === 'back' ? 1.1 : 0.7,
      opacity: depth === 'back' ? 0.4 : 0.3
    },
    beast: {
      colors: depth === 'back' ? ['#450a0a', '#7f1d1d'] : ['#4c1d95', '#991b1b'],
      blur: depth === 'back' ? '140px' : '80px',
      speed: depth === 'back' ? 0.8 : 1.5,
      scale: depth === 'back' ? 1.3 : 0.9,
      opacity: depth === 'back' ? 0.5 : 0.4
    }
  };

  const config = configs[mode];
  const speedMultiplier = 1 + (cpu / 100);

  return (
    <div className="absolute inset-0">
      {config.colors.map((color, i) => (
        <PhysicsBlob 
          key={`${mode}-${depth}-${i}`}
          color={color} 
          index={i + (depth === 'mid' ? 4 : 0)} 
          speed={config.speed * speedMultiplier}
          blur={config.blur}
          scale={config.scale}
          opacity={config.opacity}
        />
      ))}
    </div>
  );
}

function PhysicsBlob({ color, index, speed, blur, scale, opacity }) {
  const ref = useRef(null);
  const startTime = useRef(Date.now());
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  useEffect(() => {
    if (prefersReducedMotion) {
      if (ref.current) {
        ref.current.style.transform = `translate(-50%, -50%) translate(${50 + index * 5}vw, ${50}vh) scale(${scale})`;
      }
      return;
    }

    let frame;
    const animate = () => {
      if (!ref.current || document.hidden) {
        frame = requestAnimationFrame(animate);
        return;
      }
      
      const time = (Date.now() - startTime.current) / 1000;
      const angle = time * speed;
      
      // Complex sine/cosine based drift for organic motion
      const x = Math.sin(angle + index) * 25 + 50 + Math.cos(angle * 0.5) * 5;
      const y = Math.cos(angle * 0.7 + index) * 25 + 50 + Math.sin(angle * 0.3) * 5;
      
      ref.current.style.transform = `translate(-50%, -50%) translate(${x}vw, ${y}vh) scale(${scale})`;
      frame = requestAnimationFrame(animate);
    };
    
    animate();
    return () => cancelAnimationFrame(frame);
  }, [speed, index, scale, prefersReducedMotion]);

  return (
    <div 
      ref={ref}
      className="absolute top-0 left-0 w-[50vw] h-[50vw] rounded-full mix-blend-screen transition-colors duration-1000"
      style={{ 
        backgroundColor: color,
        filter: `blur(${blur})`,
        opacity: opacity,
        willChange: 'transform'
      }}
    />
  );
}

function GrainOverlay({ intensity }) {
  return (
    <>
      {/* Sub-Layer A: Fine Static Grain */}
      <div 
        className="absolute inset-0 opacity-[0.02] pointer-events-none mix-blend-overlay"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
      {/* Sub-Layer B: Animated Large Noise Particles */}
      <div 
        className="absolute inset-0 opacity-[0.015] pointer-events-none mix-blend-color-dodge animate-noise-drift"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 1024 1024' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='base'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.02' numOctaves='1'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23base)'/%3E%3C/svg%3E")`,
          backgroundSize: '200% 200%',
        }}
      />
    </>
  );
}

function Spotlight({ x, y, active, mode, intensity }) {
  const [smoothPos, setSmoothPos] = useState({ x, y });
  
  // Inertia Effect
  useEffect(() => {
    let frame;
    const animate = () => {
      setSmoothPos(prev => ({
        x: prev.x + (x - prev.x) * 0.08,
        y: prev.y + (y - prev.y) * 0.08
      }));
      frame = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(frame);
  }, [x, y]);

  const spotlightColors = {
    chill: 'rgba(59, 130, 246, 0.04)',
    smart: 'rgba(168, 85, 247, 0.07)',
    beast: 'rgba(239, 68, 68, 0.12)'
  };

  return (
    <div 
      className="absolute inset-0 pointer-events-none transition-opacity duration-1000"
      style={{
        opacity: active ? (0.5 + intensity * 0.5) : 0,
        background: `radial-gradient(500px circle at ${smoothPos.x}px ${smoothPos.y}px, ${spotlightColors[mode]}, transparent 100%)`
      }}
    />
  );
}

function ThermalBloom({ cpu }) {
  // Threshold-based bloom: starts intense at 80%+, purely subtle before
  const threshold = 70;
  const bloomIntensity = Math.max(0, (cpu - threshold) / (100 - threshold));
  
  return (
    <div 
      className="absolute inset-0 pointer-events-none transition-all duration-700"
      style={{
        opacity: bloomIntensity * 0.5,
        boxShadow: `inset 0 0 ${150 * bloomIntensity}px rgba(239, 68, 68, 0.4)`,
        border: `${bloomIntensity * 2}px solid rgba(239, 68, 68, 0.2)`,
        filter: `blur(${bloomIntensity * 10}px)`
      }}
    />
  );
}
