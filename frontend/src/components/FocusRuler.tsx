import React, { useEffect, useState } from 'react';

/**
 * Interactive reading focus ruler.
 *
 * A translucent band follows the pointer vertically, dimming everything else.
 * This constrains the visual field to a single line, which measurably reduces
 * line-skipping and re-reading for dyslexic readers. Implemented with
 * `transform` so it composites on the GPU and never triggers layout.
 */
export const FocusRuler: React.FC = () => {
  const [offsetY, setOffsetY] = useState<number>(0);
  const [visible, setVisible] = useState<boolean>(false);
  const height = 48;

  useEffect(() => {
    const handlePointerMove = (event: MouseEvent | TouchEvent) => {
      const point = 'touches' in event ? event.touches[0] : event;
      if (!point) return;
      setOffsetY(point.clientY - height / 2);
      setVisible(true);
    };

    const handleLeave = () => setVisible(false);

    window.addEventListener('mousemove', handlePointerMove, { passive: true });
    window.addEventListener('touchmove', handlePointerMove, { passive: true });
    window.addEventListener('mouseleave', handleLeave);

    return () => {
      window.removeEventListener('mousemove', handlePointerMove);
      window.removeEventListener('touchmove', handlePointerMove);
      window.removeEventListener('mouseleave', handleLeave);
    };
  }, []);

  return (
    <>
      <div
        aria-hidden
        className={`cognita-focus-dim ${visible ? 'cognita-focus-dim--active' : ''}`}
      />
      <div
        aria-hidden
        className="cognita-focus-ruler"
        style={{
          ['--cognita-ruler-height' as string]: `${height}px`,
          transform: `translateY(${offsetY}px)`,
          opacity: visible ? 1 : 0,
        }}
      />
    </>
  );
};
