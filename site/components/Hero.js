import styles from '../styles/Hero.module.css';
import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useRef, useState } from 'react';

function Hero() {
    const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
    const phrases = [
        "Get informational data close to your application",
        "Embedded database for lightning speed OLAP",
        "dataPi implements a DataMesh ready architecture"
    ].map(phrase => (
        <>
            {phrase.split(' ').map((word, index) => {
                if (word === "dataPi") {
                    return <span key={index} className={styles.highlighted}>dataPi</span>;
                } else if (word === "lightning" && phrase.split(' ')[index + 1] === "speed") {
                    return <span key={index}><span className={styles.highlighted}>lightning speed</span> </span>;
                } else if (word === "DataMesh") {
                    return <span key={index} className={styles.highlighted}>DataMesh</span>;
                } else if (word === "speed" && phrase.split(' ')[index - 1] === "lightning") {
                    return null; // Skip this word as it's already included in "lightning speed"
                } else if (word === "informational") {
                    return <span key={index} className={styles.highlighted}>informational</span>;
                } else {
                    return word + " ";
                }
            })}
           
        </>
    ));

    const terminalContentRef = useRef(null);
    const terminalRef = useRef(null); // Reference to the terminal container
    const timeoutRef = useRef(null); // To keep track of the timeout

    useEffect(() => {
        const terminalContent = terminalContentRef.current;
        const terminalContainer = terminalRef.current;
        terminalContent.innerHTML = ''; // Clear any existing content

        const textToType = [
            { class: 'command', text: ' ' },
            { class: 'command', text: 'pip install datapi' },
            { class: 'output', text: 'Successfully installed datapi' },
            { class: 'command', text: 'datapi init' },
            { class: 'output', text: 'Initializing datapi project...' },
            { class: 'command', text: 'datapi run --all' },
            { class: 'output', text: 'Found 1 resources [aggregate-sales.yml]...' },
            { class: 'output', text: 'Running 1 resources...' },
            { class: 'output', text: '1 of 1 START create endpoint for aggregate-sales.yml[RUN]' },
            { class: 'output', text: 'Building data pod: gcr.io/velascoluis-dev-sandbox/aggregate-sales:latest' },
            { class: 'output', text: 'Deploying data pod: https://acme.data.com/aggregate-sales/' },
            { class: 'output', text: 'OK endpoint for data pod: https://acme.data.com/aggregate-sales/ [OK in 20.12s]' },
            { class: 'output', text: '1 of 1 DONE create endpoint for aggregate-sales.yml' }
            
        ];
        
        let lineIndex = 0;
        let charIndex = 0;
        let currentSpan = null;

        function typeCharacter() {
            if (lineIndex < textToType.length) {
                const line = textToType[lineIndex];
                
                if (charIndex === 0) {
                    currentSpan = document.createElement('span');
                    currentSpan.className = styles[line.class];
                    terminalContent.appendChild(currentSpan);
                }

                if (charIndex < line.text.length) {
                    const char = line.text[charIndex];
                    const textNode = document.createTextNode(char);
                    currentSpan.appendChild(textNode);
                    charIndex++;
                    timeoutRef.current = setTimeout(typeCharacter, 50);
                } else {
                    terminalContent.appendChild(document.createElement('br'));
                    lineIndex++;
                    charIndex = 0;
                    timeoutRef.current = setTimeout(typeCharacter, 200); // Pause between lines
                }

                // Auto-scroll to the bottom
                terminalContainer.scrollTop = terminalContainer.scrollHeight;
            }
        }

        typeCharacter();

        // Cleanup function to clear timeout if component unmounts
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, []); // Run only once when the component mounts

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentPhraseIndex((prevIndex) => (prevIndex + 1) % phrases.length);
        }, 4500); // Change phrase every 3 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <section className={styles.hero}>
            <div className={styles.content}>
                <h1 style={{ fontSize: '3.5rem', fontWeight: 'bold' }}>
                    {phrases[currentPhraseIndex]}
                </h1>
                <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
                    dataPi is a distributed <span  className={styles.highlighted}>datalakehouse head</span> for empowering application developers to unlock the full potential of their data.
                </p>
                <div className={styles.buttons}>
                    <Link href="https://github.com/velascoluis/datapi-core" className={styles.primaryButton}>
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <Image
                                src="/images/github.png"
                                alt="github"
                                width={20}
                                height={20}
                                style={{ marginRight: '8px' }}
                            />
                            <span>GitHub repository</span>
                        </div>
                    </Link>
                </div>
            </div>
            <div className={styles.image}> {/* Keep the image container */}
                <div className={styles.terminal} ref={terminalRef}> {/* Add a terminal-like container with ref */}
                    {/* Mac Window Controls */}
                    <div className={styles.windowControls}>
                        <span className={`${styles.circle} ${styles.red}`}></span>
                        <span className={`${styles.circle} ${styles.yellow}`}></span>
                        <span className={`${styles.circle} ${styles.green}`}></span>
                    </div>
                    <div className={styles.terminalContent} ref={terminalContentRef}></div>
                    <span className={styles.caret}>|</span> {/* Add the caret */}
                </div>
            </div>
        </section>
    );
}

export default Hero;