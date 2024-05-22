import { useEffect, useRef, useCallback } from 'react';
import audioFile from '../assets/win95.mp3';

const StartupSound = () => {
    const audioRef = useRef(null);
    const playedKey = 'audioPlayed';

    const handleUserInteraction = useCallback(() => {
        audioRef.current.play();
        localStorage.setItem(playedKey, 'true');
        document.removeEventListener('click', handleUserInteraction);
    }, []);

    useEffect(() => {
        const audioPlayed = localStorage.getItem(playedKey);

        if (!audioPlayed) {
            document.addEventListener('click', handleUserInteraction);
        }

        return () => {
            document.removeEventListener('click', handleUserInteraction);
        };
    }, [handleUserInteraction]);

    return (
        <audio ref={audioRef} src={audioFile} autoPlay />
    );
};

export default StartupSound;