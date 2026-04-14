import { useState, useEffect, useRef } from 'react';

const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+';

export function useCipher(targetText, speed = 40, delay = 0) {
  const [displayText, setDisplayText] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);
  const iterationRef = useRef(0);

  useEffect(() => {
    if (!targetText) return;

    let timeoutId;
    let intervalId;

    const startAnimation = () => {
      setIsAnimating(true);
      iterationRef.current = 0;
      
      intervalId = setInterval(() => {
        setDisplayText((prev) => {
          return targetText
            .split('')
            .map((char, index) => {
              if (index < iterationRef.current) {
                return targetText[index];
              }
              return characters[Math.floor(Math.random() * characters.length)];
            })
            .join('');
        });

        if (iterationRef.current >= targetText.length) {
          clearInterval(intervalId);
          setIsAnimating(false);
        }

        iterationRef.current += 1 / 3;
      }, speed);
    };

    timeoutId = setTimeout(startAnimation, delay);

    return () => {
      clearTimeout(timeoutId);
      clearInterval(intervalId);
    };
  }, [targetText, speed, delay]);

  return { displayText, isAnimating };
}
