import styles from '../styles/Footer.module.css';
import Link from 'next/link';

function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.quickLinks}>
        <h4>Quick Links</h4>
        <Link href="/">Home</Link>
      </div>
      <div className={styles.socials}>
        <h4>Connect with Us</h4>
        <a href="https://twitter.com/" target="_blank" rel="noopener noreferrer">
          Twitter
        </a>
        <a href="https://linkedin.com/" target="_blank" rel="noopener noreferrer">
          LinkedIn
        </a>
      </div>
      
      <div className={styles.copy}>
        <p>&copy; {new Date().getFullYear()} DataPi. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
