import Image from 'next/image';
import styles from '../styles/Home.module.css';
import Header from '../components/Header';
import Hero from '../components/Hero';
import Features from '../components/Features';
import Integrations from '../components/Integrations';

export default function Home() {
  return (
    <div className={styles.container}>
     
      <Hero />
      <section id="features">
        <Features />
      </section>
      <section id="integrations">
        <Integrations />
      </section>
      {/* Add more sections as needed */}
    </div>
  );
}